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
                                           
    )    )   )                             
 ( /( ( /(( /(       (     (               
 )\()))\())\())`  )  )(   ))\ (  (   (     
((_)\(_))(_))/ /(/( (()\ /((_))\ )\  )\ )  
| |(_) |_| |_ ((_)_\ ((_|_)) ((_|(_)_(_/(  
| ' \|  _|  _|| '_ \) '_/ -_) _/ _ \ ' \)) 
|_||_|\__|\__|| .__/|_| \___\__\___/_||_|  
              |_|
              
    \033[0m
    """
    print(banner)
    time.sleep(1)  # Optional delay for a more dramatic effect

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
            print(f" - HTTP but not HTTPS")
            http_only_ips.append(ip_str)

        time.sleep(0.1)  # Optional: Add a short delay to control the refresh rate

    print("\nScanning complete.\n\nIP Addresses with HTTP but not HTTPS:")
    for ip in http_only_ips:
        print(f"- {ip}")

    # Check if there are IP addresses with HTTP but not HTTPS
    if not http_only_ips:
        print("No IP addresses found with HTTP but not HTTPS support.")
        return

    # Ask if the user wants to see more specific information for each address
    more_specific_info = input("\nDo you want to see more specific information for each address? (y/n): ").lower()

    if more_specific_info == 'y':
        print("\nHTTP Versions:")
        for ip in http_only_ips:
            for version in ['1.0', '1.1', '2.0']:  # You can customize the list of versions to check
                version_supported = check_http_version(ip, version)
                print(f"- {ip} supports HTTP {version}" if version_supported else f"- {ip} does not support HTTP {version}")
    else:
        print("\nNot showing more specific information.")

if __name__ == "__main__":
    main()
