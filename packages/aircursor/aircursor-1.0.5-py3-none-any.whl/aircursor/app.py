from __future__ import annotations

from .server import create_app

app = create_app()

if __name__ == "__main__":
    import os

    host = os.getenv("AIRCURSOR_HOST", "0.0.0.0")
    port = int(os.getenv("AIRCURSOR_PORT", "5055"))
    debug = os.getenv("AIRCURSOR_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
