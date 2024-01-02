import socket
import ipaddress
import sys
import time

def check_http_support(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)  # Set a timeout for the connection attempt
            s.connect((ip, port))
            return True
    except (socket.timeout, socket.error):
        return False

def check_http_version(ip, version):
    try:
        with socket.create_connection((ip, 80), timeout=2) as s:
            s.sendall(f"GET / HTTP/{version}\r\nHost: {ip}\r\n\r\n".encode())
            data = s.recv(1024).decode()
            return f"HTTP/{version}" in data
    except (socket.timeout, socket.error):
        return False

def loading_animation():
    animation = "|/-\\"
    for _ in range(10):
        for char in animation:
            sys.stdout.write(f"\r\033[93mScanning... {char}\033[0m")
            sys.stdout.flush()
            time.sleep(0.1)

def display_banner():
    banner = """
     \033[91m                                     
    ┓              
    ┣┓╋╋┏┓┏┓┏┓┏┏┓┏┓
    ┛┗┗┗┣┛┛ ┗ ┗┗┛┛┗
        ┛                  
    \033[0m
    """
    print(banner)
    time.sleep(1)  # Delay for dramatic effect

def main():
    display_banner()

    ip_input = input("\033[96mEnter an IP address or range (e.g., 192.168.1.1 or 192.168.1.1/22):\033[0m ")

    try:
        ip_network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
        return

    loading_animation()

    http_only_ips = []
    for ip in ip_network.hosts():
        ip_str = str(ip)
        http_support = check_http_support(ip_str, 80)
        https_support = check_http_support(ip_str, 443)

        sys.stdout.write(f"\r\033[93mScanning IP: {ip_str}\033[0m ")
        sys.stdout.flush()

        if http_support and not https_support:
            print(f" - \033[92mPossible HTTP address\033[0m")
            http_only_ips.append(ip_str)

        time.sleep(0.1)  # Optional: Add a short delay to control the refresh rate

    print("\nScanning complete.\n\n\033[96mPossible HTTP addresses:\033[0m")
    for ip in http_only_ips:
        print(f"- {ip}")

    # Check if there are IP addresses with HTTP but not HTTPS
    if not http_only_ips:
        print("\033[91mNo IP addresses found with HTTP\033[0m")
        return

    # Ask if the user wants to see more specific information for each address
    more_specific_info = input("\n\033[96mMore specific info? (y/n):\033[0m ").lower()

    if more_specific_info == 'y':
        print("\nChecking HTTP versions for found addresses:")
        for ip in http_only_ips:
            supported_versions = {'0.9': 0, '1.0': 0, '1.1': 0, '2.0': 0, '3.0': 0}
            total_checks = 0

            for version in supported_versions:
                if check_http_version(ip, version):
                    supported_versions[version] += 1
                    total_checks += 1

            print(f"\n\033[95mIP Address: {ip}\033[0m")
            if total_checks > 0:
                print("\033[92mConfidence Level:\033[0m")
                for version, count in supported_versions.items():
                    probability = (count / total_checks) * 100
                    print(f"- {version}: {probability:.2f}% confidence")
            else:
                print("\033[91mNo supported HTTP versions found\033[0m")
    else:
        print("\n\033[96m“To know your Enemy, you must become your Enemy.” ― Sun Tzu\033[0m")

if __name__ == "__main__":
    main()
