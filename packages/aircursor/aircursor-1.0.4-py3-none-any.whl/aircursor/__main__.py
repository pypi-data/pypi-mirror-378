from __future__ import annotations

import os
from .server import create_app


def main() -> None:
    app = create_app()
    host = os.getenv("AIRCURSOR_HOST", "0.0.0.0")
    port = int(os.getenv("AIRCURSOR_PORT", "5055"))
    debug = os.getenv("AIRCURSOR_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
