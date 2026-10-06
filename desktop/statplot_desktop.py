"""StatPlot – Desktop-Version.

Zeigt die Web-Oberflaeche (web/static) in einem eigenen Fenster, ganz ohne
Internet. Es gibt dadurch nur EINE Implementierung von Diagrammen, Kennwerten
und Tests (stats.js/statplot.js) – Web- und Desktop-Version koennen nicht
auseinanderlaufen.

    python3 desktop/statplot_desktop.py            # eigenes Fenster (pywebview)
    python3 desktop/statplot_desktop.py --browser  # im Standardbrowser oeffnen

Ist pywebview nicht installiert, wird automatisch der Browser benutzt.
"""

import base64
import functools
import http.server
import os
import socketserver
import sys
import threading
import webbrowser

APP_NAME = "StatPlot"


def static_dir():
    """Ordner mit index.html – im PyInstaller-Paket liegt er unter _MEIPASS."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, "static")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "web", "static")


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):   # kein Konsolenfenster vorhanden
        pass


def start_server():
    """Lokaler Server nur auf 127.0.0.1 mit freiem Port."""
    handler = functools.partial(_QuietHandler, directory=static_dir())
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/index.html?desktop=1"


def _dialog(webview, name, fallback):
    """FileDialog.OPEN/SAVE (pywebview ≥ 5) oder die alten Konstanten."""
    dialog = getattr(getattr(webview, "FileDialog", None), name, None)
    return dialog if dialog is not None else getattr(webview, fallback)


class Api:
    """Von statplot.js aufgerufen (window.pywebview.api): native Datei-Dialoge."""

    def __init__(self):
        self.window = None
        self.last_dir = os.path.expanduser("~")

    def open_file(self):
        """CSV-Datei waehlen → {name, path, text} oder None.

        Der volle Pfad landet im Python-Code-Export (DATEI = r"…").
        """
        import webview

        result = self.window.create_file_dialog(
            _dialog(webview, "OPEN", "OPEN_DIALOG"), directory=self.last_dir,
            file_types=("CSV-Dateien (*.csv;*.tsv;*.txt)", "Alle Dateien (*.*)"),
        )
        if not result:
            return None
        path = result if isinstance(result, str) else result[0]
        with open(path, "rb") as handle:
            raw = handle.read()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:          # Excel speichert CSV oft als Windows-1252
            text = raw.decode("cp1252", errors="replace")
        self.last_dir = os.path.dirname(path)
        return {"name": os.path.basename(path), "path": path, "text": text}

    def save_file(self, name, data_b64):
        import webview

        ext = os.path.splitext(name)[1].lstrip(".") or "*"
        result = self.window.create_file_dialog(
            _dialog(webview, "SAVE", "SAVE_DIALOG"), directory=self.last_dir, save_filename=name,
            file_types=(f"{ext.upper()}-Datei (*.{ext})", "Alle Dateien (*.*)"),
        )
        if not result:
            return None
        path = result if isinstance(result, str) else result[0]
        if not os.path.splitext(path)[1] and ext != "*":
            path += "." + ext
        with open(path, "wb") as handle:
            handle.write(base64.b64decode(data_b64))
        self.last_dir = os.path.dirname(path)
        return path


def main():
    httpd, url = start_server()
    use_browser = "--browser" in sys.argv
    webview = None
    if not use_browser:
        try:
            import webview  # pywebview
        except ImportError:
            print("pywebview ist nicht installiert – StatPlot oeffnet sich im Browser.")
    if webview is None:
        webbrowser.open(url)
        print(f"{APP_NAME} laeuft unter {url}\nBeenden mit Strg+C.")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        return
    api = Api()
    api.window = webview.create_window(
        APP_NAME, url, js_api=api, width=1360, height=880, min_size=(900, 600)
    )
    webview.start()
    httpd.shutdown()


if __name__ == "__main__":
    main()
