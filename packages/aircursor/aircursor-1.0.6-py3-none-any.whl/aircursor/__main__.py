from __future__ import annotations

import os
import qrcode
from .server import create_app


def _candidate_ips():
    """Get list of candidate IP addresses for the server."""
    import socket
    import ipaddress
    
    ips = set()
    # Primary outbound IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
    except Exception:
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass

    # Hostname-bound addresses
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET):
            ips.add(info[4][0])
    except Exception:
        pass

    # Env host
    host = os.getenv("AIRCURSOR_HOST")
    if host and host != "0.0.0.0":
        ips.add(host)

    # Always include localhost
    ips.add("127.0.0.1")

    def ok(ip):
        try:
            ipobj = ipaddress.ip_address(ip)
            if ipobj.is_loopback:
                return True
            if ipobj.is_private and not ipobj.is_link_local:
                return True
            return False
        except Exception:
            return False

    ordered = [ip for ip in ips if ok(ip)]
    # Prefer non-loopback first
    ordered.sort(key=lambda x: (x.startswith("127."), x))
    return ordered


def main() -> None:
    # ANSI color codes
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{CYAN}")
    print("     _    ___ ____   ____ _   _ ____  ____   ___  ____  ")
    print("    / \\  |_ _|  _ \\ / ___| | | |  _ \\/ ___| / _ \\|  _ \\ ")
    print("   / _ \\  | || |_) | |   | | | | |_) \\___ \\| | | | |_) |")
    print("  / ___ \\ | ||  _ <| |___| |_| |  _ < ___) | |_| |  _ < ")
    print(" /_/   \\_\\___|_| \\_\\\\____\\___/|_| \\_\\____/ \\___/|_| \\_\\")
    print(f"{RESET}")
    print(f"{YELLOW}         Remote Mouse Control Server{RESET}")
    print(f"{GREEN}         Created by: NiqueWrld{RESET}")
    print(f"{BLUE}         GitHub: https://github.com/NiqueWrld")
    print()
    
    host = os.getenv("AIRCURSOR_HOST", "0.0.0.0")
    port = int(os.getenv("AIRCURSOR_PORT", "5055"))
    debug = os.getenv("AIRCURSOR_DEBUG", "false").lower() == "true"
    
    print(f"{BOLD}{GREEN}🚀 Starting AirCursor Server...{RESET}")
    print(f"{YELLOW}📡 Port: {BOLD}{port}{RESET}")
    if debug:
        print(f"{YELLOW}🔧 Debug Mode: {BOLD}ON{RESET}")
    
    # Get and display all available IP addresses
    ips = _candidate_ips()
    print(f"{YELLOW}🌐 Available on:{RESET}")
    for ip in ips:
        print(f"   {BLUE}http://{BOLD}{ip}:{port}/{RESET}")

    print(f"\n{CYAN}─────────────────────────────────────────{RESET}")
    
    print(f"\n{GREEN}📱 Quick Usage:{RESET}")
    print(f"   • Open any URL above in your browser")
    print(f"   • Scan QR code with your phone")
    print(f"   • Use trackpad gestures to control mouse")
    print(f"   • API available at /api/v1/")
    print()
    
    # Generate and display QR code for the primary IP
    if ips:
        primary_url = f"http://{ips[0]}:{port}"
        qr = qrcode.QRCode(border=1, box_size=1)
        qr.add_data(primary_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    
    print(f"\n{CYAN}─────────────────────────────────────────{RESET}")
    print(f"{YELLOW}💡 Press Ctrl+C to stop the server{RESET}\n")
    
    app = create_app()
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    main()
