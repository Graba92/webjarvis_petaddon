#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8088
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Ruhiges Logging
        pass

def main():
    os.chdir(DIRECTORY)
    # Versuche Port zu belegen oder weiche aus
    global PORT
    for p in range(8088, 8100):
        try:
            httpd = socketserver.TCPServer(("", p), Handler)
            PORT = p
            break
        except OSError:
            continue
    else:
        print("❌ Kein freier Port gefunden.")
        sys.exit(1)

    url = f"http://localhost:{PORT}"
    print(f"🐾 Yuyus Tamagotchi Life Server läuft auf: {url}")
    print("Drücke Strg+C zum Beenden.")

    if "--no-browser" not in sys.argv:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")
        httpd.server_close()

if __name__ == "__main__":
    main()
