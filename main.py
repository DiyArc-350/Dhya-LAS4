import requests 
import time 
import socket
import concurrent.futures
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os



def title():
  os.system("cls")
  art = """
  ▓█████▄  ██░ ██ ▓██   ██▓ ▄▄▄           
  ▒██▀ ██▌▓██░ ██▒ ▒██  ██▒▒████▄         
  ░██   █▌▒██▀▀██░  ▒██ ██░▒██  ▀█▄       
  ░▓█▄   ▌░▓█ ░██   ░ ▐██▓░░██▄▄▄▄██      
  ░▒████▓ ░▓█▒░██▓  ░ ██▒▓░ ▓█   ▓██▒ ██▓ 
  ▒▒▓  ▒  ▒ ░░▒░▒   ██▒▒▒  ▒▒   ▓▒█░ ▒▓▒ 
  ░ ▒  ▒  ▒ ░▒░ ░ ▓██ ░▒░   ▒   ▒▒ ░ ░▒  
  ░ ░  ░  ░  ░░ ░ ▒ ▒ ░░    ░   ▒    ░   
    ░     ░  ░  ░ ░ ░           ░  ░  ░  
  ░               ░ ░                 ░  
  """
  print(art)

def input_url():
    while 1:
        try:
            url = input('\nEnter URL: ').strip()  # Remove leading/trailing whitespace
            if not url:
                print('\033[31mError:\033[0m URL cannot be empty.')
                continue
            if not url.startswith(('http://', 'https://')):
                print('\033[31mError:\033[0m URL must start with http:// or https://')
                continue
            if url.endswith('/'):
                url = url[:-1]  # Remove trailing slash
            return url
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print('\033[31mAn error occurred:\033[0m', e)

def load_cms_metadata(json_file):
    with open(json_file, "r") as file:
        return json.load(file)
def server_info(res):
    try:
        response = res
        ip_address = get_ip(url)
        if response.status_code == 200:
            # Load Time Calculation.
            server_headers = response.headers
            server = server_headers.get('Server', 'N/A')
            os = server_headers.get('X-Powered-By', 'N/A')

            print(f"\033[31mIP Address:\033[0m {ip_address}")
            print(f"\033[31mServer Software:\033[0m {server}")
            print(f"\033[31mServer OS:\033[0m {os}")
        else:
            print('Failed to fetch URL:', response.status_code)
            time.sleep(1)
            exit(1)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

def get_ip(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except Exception as e:
        print("Error:", e)
        return "N/A"
    
def refactor_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    if url == base_url:
        return url
    print(f"Specefied URL: {url}\n")
    print(f"1. Stripped URL: {base_url}")
    print("2. Enter new URL")
    print(f"3. Continue with: {url}")
    user = input("\nEnter your selection: ")
    if user == '1':
        url = base_url
    if user == '2':
        url = input_url()
    return url

    
def check_subdomain(scheme, base_url, subdomain):
    full_url = f"{scheme}://{subdomain}.{base_url}"
    try:
        response = requests.get(full_url, timeout=5)
        if response.status_code == 200:
            return full_url, response.status_code
    except requests.RequestException:
        return None

def search_subdomains(url, wordlist_path):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    base_url = parsed_url.netloc

    with open(wordlist_path, 'r') as f:
        subdomains = f.read().splitlines()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_subdomain = {executor.submit(check_subdomain, scheme, base_url, subdomain): subdomain for subdomain in subdomains}
            for future in concurrent.futures.as_completed(future_to_subdomain):
                result = future.result()
                if result:
                    ip_addr=get_ip(result[0])
                    print(f"[+] {result[0]} (Status: {result[1]}) [{ip_addr}]")
    except KeyboardInterrupt:
        exit(0)

def scan_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))
    sock.close()
    if result == 0:
        return port

def get_open_ports(ip_address):

    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {executor.submit(scan_port, ip_address, port): port for port in range(1, 1024)}
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            if future.result() is not None:
                open_ports.append(port)

    return open_ports

def list_menu():
    print("\n1.Server Info")
    print("2.Scan Subdomains")
    print("3.Scan Open Ports")
    print("0.Exit")
   
if __name__ == "__main__":
    title()
    url = input_url()
    start_time = time.time()
    res= requests.get(url)
    print("\nFetching URL...")
    end_time =  time.time()  if res.status_code == 200 else 0.0
    load_time = end_time - start_time
    print(f"\n\033[31mLoad Time:\033[0m {load_time:.1f} seconds")
    
     # Reducing load by importing files in the main stack.
    cms_metadata = load_cms_metadata("src/cms_metadata.json")

    #Init value if CMS Detection skipped.
    cms_name = "Unknown CMS"

    while True:
        list_menu()
        in_usr = input("Enter your choice: ")
        #switch case task
        if in_usr == '1':
            title()
            server_info(res)
        elif in_usr == '2':
            title()
            print("\n[+] Scanning Subdomains...\n")
            wordlist_path = "src/sub.txt"
            search_subdomains(url, wordlist_path)
        elif in_usr == '3':
            title()
            print("\n[+] Scanning Ports...\n")
            print(get_open_ports(get_ip(url)))
        elif in_usr == '0':
            os.system("cls")
            exit(0)
        else:
            os.system("cls")
            print("\033[31mInvalid option. Please try again.\033[0m")

    


