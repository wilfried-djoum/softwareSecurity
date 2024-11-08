import socket

def port_scan_attack(target_ip):
    open_ports = []
    common_ports = [22, 80, 443, 21, 25, 110]  #List of all ports possible to scan
    
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout après 1 seconde
        result = sock.connect_ex((target_ip, port))
        
        if result == 0:
            open_ports.append(port)
        sock.close()

    if open_ports:
        return f"Ports ouverts sur {target_ip} : {', '.join(map(str, open_ports))}."
    else:
        return f"Aucun port ouvert détecté sur {target_ip}."