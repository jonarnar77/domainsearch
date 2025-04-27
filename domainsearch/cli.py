# search_dns_dynamic.py

import sys
import socket
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

TLD_LIST_FILE = "tlds.txt"
IANA_TLD_LIST_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
MAX_WORKERS = 20
DEFAULT_TIMEOUT = 3  # Default timeout for HTTPS checks


def fetch_tlds():
    try:
        response = requests.get(IANA_TLD_LIST_URL, timeout=10)
        response.raise_for_status()
        tlds = []
        for line in response.text.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            tlds.append("." + line.strip().lower())
        return tlds
    except Exception as e:
        print(f"Failed to fetch TLDs: {e}")
        sys.exit(1)


def save_tlds_to_file(tlds):
    with open(TLD_LIST_FILE, "w") as f:
        for tld in tlds:
            f.write(tld + "\n")
    print(f"Saved {len(tlds)} TLDs to {TLD_LIST_FILE}")


def load_tlds_from_file():
    if not os.path.exists(TLD_LIST_FILE):
        print(f"No {TLD_LIST_FILE} found. Downloading fresh list...")
        tlds = fetch_tlds()
        save_tlds_to_file(tlds)
    with open(TLD_LIST_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def check_domain(domain):
    try:
        socket.gethostbyname(domain)
        return domain
    except socket.gaierror:
        return None


def check_https(domain, timeout):
    try:
        with socket.create_connection((domain, 443), timeout=timeout):
            return domain
    except (socket.timeout, socket.error):
        return None


def color_text(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "reset": "\033[0m",
    }
    return f"{colors[color]}{text}{colors['reset']}"


def print_help():
    help_text = """
Usage:
  python search_dns_dynamic.py <domain_base> [--check-site] [--output <file>] [--timeout <seconds>]
  python search_dns_dynamic.py --update
  python search_dns_dynamic.py --input <file> --check-site [--timeout <seconds>]

Examples:
  python search_dns_dynamic.py advania
  python search_dns_dynamic.py advania --check-site
  python search_dns_dynamic.py advania --output results.txt
  python search_dns_dynamic.py --input results.txt --check-site
  python search_dns_dynamic.py --update

Options:
  --check-site      Check if port 443 (HTTPS) is responding
  --output <file>   Save found domains to a file
  --input <file>    Load domains from a file instead of searching
  --timeout <sec>   Set timeout for HTTPS checks (default: 3s)
  --update          Update the TLD list from IANA
  --help            Show this help message
"""
    print(help_text)


def parse_args():
    args = sys.argv[1:]
    options = {
        "mode": "search",  # or "input"
        "domain_base": None,
        "input_file": None,
        "check_site": False,
        "output_file": None,
        "update": False,
        "timeout": DEFAULT_TIMEOUT,
    }

    if not args or "--help" in args:
        print_help()
        sys.exit(0)

    if args[0] == "--update":
        options["update"] = True
        return options

    if args[0] == "--input":
        if len(args) < 2:
            print("Usage: python search_dns_dynamic.py --input <file> [--check-site]")
            sys.exit(1)
        options["mode"] = "input"
        options["input_file"] = args[1]
        if "--check-site" in args:
            options["check_site"] = True
        if "--timeout" in args:
            timeout_idx = args.index("--timeout")
            if len(args) > timeout_idx + 1:
                options["timeout"] = int(args[timeout_idx + 1])
            else:
                print("Missing value after --timeout")
                sys.exit(1)
        return options

    # Otherwise, assume normal domain search
    options["domain_base"] = args[0]
    if "--check-site" in args:
        options["check_site"] = True
    if "--output" in args:
        output_idx = args.index("--output")
        if len(args) > output_idx + 1:
            options["output_file"] = args[output_idx + 1]
        else:
            print("Missing filename after --output")
            sys.exit(1)
    if "--timeout" in args:
        timeout_idx = args.index("--timeout")
        if len(args) > timeout_idx + 1:
            options["timeout"] = int(args[timeout_idx + 1])
        else:
            print("Missing value after --timeout")
            sys.exit(1)

    return options


def run():
    options = parse_args()

    if options["update"]:
        print("Fetching latest TLDs from IANA...")
        tlds = fetch_tlds()
        save_tlds_to_file(tlds)
        sys.exit(0)

    domains = []

    if options["mode"] == "input":
        input_file = options["input_file"]
        if not os.path.exists(input_file):
            print(f"Input file '{input_file}' does not exist.")
            sys.exit(1)
        with open(input_file, "r") as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domain_base = options["domain_base"]
        tlds = load_tlds_from_file()
        domains = [domain_base + tld for tld in tlds]

        print(
            f"Searching domains for base '{domain_base}' with {MAX_WORKERS} threads..."
        )

        found_domains = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_domain = {
                executor.submit(check_domain, domain): domain for domain in domains
            }

            for future in as_completed(future_to_domain):
                result = future.result()
                if result:
                    found_domains.append(result)
                    print(color_text(f"{result} exists!", "green"))

        domains = found_domains

        if options["output_file"]:
            with open(options["output_file"], "w") as f:
                for domain in domains:
                    f.write(domain + "\n")
            print(f"\nSaved {len(domains)} domains to {options['output_file']}")

    if options["check_site"]:
        print(
            f"\nChecking HTTPS (port 443) on {len(domains)} domains (timeout {options['timeout']}s)..."
        )

        alive_domains = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_domain = {
                executor.submit(check_https, domain, options["timeout"]): domain
                for domain in domains
            }

            for future in as_completed(future_to_domain):
                result = future.result()
                domain = future_to_domain[future]
                if result:
                    alive_domains.append(result)
                    print(color_text(f"{result} responds on 443!", "green"))
                else:
                    print(color_text(f"{domain} no response on 443", "red"))

        print(f"\n{len(alive_domains)} domains responded on port 443.")


if __name__ == "__main__":
    run()