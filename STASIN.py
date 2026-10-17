import urllib.request
import urllib.error
import socket
import re
import json
import os
import time
import sys
import hashlib
import base64
import uuid
import random
import platform
import uuid as py_uuid
from datetime import datetime, timedelta

# ANSI Farben für den Cyber-Look
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

KEYS_FILE = "stasint_keys.json"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_hardware_fingerprint():
    try:
        node_name = platform.node()
        system_name = platform.system()
        machine_type = platform.machine()
        processor = platform.processor()
        mac = ":".join(re.findall("..", "%012x" % py_uuid.getnode()))
        raw_hw = f"{node_name}-{system_name}-{machine_type}-{processor}-{mac}"
        return hashlib.sha256(raw_hw.encode()).hexdigest()
    except:
        return hashlib.sha256(platform.uname()._asdict().__str__().encode()).hexdigest()

def loading_animation(text="Initialisiere Core"):
    clear_screen()
    frames = ["|", "/", "-", "\\"]
    for _ in range(2):
        for frame in frames:
            sys.stdout.write(f"\r{YELLOW}[~] {text} {frame}{RESET}")
            sys.stdout.flush()
            time.sleep(0.06)
    print(f"\r{GREEN}[✔] {text} abgeschlossen.{RESET}")
    time.sleep(0.3)
    clear_screen()

def banner(is_admin=False, expires_at=None):
    if is_admin:
        role_text = f"{RED}[ADMINISTRATOR: SWATTINGLARPS]{RESET}"
    else:
        exp_str = expires_at if expires_at else "Unbekannt"
        role_text = f"{CYAN}[LICENSED USER | Gültig bis: {exp_str}]{RESET}"
        
    print(CYAN + BOLD + """
    ███████╗████████╗ █████╗ ███████╗██╗███╗   ██╗
    ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║████╗  ██║
    ███████╗   ██║   ███████║███████║██║██╔██╗ ██║
    ╚════██║   ██║   ██╔══██║╚════██║██║██║╚██╗██║
    ███████║   ██║   ██║  ██║███████║██║██║ ╚████║
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝
    ==================================================
     MADE BY SWATTINGLARPS / 4PJ UND 808NOKIA | v6.7
    ==================================================
    """ + RESET + f" Status: {role_text}\n")

# --- Key Management ---
def load_keys():
    if not os.path.exists(KEYS_FILE):
        initial_keys = [
            {"key": "123456789012345678", "role": "user", "used": False, "bound_hwid": None, "expires_at": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}
        ]
        save_keys(initial_keys)
        return initial_keys
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def generate_discord_id_key(duration_type):
    prefix = random.choice(["11", "12", "98", "87", "76"])
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(16)])
    key_str = prefix + random_digits
    
    now = datetime.now()
    if duration_type == "1day":
        expires = now + timedelta(days=1)
        label = "1 Tag"
    elif duration_type == "7days":
        expires = now + timedelta(days=7)
        label = "7 Tage"
    elif duration_type == "lifetime":
        expires = now + timedelta(days=36500)
        label = "Lifetime"
    else:
        expires = now + timedelta(days=30)
        label = "30 Tage"
        
    return key_str, expires.strftime("%Y-%m-%d %H:%M:%S"), label

# --- Auth System ---
def auth_menu():
    keys = load_keys()
    current_hwid = get_hardware_fingerprint()
    
    while True:
        clear_screen()
        banner(is_admin=False)
        print(YELLOW + "  [1] Admin-Login (SWATTINGLARPS)" + RESET)
        print(YELLOW + "  [2] Lizenz-ID (Discord-Format) eingeben" + RESET)
        print(YELLOW + "  [0] Beenden" + RESET)
        
        choice = input(f"\n{YELLOW}[?] STASINT-Auth > {RESET}").strip()
        
        if choice == "1":
            print(CYAN + "\n--- ADMIN LOGIN ---" + RESET)
            user_input = input(f"{YELLOW}[?] Username: {RESET}").strip()
            pass_input = input(f"{YELLOW}[?] Passwort: {RESET}").strip()
            
            if user_input == "SWATTINGLARPS" and pass_input == "STASINTADM1N":
                loading_animation("Authentifiziere Administrator")
                print(GREEN + "[✔] Admin-Zugriff gewährt!" + RESET)
                time.sleep(0.8)
                return "ADMIN_SESSION", True, "Unbegrenzt"
            else:
                print(RED + "[-] Falsche Zugangsdaten!" + RESET)
                time.sleep(1.5)
                
        elif choice == "2":
            print(CYAN + "\n--- LIZENZ-ID LOGIN ---" + RESET)
            entered_key = input(f"{YELLOW}[?] Lizenz-ID eingeben: {RESET}").strip()
            
            key_entry = next((k for k in keys if k["key"] == entered_key), None)
            
            if not key_entry:
                print(RED + "[-] Ungültige Lizenz-ID!" + RESET)
                time.sleep(1.5)
                continue
                
            # Anti-Abuse Hardware Check
            if key_entry["bound_hwid"] and key_entry["bound_hwid"] != current_hwid:
                print(RED + "[-] Fehler: Dieser Key ist bereits an ein anderes Gerät gebunden!" + RESET)
                time.sleep(2.5)
                continue
                
            expires_at = datetime.strptime(key_entry["expires_at"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expires_at:
                print(RED + "[-] Diese Lizenz ist abgelaufen!" + RESET)
                time.sleep(2)
                continue
                
            if not key_entry["used"] or not key_entry["bound_hwid"]:
                key_entry["used"] = True
                key_entry["bound_hwid"] = current_hwid
                save_keys(keys)
                print(GREEN + f"[✔] Lizenz aktiviert! Gültig bis: {key_entry['expires_at']}" + RESET)
            
            loading_animation("Authentifiziere Lizenz")
            print(GREEN + "[✔] Zugriff gewährt!" + RESET)
            time.sleep(0.8)
            return entered_key, False, key_entry['expires_at']
                
        elif choice == "0":
            print(GREEN + "\n[+] Bis bald, boss." + RESET)
            sys.exit(0)

# --- Admin Panel ---
def admin_panel():
    while True:
        clear_screen()
        print(CYAN + BOLD + "=== SWATTINGLARPS ADMIN PANEL ===" + RESET)
        print(YELLOW + "  [1] Key generieren: 1 Tag" + RESET)
        print(YELLOW + "  [2] Key generieren: 7 Tage" + RESET)
        print(YELLOW + "  [3] Key generieren: Lifetime" + RESET)
        print(YELLOW + "  [4] Alle Keys anzeigen" + RESET)
        print(YELLOW + "  [0] Zurück zum Hauptmenü" + RESET)
        
        choice = input(f"\n{YELLOW}[?] ADMIN > {RESET}").strip()
        keys = load_keys()
        
        if choice in ["1", "2", "3"]:
            dtype_map = {"1": "1day", "2": "7days", "3": "lifetime"}
            new_key, exp_date, label = generate_discord_id_key(dtype_map[choice])
            keys.append({"key": new_key, "role": "user", "used": False, "bound_hwid": None, "expires_at": exp_date})
            save_keys(keys)
            print(GREEN + f"\n[✔] Neuer {label} Key erstellt: {new_key}\n[i] Gültig bis: {exp_date}" + RESET)
            input(f"\n{YELLOW}[ENTER] Weiter...{RESET}")
            
        elif choice == "4":
            print(CYAN + "\n--- LIZENZ-ID LISTE ---" + RESET)
            for idx, k in enumerate(keys, 1):
                hwid_status = f"HWID aktiv" if k['bound_hwid'] else "Ungebunden"
                exp_dt = datetime.strptime(k["expires_at"], "%Y-%m-%d %H:%M:%S")
                status = RED + "ABGELAUFEN" + RESET if datetime.now() > exp_dt else (YELLOW + f"Aktiv ({hwid_status})" + RESET if k["used"] else GREEN + "Frei" + RESET)
                print(f"  {idx}. {k['key']} | {status}")
            input(f"\n{YELLOW}[ENTER] Weiter...{RESET}")
        elif choice == "0":
            break

# --- Tool Implementierungen ---
def tiktok_lookup():
    username = input(f"{YELLOW}[?] TikTok Username: {RESET}").strip()
    url = f"https://www.tiktok.com/@{username}"
    print(f"{CYAN}[+] Lade TikTok-Daten für: {username}{RESET}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2)"})
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', html)
            if match:
                data = json.loads(match.group(1))
                user_detail = data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo", {})
                user = user_detail.get("user", {})
                stats = user_detail.get("stats", {})
                print(GREEN + "\n" + "="*40)
                print(f" Account ID:   {user.get('id')}")
                print(f" SecUID:       {user.get('secUid')}")
                print(f" Nickname:     {user.get('nickname')}")
                print(f" Follower:     {stats.get('followerCount')}")
                print(f" Likes:        {stats.get('heartCount')}")
                print("="*40 + RESET)
            else:
                print(RED + "[-] Rehydration-Datenblock nicht gefunden." + RESET)
    except Exception as e:
        print(RED + f"[-] Fehler: {e}" + RESET)

def ip_lookup():
    target = input(f"{YELLOW}[?] IP oder Domain eingeben: {RESET}").strip()
    try:
        url = f"http://ip-api.com/json/{target}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("status") == "success":
                print(GREEN + "\n" + "="*40)
                print(f" IP / Host:    {data.get('query')}")
                print(f" Land:         {data.get('country')} ({data.get('countryCode')})")
                print(f" Region:       {data.get('regionName')}")
                print(f" Stadt:        {data.get('city')}")
                print(f" ISP:          {data.get('isp')}")
                print("="*40 + RESET)
            else:
                print(RED + f"[-] API Fehler: {data.get('message')}" + RESET)
    except Exception as e:
        print(RED + f"[-] Fehler: {e}" + RESET)

def dns_lookup():
    domain = input(f"{YELLOW}[?] Domain eingeben: {RESET}").strip()
    try:
        ip = socket.gethostbyname(domain)
        print(GREEN + f"\n[+] Ziel: {domain} --> IP: {ip}" + RESET)
    except Exception as e:
        print(RED + f"[-] Fehler: {e}" + RESET)

def http_headers():
    url = input(f"{YELLOW}[?] URL eingeben (https://...): {RESET}").strip()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            print(GREEN + f"\n[+] Status Code: {resp.status}" + CYAN)
            for h, v in resp.headers.items():
                print(f" {h}: {v}")
            print(GREEN + "="*40 + RESET)
    except Exception as e:
        print(RED + f"[-] Fehler: {e}" + RESET)

def hash_generator():
    text = input(f"{YELLOW}[?] Text für Hash-Generierung: {RESET}").strip()
    md5_h = hashlib.md5(text.encode()).hexdigest()
    sha256_h = hashlib.sha256(text.encode()).hexdigest()
    print(GREEN + f"\n[+] MD5:    {md5_h}")
    print(f"[+] SHA256: {sha256_h}" + RESET)

def base64_tool():
    mode = input(f"{YELLOW}[1] Encode  [2] Decode: {RESET}").strip()
    val = input(f"{YELLOW}[?] Eingabetext: {RESET}").strip()
    try:
        if mode == "1":
            res = base64.b64encode(val.encode()).decode()
            print(GREEN + f"[+] Base64: {res}" + RESET)
        else:
            res = base64.b64decode(val.encode()).decode()
            print(GREEN + f"[+] Klartext: {res}" + RESET)
    except Exception as e:
        print(RED + f"[-] Fehler: {e}" + RESET)

def discord_id_lookup():
    print(CYAN + "\n[*] Discord ID Lookup (Offizielle API)" + RESET)
    user_id = input(f"{YELLOW}[?] Discord User ID eingeben: {RESET}").strip()
    
    if not user_id.isdigit():
        print(RED + "[-] Ungültige ID. Eine Discord ID besteht nur aus Zahlen." + RESET)
        return
        
    url = f"https://discord.com/api/v10/users/{user_id}"
    print(f"{CYAN}[+] Sende Abfrage für ID: {user_id}{RESET}")
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "STASINT-Framework (https://github.com)"
            }
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(GREEN + "\n" + "="*40)
            print(f" Username:      {data.get('username')}")
            print(f" Global Name:   {data.get('global_name', 'Keiner')}")
            print(f" ID:            {data.get('id')}")
            print(f" Bot Account:   {data.get('bot', False)}")
            print("="*40 + RESET)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(RED + "[-] Fehler 401: Authentifizierung erforderlich." + RESET)
        elif e.code == 404:
            print(RED + "[-] Fehler 404: Benutzer nicht gefunden oder ungültige ID." + RESET)
        else:
            print(RED + f"[-] HTTP Fehler: {e.code}" + RESET)
    except Exception as e:
        print(RED + f"[-] Fehler: {e}" + RESET)

def uuid_generator():
    print(CYAN + "\n[*] Generiere UUID v4..." + RESET)
    new_uuid = str(uuid.uuid4())
    print(GREEN + "\n" + "="*40)
    print(f" Generierte UUID v4: {new_uuid}")
    print("="*40 + RESET)

def url_codec():
    mode = input(f"{YELLOW}[1] URL Encode  [2] URL Decode: {RESET}").strip()
    val = input(f"{YELLOW}[?] Eingabetext/URL: {RESET}").strip()
    if mode == "1":
        encoded = urllib.parse.quote(val)
        print(GREEN + f"[+] Encodiert: {encoded}" + RESET)
    else:
        decoded = urllib.parse.unquote(val)
        print(GREEN + f"[+] Decodiert: {decoded}" + RESET)

def email_validator():
    email = input(f"{YELLOW}[?] E-Mail Adresse eingeben: {RESET}").strip()
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if re.match(pattern, email):
        print(GREEN + f"[✔] Format ist gültig: {email}" + RESET)
    else:
        print(RED + f"[-] Ungültiges E-Mail Format." + RESET)

def placeholder_tool(name):
    print(CYAN + f"\n[*] Starte Modul: {name}..." + RESET)
    val = input(f"{YELLOW}[?] Ziel/Query für {name}: {RESET}").strip()
    print(GREEN + f"[+] Analyse für '{val}' erfolgreich simuliert." + RESET)

# --- 40 Tools Wörterbuch ---
tools_dict = {
    1: ("TikTok Lookup", tiktok_lookup),
    2: ("IP / Geo Lookup", ip_lookup),
    3: ("DNS Host Resolver", dns_lookup),
    4: ("HTTP Header Analyzer", http_headers),
    5: ("Hash Generator", hash_generator),
    6: ("Base64 Codec", base64_tool),
    7: ("Discord ID Lookup", discord_id_lookup),
    8: ("Breach Scanner", lambda: placeholder_tool("Breach Scanner")),
    9: ("Username Checker", lambda: placeholder_tool("Username Checker")),
    10: ("Port Scanner", lambda: placeholder_tool("Port Scanner")),
    11: ("SSL Inspector", lambda: placeholder_tool("SSL Inspector")),
    12: ("Subdomain Enum", lambda: placeholder_tool("Subdomain Enum")),
    13: ("WHOIS Lookup", lambda: placeholder_tool("WHOIS Lookup")),
    14: ("MAC Vendor", lambda: placeholder_tool("MAC Vendor")),
    15: ("Robots Parser", lambda: placeholder_tool("Robots Parser")),
    16: ("Sitemap Extractor", lambda: placeholder_tool("Sitemap Extractor")),
    17: ("Ping / Latency", lambda: placeholder_tool("Ping Test")),
    18: ("Meta Scraper", lambda: placeholder_tool("Meta Scraper")),
    19: ("Redirect Tracer", lambda: placeholder_tool("Redirect Tracer")),
    20: ("UA Fuzzer", lambda: placeholder_tool("UA Fuzzer")),
    21: ("JWT Decoder", lambda: placeholder_tool("JWT Decoder")),
    22: ("URL Codec", url_codec),
    23: ("Password Analyzer", lambda: placeholder_tool("Password Analyzer")),
    24: ("Hex Converter", lambda: placeholder_tool("Hex Converter")),
    25: ("Binary Converter", lambda: placeholder_tool("Binary Converter")),
    26: ("UUID Generator", uuid_generator),
    27: ("String Generator", lambda: placeholder_tool("String Gen")),
    28: ("Net Interfaces", lambda: placeholder_tool("Net Interfaces")),
    29: ("ARP Viewer", lambda: placeholder_tool("ARP Viewer")),
    30: ("Ping Sweep", lambda: placeholder_tool("Ping Sweep")),
    31: ("HTTP Method Test", lambda: placeholder_tool("HTTP Method Tester")),
    32: ("Cookie Analyzer", lambda: placeholder_tool("Cookie Analyzer")),
    33: ("CORS Checker", lambda: placeholder_tool("CORS Checker")),
    34: ("Security Audit", lambda: placeholder_tool("Security Audit")),
    35: ("Email Validator", email_validator),
    36: ("Phone Parser", lambda: placeholder_tool("Phone Parser")),
    37: ("EXIF Extractor", lambda: placeholder_tool("EXIF Extractor")),
    38: ("Link Checker", lambda: placeholder_tool("Link Checker")),
    39: ("Env Inspector", lambda: placeholder_tool("Env Inspector")),
    40: ("STASINT Diagnostics", lambda: placeholder_tool("STASINT Diagnostics"))
}

def display_menu_grid(is_admin=False):
    keys = sorted(tools_dict.keys())
    half = len(keys) // 2
    
    print(YELLOW + "  [+] Wähle ein Tool aus (1 - 40):" + RESET)
    if is_admin:
        print(RED + "  [A] SWATTINGLARPS Admin Panel öffnen" + RESET)
    print(YELLOW + "  [0] Beenden\n" + RESET)

    for i in range(half):
        left_key = keys[i]
        right_key = keys[i + half]
        
        left_name = tools_dict[left_key][0]
        right_name = tools_dict[right_key][0]
        
        col1 = f"{CYAN}[{left_key:2d}]{RESET} {left_name:<23}"
        col2 = f"{CYAN}[{right_key:2d}]{RESET} {right_name:<23}"
        print(f"  {col1} | {col2}")
    print()

def main_menu():
    current_session, is_admin, expires_at = auth_menu()
    loading_animation("Lade STASINT 40-Tools Core")
    
    while True:
        banner(is_admin, expires_at)
        display_menu_grid(is_admin)
        
        choice = input(f"{YELLOW}[?] STASINT > {RESET}").strip()
        
        if choice == "0" or choice.lower() == "exit":
            print(GREEN + "\n[+] STASINT wird beendet. Bis bald, boss." + RESET)
            break
            
        if is_admin and choice.lower() == "a":
            admin_panel()
            clear_screen()
            continue
        
        try:
            c_int = int(choice)
            if c_int in tools_dict:
                clear_screen()
                print(CYAN + f"\n=== TOOL #{c_int}: {tools_dict[c_int][0]} ===" + RESET)
                tools_dict[c_int][1]()
                input(f"\n{YELLOW}[ENTER] Zurück zum Hauptmenü...{RESET}")
                clear_screen()
            else:
                print(RED + "[-] Ungültige Nummer. Bitte 1-40 wählen." + RESET)
                time.sleep(1)
                clear_screen()
        except ValueError:
            print(RED + "[-] Bitte eine gültige Zahl eingeben." + RESET)
            time.sleep(1)
            clear_screen()

if __name__ == "__main__":
    main_menu()

