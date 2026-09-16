# 1. Asigură-te că WSL rulează (pornește o instanță silențioasă dacă era oprită)
wsl -d Ubuntu -e true

# 2. Obține automat noul IP din WSL
$wslIp = (wsl -d Ubuntu hostname -I).Trim().Split(" ")[0]

if (-not $wslIp) {
    Write-Host "[-] Eroare: Nu s-a putut obține IP-ul din WSL!" -ForegroundColor Red
    exit
}

Write-Host "[+] IP-ul curent din WSL detectat: $wslIp" -ForegroundColor Green

# 3. Șterge regulile vechi portproxy (fără erori dacă nu există)
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=52415 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=7447 2>$null

# 4. Adaugă noile reguli cu IP-ul actualizat
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=52415 connectaddress=$wslIp connectport=52415
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=7447 connectaddress=$wslIp connectport=7447

Write-Host "[+] Regulile netsh au fost actualizate cu succes pentru IP-ul $wslIp!" -ForegroundColor Cyan
Write-Host "[*] Gata de treabă. Poți porni exo în WSL." -ForegroundColor Yellow