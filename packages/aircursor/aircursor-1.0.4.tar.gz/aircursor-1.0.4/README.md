# AirCursor - Remote Mouse Control Server

```
     _    ___ ____   ____ _   _ ____  ____   ___  ____  
    / \  |_ _|  _ \ / ___| | | |  _ \/ ___| / _ \|  _ \ 
   / _ \  | || |_) | |   | | | | |_) \___ \| | | | |_) |
  / ___ \ | ||  _ <| |___| |_| |  _ < ___) | |_| |  _ < 
 /_/   \_\___|_| \_\____\___/|_| \_\____/ \___/|_| \_\
```

A lightweight, cross-platform HTTP server that transforms your computer into a remote-controllable mouse. Perfect for presentations, media centers, IoT projects, and accessibility solutions.

**Created by:** [NiqueWrld](https://github.com/NiqueWrld)

[![PyPI version](https://badge.fury.io/py/aircursor.svg)](https://badge.fury.io/py/aircursor)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

##  Quick Start

### Installation

```bash
pip install aircursor
```

### Running the Server

```bash
# Run directly
aircursor

# Or with Python module
python -m aircursor
```

##  Features

-  **Full Mouse Control**: Move cursor, click, scroll, and drag operations
-  **Web Interface**: Clean, responsive interface accessible from any device
-  **RESTful API**: Programmatic control for automation and integration
-  **QR Code Access**: Instant connection via generated QR codes
-  **Multi-Platform**: Works on Windows, macOS, and Linux
-  **Local Network**: Secure operation within your local network
-  **Lightweight**: Minimal resource usage and fast response times

##  API Reference

### Get Cursor Position
```http
GET /api/v1/cursor
```

### Set Cursor Position
```http
PUT /api/v1/cursor
Content-Type: application/json

{"x": 500, "y": 300}
```

### Move Cursor (Relative)
```http
PATCH /api/v1/cursor
Content-Type: application/json

{"dx": 10, "dy": -5}
```

### Mouse Click
```http
POST /api/v1/click
Content-Type: application/json

{
  "button": "left",
  "count": 1,
  "at": {"x": 100, "y": 200}
}
```

### Scroll
```http
POST /api/v1/scroll
Content-Type: application/json

{"dx": 0, "dy": -3}
```

##  Contributing

Contributions are welcome! Please visit the [GitHub repository](https://github.com/NiqueWrld/AirCursor) for more information.

##  License

This project is licensed under the MIT License.

---

** Give it a star on [GitHub](https://github.com/NiqueWrld/AirCursor)!**
