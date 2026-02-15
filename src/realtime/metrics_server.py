from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def start_metrics_server(metrics_registry, port=8000):

    class MetricsHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            if self.path == "/metrics":
                metrics_data = metrics_registry.export_metrics()

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(metrics_data.encode())
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer(("0.0.0.0", port), MetricsHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"📊 Metrics server running at http://localhost:{port}/metrics")
