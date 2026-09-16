# Cluster Edge Infrastructure Daemons & WSL2 Networking Tools
> Technical Documentation and User Guide for Distributed Pure UTC Time Synchronization & WSL2 Port Forwarding.

## Author & Academic Affiliation

* **Author:** Prof. Lorentz Jäntschi
* **Institution:** Technical University of Cluj-Napoca, Department of Physics and Chemistry
* **Email:** [lorentz.jantschi@chem.utcluj.ro](mailto:lorentz.jantschi@chem.utcluj.ro)
* **Website:** [https://lori.academicdirect.org](https://lori.academicdirect.org)
* **Date:** September 2026
* **Version:** 1.0

---

## 1. General Overview

This suite of scripts provides administrative, time-synchronization, and network configuration tools for hybrid distributed computing clusters combining Windows, WSL2 Linux, the Exo Framework, and Apache Zenoh P2P middleware.

### Key Challenges Addressed
1. **High-Precision Time Synchronization:** Achieves pure UTC clock alignment via the native Windows `SetSystemTime` API, eliminating timezone skew and bypasses interference from the default Windows Time service (`w32time`).
2. **Centralized Drift Tracking:** Collects real-time temporal drift metrics across worker nodes on the Master node (`C-0`).
3. **Automated Port Forwarding:** Manages dynamic IP reassignment under Hyper-V NAT using `netsh interface portproxy` to route traffic into WSL2 (Ubuntu) instances transparently.

---

## 2. Repository Structure

| File | Type | Target Node | Primary Function |
| :--- | :--- | :--- | :--- |
| `master_daemon.py` | Python | Master (`C-0`) | HTTP reference clock server and centralized log collector. |
| `sync_daemon.py` | Python | Workers (`C-1`–`C-6`) | Unprivileged background agent for UTC drift correction. |
| `fix-wsl-ports.ps1` | PowerShell | Any Host | Detects dynamic WSL2 IP and updates `netsh portproxy` rules. |
| `start_master.ps1` | PowerShell | Master (`C-0`) | Bootstraps WSL Ubuntu, clears stale bindings, and maps ports `52415` & `7447`. |

---

## 3. System Requirements & Prerequisites

* **Operating System:** Windows 10 / Windows 11 Pro, Enterprise, or Education with WSL2 (Ubuntu) active.
* **Runtime:** Python 3.8+ installed on the Windows host.
* **Privileges:** Administrator rights (*Run as Administrator*) required for API calls and service manipulation.
* **Network Connectivity:** IP access between Worker nodes and Master node (Default Master IP: `10.147.1.97`).
* **Firewall Port Openings:**
  * `8080/TCP` — HTTP Synchronization Daemon (Master)
  * `52415/TCP` — P2P Communication / Exo Framework
  * `7447/TCP` — Apache Zenoh Protocol / Cluster messaging

---

## 4. Script Documentation

### 4.1. `master_daemon.py` (Master Server C-0)
Acts as the authoritative pure UTC reference clock and records worker status metrics.

* **Default Port:** `8080` (HTTP)
* **Log Directory:** `C:\SyncLogs`

bash
python master_daemon.py

### 4.2. `sync_daemon.py` (Worker Node Client)

Runs in the background on worker nodes, terminates `w32time`, and continuously aligns the host system clock with Master `C-0`.

* **Master Target:** `10.147.1.97:8080`
* **Default Polling Interval:** 10 minutes

powershell
# Standard execution (10-minute interval)
python sync_daemon.py

# Custom execution (e.g., 5-minute interval)
python sync_daemon.py 5


> **Security Note:** Requires Administrator privileges to invoke `SetSystemTime` (`kernel32.dll`) and control services. If launched without elevation, the script displays a warning and enters an idle loop to avoid repetitive exception logging.

### 4.3. `fix-wsl-ports.ps1` (WSL2 Portproxy Updater)

Forwards incoming host traffic on ports `52415` and `7447` directly to the dynamic IP assigned to the WSL2 guest container.

powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\fix-wsl-ports.ps1


### 4.4. `start_master.ps1` (Master Node Initializer)

Initializes the WSL Ubuntu instance, extracts its current IP address, purges legacy portproxy entries, and applies new bindings for ports `52415` and `7447`.

powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start_master.ps1

## 5. Automation & Task Scheduler Setup

### [A] Master Node Setup (`C-0`)

1. Create directory `C:\SyncLogs`.
2. Register `master_daemon.py` in Windows Task Scheduler:
* **Trigger:** *At system startup*
* **Action:** `python.exe C:\Path\To\master_daemon.py`
* **Options:** *Run with highest privileges*

### [B] Worker Node Setup (`C-1` to `C-6`)

1. Verify `MASTER_IP` inside `sync_daemon.py`.
2. Register in Windows Task Scheduler:
* **Trigger:** *At system startup*
* **Action:** `python.exe`
* **Arguments:** `C:\Path\To\sync_daemon.py 10`
* **Options:** *Run with highest privileges*

### [C] WSL2 Network Proxy Task Setup

1. Register `fix-wsl-ports.ps1` or `start_master.ps1`:
* **Trigger:** *At system startup* or *At user log on*
* **Action:** `powershell.exe`
* **Arguments:** `-ExecutionPolicy Bypass -File "C:\Path\To\fix-wsl-ports.ps1"`
* **Options:** *Run with highest privileges*


## 6. Troubleshooting

* **Elevation Error:** `"Script NOT running with administrator privileges"`
* *Fix:* Open PowerShell/CMD using *Run as Administrator*.


* **Synchronization Timeout:** Worker cannot reach `10.147.1.97:8080`.
* *Fix:* Verify IP route (`ping 10.147.1.97`) and add an inbound firewall rule on Master `C-0` for TCP port `8080`.


* **Zero Incoming Traffic in WSL2:**
* *Fix:* Re-run `fix-wsl-ports.ps1` as Administrator to update proxy tables after a WSL reboot. Inspect active rules via:
powershell
netsh interface portproxy show all

## 7. License

This project is released under the **MIT License**.
