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
            sys.stdout.write(f"\rScanning... {char}")
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

    ip_input = input("Enter an IP address or range (e.g., 192.168.1.1 or 192.168.1.1/22): ")

    try:
        ip_network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError as e:
        print(f"Error: {e}")
        return

    loading_animation()

    http_only_ips = []
    for ip in ip_network.hosts():
        ip_str = str(ip)
        http_support = check_http_support(ip_str, 80)
        https_support = check_http_support(ip_str, 443)

        sys.stdout.write(f"\rScanning IP: {ip_str} ")
        sys.stdout.flush()

        if http_support and not https_support:
            print(f" - Possible HTTP address")
            http_only_ips.append(ip_str)

        time.sleep(0.1)  # Optional: Add a short delay to control the refresh rate

    print("\nScanning complete.\n\nPossible HTTP addresses:")
    for ip in http_only_ips:
        print(f"- {ip}")

    # Check if there are IP addresses with HTTP but not HTTPS
    if not http_only_ips:
        print("No IP addresses found with HTTP")
        return

    # Ask if the user wants to see more specific information for each address
    more_specific_info = input("\nMore specific info? (y/n): ").lower()

    if more_specific_info == 'y':
        print("\nChecking HTTP versions for found addresses:")
        for ip in http_only_ips:
            supported_versions = []
            for version in ['0.9', '1.0', '1.1', '2.0', '3.0']:  # You can customize the list of versions to check
                if check_http_version(ip, version):
                    supported_versions.append(version)
            if supported_versions:
                print(f"\033[92m- {ip} supports HTTP versions: {', '.join(supported_versions)}\033[0m")
            else:
                print(f"\033[91m- {ip} does not support any checked HTTP versions\033[0m")
    else:
        print("\n“To know your Enemy, you must become your Enemy.” ― Sun Tzu")

if __name__ == "__main__":
    main()
