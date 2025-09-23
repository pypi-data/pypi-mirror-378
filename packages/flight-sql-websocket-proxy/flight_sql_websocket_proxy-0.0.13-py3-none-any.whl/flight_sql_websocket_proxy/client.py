from __future__ import annotations

import asyncio
import json
import os
import re
import signal
import ssl
import sys
import threading
from time import sleep
from typing import Any, Set

import click
import pandas as pd
from munch import munchify
from websockets.exceptions import ConnectionClosed
from websockets.frames import Close
from websockets.legacy.client import connect

from . import __version__ as arrow_flight_sql_websocket_proxy_client_version
from .constants import SERVER_PROTOCOL, SERVER_PORT, SERVER_BASE_PATH
from .utils import get_dataframe_from_ipc_base64_str

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.set_option('display.max_colwidth', None)
# pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 99)

if sys.platform == "win32":

    def win_enable_vt100() -> None:
        """
        Enable VT-100 for console output on Windows.

        See also https://bugs.python.org/issue29059.

        """
        import ctypes

        STD_OUTPUT_HANDLE = ctypes.c_uint(-11)
        INVALID_HANDLE_VALUE = ctypes.c_uint(-1)
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x004

        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        if handle == INVALID_HANDLE_VALUE:
            raise RuntimeError("unable to obtain stdout handle")

        cur_mode = ctypes.c_uint()
        if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(cur_mode)) == 0:
            raise RuntimeError("unable to query current console mode")

        # ctypes ints lack support for the required bit-OR operation.
        # Temporarily convert to Py int, do the OR and convert back.
        py_int_mode = int.from_bytes(cur_mode, sys.byteorder)
        new_mode = ctypes.c_uint(py_int_mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

        if ctypes.windll.kernel32.SetConsoleMode(handle, new_mode) == 0:
            raise RuntimeError("unable to set console mode")


def exit_from_event_loop_thread(
        loop: asyncio.AbstractEventLoop,
        stop: asyncio.Future[None],
) -> None:
    loop.stop()
    if not stop.done():
        # When exiting the thread that runs the event loop, raise
        # KeyboardInterrupt in the main thread to exit the program.
        if sys.platform == "win32":
            ctrl_c = signal.CTRL_C_EVENT
        else:
            ctrl_c = signal.SIGINT
        os.kill(os.getpid(), ctrl_c)


def print_during_input(string: str) -> None:
    sys.stdout.write(
        # Save cursor position
        "\N{ESC}"
        # Add a new line
        "\N{LINE FEED}"
        # Move cursor up
        "\N{ESC}[A"
        # Insert blank line, scroll last line down
        "\N{ESC}[L"
        # Print string in the inserted blank line
        f"{string}\N{LINE FEED}"
        # Restore cursor position
        "\N{ESC}"
        # Move cursor down
        "\N{ESC}[B"
    )
    sys.stdout.flush()


def print_over_input(string: str) -> None:
    sys.stdout.write(
        # Move cursor to beginning of line
        "\N{CARRIAGE RETURN}"
        # Delete current line
        "\N{ESC}[K"
        # Print string
        f"{string}\N{LINE FEED}"
    )
    sys.stdout.flush()


async def _run_client(
        server_protocol: str,
        server_hostname: str,
        server_port: int,
        server_base_path: str,
        tls_verify: bool,
        tls_roots: str,
        token: str,
        max_result_set_rows: int,
        autocommit: bool,
        loop: asyncio.AbstractEventLoop,
        inputs: asyncio.Queue[str],
        stop: asyncio.Future[None],
) -> None:
    print(
        f"Starting Arrow Flight SQL Websocket Proxy Client - by GizmoData™ - version: {arrow_flight_sql_websocket_proxy_client_version}")

    scheme = server_protocol.lower()

    ssl_context = None
    if scheme == "wss":
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_default_certs()

        if tls_verify:
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            if tls_roots:
                ssl_context.load_verify_locations(cafile=tls_roots)
        else:
            print("WARNING: TLS Verification is disabled.")
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

    server_uri = f"{scheme}://{server_hostname}:{server_port}{server_base_path.rstrip('/')}/client"
    print(f"Connecting to Server URI: {server_uri}")

    try:
        websocket = await connect(uri=server_uri,
                                  extra_headers=dict(),
                                  max_size=1024 ** 3,
                                  ssl=ssl_context
                                  )
    except Exception as exc:
        print_over_input(f"Failed to connect to {server_uri}: {exc}.")
        exit_from_event_loop_thread(loop, stop)
        return
    else:
        # Authenticate
        message_dict = dict(action="authenticate",
                            token=token,
                            autocommit=autocommit
                            )

        await websocket.send(json.dumps(message_dict))

        print_during_input(f"Successfully connected to {server_uri}.")

    try:
        while True:
            incoming: asyncio.Future[Any] = asyncio.create_task(websocket.recv())
            outgoing: asyncio.Future[Any] = asyncio.create_task(inputs.get())
            done: Set[asyncio.Future[Any]]
            pending: Set[asyncio.Future[Any]]
            done, pending = await asyncio.wait(
                [incoming, outgoing, stop], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks to avoid leaking them.
            if incoming in pending:
                incoming.cancel()
            if outgoing in pending:
                outgoing.cancel()

            if incoming in done:
                try:
                    raw_message = incoming.result()
                except ConnectionClosed:
                    break
                else:
                    if isinstance(raw_message, str):
                        message = munchify(x=json.loads(raw_message))

                        if message.kind == "message":
                            print_during_input("< " + message.message)
                        elif message.kind == "error":
                            print_during_input("< ERROR: " + message.error)
                        elif message.kind == "queryResult":
                            if message.success:
                                query_id = message.query_id
                                fetch_more_data = True
                                total_rows_fetched = 0
                                result_set_bytes = 0
                                remaining_rows_to_print = max_result_set_rows

                                while fetch_more_data:
                                    message_dict = dict(action="fetch",
                                                        query_id=query_id,
                                                        fetch_mode="batch"
                                                        )
                                    await websocket.send(json.dumps(message_dict))

                                    raw_message = await websocket.recv()
                                    message = munchify(x=json.loads(raw_message))

                                    if message.kind == "fetchResult":
                                        if message.success:
                                            if message.data:
                                                df = get_dataframe_from_ipc_base64_str(base64_str=message.data)
                                                total_rows_fetched += df.num_rows
                                                result_set_bytes += df.nbytes

                                                print_during_input(
                                                    f"Results (only displaying {remaining_rows_to_print:,} row(s)):\n{df.to_pandas().head(n=remaining_rows_to_print)}")

                                                remaining_rows_to_print -= df.num_rows
                                                if remaining_rows_to_print <= 0:
                                                    fetch_more_data = False
                                                    print_during_input(
                                                        f"\n-----------\nResult set size: {total_rows_fetched:,} row(s) / {result_set_bytes:,} bytes")
                                                    message_dict = dict(action="closeCursor",
                                                                        query_id=query_id
                                                                        )
                                                    await websocket.send(json.dumps(message_dict))
                                                    break

                                            if message.all_rows_fetched:
                                                print_during_input(
                                                    f"\n-----------\nResult set size: {total_rows_fetched:,} row(s) / {result_set_bytes:,} bytes")
                                                break
                                        else:
                                            print_during_input(f"Error: {message.error}")
                                            break
                                    else:
                                        raise ValueError(f"Unknown message kind: {message.kind}")

                            elif not message.success:
                                print_during_input(f"Error: {message.error}")
                        else:
                            raise ValueError(f"Unknown message kind: {message.kind}")

            if outgoing in done:
                message_dict = dict(action="query",
                                    sql=outgoing.result(),
                                    parameters=[]
                                    )

                await websocket.send(json.dumps(message_dict))

            if stop in done:
                break

    finally:
        await websocket.close()
        assert websocket.close_code is not None and websocket.close_reason is not None
        close_status = Close(websocket.close_code, websocket.close_reason)

        print_over_input(f"Connection closed: {close_status}.")

        exit_from_event_loop_thread(loop, stop)


def run_client(version: bool,
               server_protocol: str,
               server_hostname: str,
               server_port: int,
               server_base_path: str,
               tls_verify: bool,
               tls_roots: str,
               token: str,
               max_result_set_rows: int,
               autocommit: bool
               ):
    if version:
        print(f"Arrow Flight SQL Websocket Proxy Client - version: {arrow_flight_sql_websocket_proxy_client_version}")
        return

    # If we're on Windows, enable VT100 terminal support.
    if sys.platform == "win32":
        try:
            win_enable_vt100()
        except RuntimeError as exc:
            sys.stderr.write(
                f"Unable to set terminal to VT100 mode. This is only "
                f"supported since Win10 anniversary update. Expect "
                f"weird symbols on the terminal.\nError: {exc}\n"
            )
            sys.stderr.flush()

    try:
        import readline  # noqa
    except ImportError:  # Windows has no `readline` normally
        pass

    # Create an event loop that will run in a background thread.
    loop = asyncio.new_event_loop()

    # Due to zealous removal of the loop parameter in the Queue constructor,
    # we need a factory coroutine to run in the freshly created event loop.
    async def queue_factory() -> asyncio.Queue[str]:
        return asyncio.Queue()

    # Create a queue of user inputs. There's no need to limit its size.
    inputs: asyncio.Queue[str] = loop.run_until_complete(queue_factory())

    # Create a stop condition when receiving SIGINT or SIGTERM.
    stop: asyncio.Future[None] = loop.create_future()

    # Schedule the task that will manage the connection.
    loop.create_task(_run_client(server_protocol=server_protocol,
                                 server_hostname=server_hostname,
                                 server_port=server_port,
                                 server_base_path=server_base_path,
                                 tls_verify=tls_verify,
                                 tls_roots=tls_roots,
                                 token=token,
                                 max_result_set_rows=max_result_set_rows,
                                 autocommit=autocommit,
                                 loop=loop,
                                 inputs=inputs,
                                 stop=stop,
                                 )
                     )

    # Start the event loop in a background thread.
    thread = threading.Thread(target=loop.run_forever)
    thread.start()

    # Read from stdin in the main thread in order to receive signals.
    try:
        while True:
            lines = []
            prompt_str = "> "
            while True:
                line = input(prompt_str)
                if line:
                    prompt_str = ". "
                    lines.append(line)

                # Search for a SQL terminator
                if re.search(r"(;|^/)\s*$", line):
                    break
            message = '\n'.join(lines)
            loop.call_soon_threadsafe(inputs.put_nowait, message)
    except (KeyboardInterrupt, EOFError):  # ^C, ^D
        # Sleep for a second in case the EOF was called in a bash script
        sleep(1)

        loop.call_soon_threadsafe(stop.set_result, None)

    # Wait for the event loop to terminate.
    thread.join()

    # For reasons unclear, even though the loop is closed in the thread,
    # it still thinks it's running here.
    loop.close()


@click.command()
@click.option(
    "--version/--no-version",
    type=bool,
    default=False,
    show_default=False,
    required=True,
    help="Prints the Arrow Flight SQL Websocket Proxy Client version and exits."
)
@click.option(
    "--server-protocol",
    type=click.Choice(["wss", "ws"]),
    default=os.getenv("SERVER_PROTOCOL", SERVER_PROTOCOL),
    show_default=False,
    required=True,
    help=f"The protocol of the Arrow Flight SQL Websocket Proxy server.  Defaults to environment variable SERVER_PROTOCOL if set, or {SERVER_PROTOCOL} if not set."
)
@click.option(
    "--server-hostname",
    type=str,
    default=os.getenv("SERVER_HOSTNAME", "localhost"),
    show_default=False,
    required=True,
    help="The hostname of the Arrow Flight SQL Websocket Proxy server.  Defaults to environment variable SERVER_HOSTNAME if set, or localhost if not set."
)
@click.option(
    "--server-port",
    type=int,
    default=os.getenv("SERVER_PORT", SERVER_PORT),
    show_default=False,
    required=True,
    help=f"The port of the Arrow Flight SQL Websocket Proxy server.  Defaults to environment variable SERVER_PORT if set, or {SERVER_PORT} if not set."
)
@click.option(
    "--server-base-path",
    type=str,
    default=os.getenv("SERVER_BASE_PATH", SERVER_BASE_PATH),
    show_default=False,
    required=True,
    help=f"The base path of the Arrow Flight SQL Websocket Proxy server.  Defaults to environment variable SERVER_BASE_PATH if set, or {SERVER_BASE_PATH} if not set."
)
@click.option(
    "--tls-verify/--no-tls-verify",
    type=bool,
    default=(os.getenv("TLS_VERIFY", "TRUE").upper() == "TRUE"),
    show_default=True,
    help="Verify the server's TLS certificate hostname and signature.  Using --no-tls-verify is insecure, only use for development purposes!"
)
@click.option(
    "--tls-roots",
    type=str,
    default=os.getenv("TLS_ROOTS"),
    show_default=True,
    help="'Path to trusted TLS certificate(s).  Defaults to environment variable TLS_ROOTS if set.  If not set, the system default trusted certificates will be used."
)
@click.option(
    "--token",
    type=str,
    default=os.getenv("TOKEN"),
    show_default=False,
    required=True,
    help="The client clerk JWT token to authenticate with.  Defaults to environment variable TOKEN if set."
)
@click.option(
    "--max-result-set-rows",
    type=int,
    default=100,
    show_default=True,
    required=True,
    help="The maximum number of rows to show in result sets.  A value of 0 means no limit."
)
@click.option(
    "--autocommit/--no-autocommit",
    type=bool,
    default=(os.getenv("AUTOCOMMIT", "TRUE").upper() == "TRUE"),
    show_default=True,
    help="Enable autocommit mode."
)
def click_run_client(version: bool,
                     server_protocol: str,
                     server_hostname: str,
                     server_port: int,
                     server_base_path: str,
                     tls_verify: bool,
                     tls_roots: str,
                     token: str,
                     max_result_set_rows: int,
                     autocommit: bool
                     ) -> None:
    run_client(**locals())


if __name__ == "__main__":
    click_run_client()
