import ctypes
from datetime import datetime, timezone
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

MASTER_IP = "10.147.1.97"
PORT = 8080
HOSTNAME = socket.gethostname()


class SYSTEMTIME(ctypes.Structure):
  _fields_ = [
      ("wYear", ctypes.c_ushort),
      ("wMonth", ctypes.c_ushort),
      ("wDayOfWeek", ctypes.c_ushort),
      ("wDay", ctypes.c_ushort),
      ("wHour", ctypes.c_ushort),
      ("wMinute", ctypes.c_ushort),
      ("wSecond", ctypes.c_ushort),
      ("wMilliseconds", ctypes.c_ushort),
  ]


def set_utc_system_time(dt_utc):
  """Setează ora folosind SetSystemTime (UTC pur), imun la setările greșite

  de fus orar ale utilizatorului.
  """
  st = SYSTEMTIME()
  st.wYear = dt_utc.year
  st.wMonth = dt_utc.month
  st.wDayOfWeek = (dt_utc.weekday() + 1) % 7
  st.wDay = dt_utc.day
  st.wHour = dt_utc.hour
  st.wMinute = dt_utc.minute
  st.wSecond = dt_utc.second
  st.wMilliseconds = int(dt_utc.microsecond / 1000)
  return ctypes.windll.kernel32.SetSystemTime(ctypes.byref(st))


def is_admin():
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False


def main():
  # Dacă nu are privilegii de administrator, afișează mesajul și rămâne în așteptare infinită
  if not is_admin():
    print("=" * 65)
    print(" [!] ATENȚIE: Scriptul NU rulează cu drepturi de administrator!")
    print("     Modificarea orei sistemului este blocată de Windows.")
    print("     Daemonul intră în așteptare. Apasă Ctrl+C sau închide fereastra.")
    print("=" * 65)
    while True:
      time.sleep(3600)  # Doar stă și așteaptă să fie oprit, fără a face nimic

  interval_minutes = 10
  if len(sys.argv) > 1:
    try:
      interval_minutes = float(sys.argv[1])
    except ValueError:
      pass

  interval_seconds = int(interval_minutes * 60)

  # Suprimăm complet interferențele serviciului Windows Time nativ
  subprocess.run(
      "sc config w32time start= disabled",
      shell=True,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
  )
  subprocess.run(
      "net stop w32time",
      shell=True,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
  )

  print("=" * 65)
  print(
      f" DAEMON STAȚIE BLINDAT (UTC PUR) | Interval: {interval_minutes} minute"
  )
  print("=" * 65)

  while True:
    try:
      # Trimitem ora curentă UTC a stației către master
      local_now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
      local_time_str = local_now_utc.strftime("%Y-%m-%d %H:%M:%S.%f")

      url = f"http://{MASTER_IP}:{PORT}/?host={urllib.parse.quote(HOSTNAME)}&time={urllib.parse.quote(local_time_str)}"
      req = urllib.request.urlopen(url, timeout=3)
      server_time_str = req.read().decode("utf-8").strip()

      # Parsăm ora exactă primită de la master (tot în UTC)
      server_time_utc = datetime.strptime(server_time_str, "%Y-%m-%d %H:%M:%S.%f")

      drift = (local_now_utc - server_time_utc).total_seconds()

      # Aplicăm ora corectă în sistem la nivel hardware/UTC
      success = set_utc_system_time(server_time_utc)
      current_str = datetime.now().strftime("%H:%M:%S")

      if success:
        print(
            f"[{current_str}] Sincronizat cu C-0 (UTC) | Ora setată:"
            f" {server_time_str[:19]} | Decalaj corectat: {drift:+.3f} sec"
        )
      else:
        print(f"[{current_str}] [-] Eroare API Windows la setarea orei UTC.")
    except Exception as e:
      print(
          f"[{datetime.now().strftime('%H:%M:%S')}] [-] Eroare de"
          f" rețea/sincronizare: {e}"
      )

    time.sleep(interval_seconds)


if __name__ == "__main__":
  main()