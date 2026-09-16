$wslIp = (wsl hostname -I).Trim().Split(" ")[0]
if (-not $wslIp) {
    Write-Error "Nu s-a putut detecta IP-ul WSL."
    exit
}
Write-Host "IP-ul curent WSL detectat: $wslIp"
netsh interface portproxy reset | Out-Null
# Adaugă regulile noi pentru porturile 7447 și 52415
netsh interface portproxy add v4tov4 listenport=7447 listenaddress=0.0.0.0 connectport=7447 connectaddress=$wslIp
netsh interface portproxy add v4tov4 listenport=52415 listenaddress=0.0.0.0 connectport=52415 connectaddress=$wslIp
Write-Host "Portproxy actualizat cu succes pentru IP-ul $wslIp!"