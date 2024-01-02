import socket
import ipaddress
import sys
import time
from datetime import timedelta

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

def calculate_probability(success_count, total_count):
    return (success_count / total_count) * 100 if total_count > 0 else 0

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

def format_time(seconds):
    td = timedelta(seconds=seconds)
    days, seconds = divmod(td.seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

def main():
    display_banner()

    ip_input = input("\033[96mEnter single IP address or CIDR Notation range (e.g., 192.168.1.1 or 192.168.1.1/22):\033[0m ")

    try:
        ip_network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
        return

    total_ips = ip_network.num_addresses  # Get the total number of IP addresses
    print(f"\n\033[96mScanning {total_ips} IP addresses...\033[0m")

    start_time = time.time()

    loading_animation()

    http_only_ips = []
    for i, ip in enumerate(ip_network.hosts(), start=1):
        sys.stdout.write(f"\r\033[93mScanning IP: {ip.compressed} | Progress: {i}/{total_ips} | Time Elapsed: {format_time(time.time() - start_time)} | Estimated Time Remaining: {format_time(((time.time() - start_time) / i) * (total_ips - i))}\033[0m ")
        sys.stdout.flush()

        ip_str = str(ip)
        http_support = check_http_support(ip_str, 80)
        https_support = check_http_support(ip_str, 443)

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
        for ip in http_only_ips:
            supported_versions = {'0.9': 0, '1.0': 0, '1.1': 0, '2.0': 0, '3.0': 0}
            total_checks = 0

            for version in supported_versions.keys():
                for _ in range(3):  # Perform multiple checks for better accuracy
                    if check_http_version(ip, version):
                        supported_versions[version] += 1
                        total_checks += 1

            print(f"\n\033[95mIP Address: {ip}\033[0m")
            print("\033[92mProbability of HTTP Versions:\033[0m")
            for version, count in supported_versions.items():
                probability = calculate_probability(count, total_checks)
                if probability > 0:
                    print(f"- HTTP/{version}: \033[93m{probability:.2f}%\033[0m")
    else:
        print("\n\033[96m“To know your Enemy, you must become your Enemy.” ― Sun Tzu\033[0m")

if __name__ == "__main__":
    main()
