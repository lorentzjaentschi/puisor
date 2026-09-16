from datetime import datetime, timezone
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080
LOG_DIR = r"C:\SyncLogs"

if not os.path.exists(LOG_DIR):
  os.makedirs(LOG_DIR)


class MasterSyncHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    # Generăm ora UTC pură, fără nicio ambiguitate de fus orar
    server_time = datetime.now(timezone.utc).replace(tzinfo=None)
    server_time_str = server_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    update_moment_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parsed_path = urllib.parse.urlparse(self.path)
    query = urllib.parse.parse_qs(parsed_path.query)

    if "host" in query and "time" in query:
      hostname = query["host"][0]
      client_time_str = query["time"][0]

      try:
        client_time = datetime.strptime(
            client_time_str, "%Y-%m-%d %H:%M:%S.%f"
        )
        drift = (client_time - server_time).total_seconds()
      except Exception:
        drift = 0.0

      # Log sigilat
      filename = os.path.join(LOG_DIR, f"{hostname}_status.txt")
      with open(filename, "w") as f:
        f.write(f"Hostname: {hostname}\n")
        f.write(f"ClientTime: {client_time_str}\n")
        f.write(f"ServerTime: {server_time_str}\n")
        f.write(f"DriftSeconds: {drift:+.3f}\n")
        f.write(f"UpdateMoment: {update_moment_str}\n")
        f.write(f"Status: OK\n")

      self.send_response(200)
      self.send_header("Content-type", "text/plain")
      self.end_headers()
      self.wfile.write(server_time_str.encode("utf-8"))

      print(
          f"[{update_moment_str}] Stație: {hostname:<12} | Decalaj:"
          f" {drift:+.3f} sec"
      )
    else:
      self.send_response(400)
      self.end_headers()
      self.wfile.write(b"BAD REQUEST")

  def log_message(self, format, *args):
    pass


def run():
  server_address = ("", PORT)
  httpd = HTTPServer(server_address, MasterSyncHandler)
  print("=" * 65)
  print(" MASTER C-0 | SERVER COLECTOR & SINCRONIZARE BLINDAT (UTC) ")
  print("=" * 65)
  httpd.serve_forever()


if __name__ == "__main__":
  run()