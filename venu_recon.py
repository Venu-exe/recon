import sys
import requests
import termcolor
from concurrent.futures import ThreadPoolExecutor
import threading

print_lock = threading.Lock()


def banner(target):
    print(' ')
    print(termcolor.colored('=' * 40, 'yellow'))
    print(termcolor.colored(f' Recon on {target}', 'blue'))
    print(termcolor.colored('=' * 40, 'yellow'))
    print('\n')


def save(output_file, text):
    with open(output_file, 'a') as f:
        f.write(text + '\n')


def log(output_file, text):
    with print_lock:
        print(text)
        # Strips ANSI color codes if saving to a plain text file (optional but cleaner)
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        save(output_file, clean_text)


def sub_domains(target, output_file):
    log(output_file, '_' * 40)
    log(output_file, '\n [+] Collecting Subdomains Using (crt.sh & HackerTarget)')
    log(output_file, '_' * 40)

    found_subs = set()

    # --- Source 1: crt.sh ---
    url = f'https://crt.sh/?q=%25.{target}&output=json'
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            data = r.json()
            for entry in data:
                found_subs.add(entry['name_value'].strip().lower())
    except Exception as e:
        log(output_file, f'[!] crt.sh error: {e}')

    # --- Source 2: HackerTarget ---
    fallback_url = f'https://api.hackertarget.com/hostsearch?q={target}'
    try:
        r = requests.get(fallback_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200 and "error" not in r.text:
            for line in r.text.strip().split('\n'):
                if line:
                    sub = line.split(',')[0].strip().lower()
                    found_subs.add(sub)
    except Exception as e:
        log(output_file, f'[!] HackerTarget error: {e}')

    cleaned_subs = sorted(list(found_subs))
    for sub in cleaned_subs:
        log(output_file, sub)

    log(output_file, f'\n[+] Found {len(cleaned_subs)} Unique Subdomains')
    print('\n')

    return cleaned_subs


def check_single(sub, output_file, alive_file, dead_file, alive_list):
    try:
        r = requests.get(f'https://{sub}', timeout=5, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})

        if r.status_code == 200:
            log(output_file, termcolor.colored(f'  [+] ALIVE {sub} [200]', 'green'))
            save(alive_file, sub)
            with print_lock:
                alive_list.append(sub)

        elif r.status_code in [301, 302]:
            log(output_file, termcolor.colored(f'  [~] REDIRECT {sub} [{r.status_code}]', 'blue'))
            save(alive_file, sub)
            with print_lock:
                alive_list.append(sub)

        elif r.status_code == 404:
            log(output_file, termcolor.colored(f'  [-] DEAD {sub} [404]', 'red'))
            save(dead_file, sub)

        else:
            log(output_file, termcolor.colored(f'  [?] {sub} [{r.status_code}]', 'yellow'))

    except requests.exceptions.RequestException:
        log(output_file, termcolor.colored(f'  [!] DEAD {sub}', 'red'))
        save(dead_file, sub)


def check_alive(subdomains, output_file, alive_file, dead_file):
    alive_list = []
    log(output_file, '_' * 40)
    log(output_file, '\n [+] Checking Alive Domains')
    log(output_file, '_' * 40)

    with ThreadPoolExecutor(max_workers=30) as executor:
        for sub in subdomains:
            # Skip wildcard entries if crt.sh provides them (e.g., *.domain.com)
            if sub.startswith('*.'):
                sub = sub.replace('*.', '')
            executor.submit(check_single, sub, output_file, alive_file, dead_file, alive_list)

    log(output_file, f'\n[+] {len(alive_list)} alive out of {len(subdomains)}')
    return alive_list


def main():
    if len(sys.argv) < 2:
        print(termcolor.colored('[!] Usage: python recon.py <target>', 'red'))
        sys.exit(1)

    target = sys.argv[1]

    output_file = f'{target}_recon_log.txt'
    alive_file = f'{target}_alive.txt'
    dead_file = f'{target}_dead.txt'

    for f in [output_file, alive_file, dead_file]:
        open(f, 'w').close()

    banner(target)
    log(output_file, '[*] Script started...')

    # Run pipeline
    subdomains = sub_domains(target, output_file)

    if subdomains:
        check_alive(subdomains, output_file, alive_file, dead_file)
    else:
        log(output_file, '[!] No subdomains found to check.')


if __name__ == '__main__':
    main()