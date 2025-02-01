import argparse
import asyncio
import logging

import httpx
import uvicorn
from click import style

from .utils import get_ip


async def wait_for_server(host, port):
    url = f"http://{host}:{port}/health"
    while True:
        try:
            logging.getLogger("httpx").setLevel(logging.WARNING)
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    break
        except Exception:
            pass
        await asyncio.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description="Run the jeopardy server.")
    parser.add_argument("--host", type=str, default=get_ip())
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    host, port = args.host, args.port
    from .server import app

    config = uvicorn.Config(app, host=host, port=port, log_level=logging.WARNING)
    server = uvicorn.Server(config)

    async def run_server():
        server_task = asyncio.create_task(server.serve())  # Start Uvicorn
        await wait_for_server(host, port)  # Ensure server is up
        print(style("Server running!", fg="blue", bold=True))
        print(
            style("Connect to", fg="cyan"),
            style(f"http://{host}:{port}", fg="cyan", bold=True, underline=True),
            style("to play.", fg="cyan"),
        )
        try:
            await server_task  # Keep Uvicorn running
        except asyncio.exceptions.CancelledError:
            print()
            print(style("Shutting down...", fg="yellow"))

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
