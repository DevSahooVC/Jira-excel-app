from __future__ import annotations

import socket
import tempfile
import time
import webbrowser
from pathlib import Path

import uvicorn

from app.main import app


def _pick_port(host: str, start: int = 8000, attempts: int = 20) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No free port found in range {start}-{start + attempts - 1}")


def main() -> None:
    host = "127.0.0.1"
    port = _pick_port(host, start=8000, attempts=20)

    # Persist the chosen port so other tooling (and humans) can discover it.
    port_file = Path(tempfile.gettempdir()) / "jira-excel-reporter-port.txt"
    port_file.write_text(str(port), encoding="utf-8")

    url = f"http://{host}:{port}/"
    # Give the server a moment to start before opening the browser.
    def _open_browser() -> None:
        time.sleep(0.8)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    _open_browser()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()

