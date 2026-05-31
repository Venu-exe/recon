import sys
import  requests
import termcolor


def banner(target):
    print(' ')
    print(termcolor.colored('='*40, 'yellow'))
    print(termcolor.colored(f' Recon on {target}', 'blue'))
    print(termcolor.colored('='*40, 'yellow'))
    print('\n')
    print(' ')

def save(ouput_file, text):
    with open(ouput_file, 'a') as f:
        f.write(text + '\n')

def log(ouput_file, text):
    print(text)
    save(ouput_file, text)


def sub_domains(target, output_file):
    global subdomains
    log(output_file, '_'*40)
    log(output_file, '\n [+] Collecting Subdomains Using (crt.sh)')
    log(output_file, '_'*40)

    url = f'https://crt.sh/?q=%25.{target}&output=json'

    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()

        subdomains = sorted(set(entry['name_value'] for entry in data ))
        for sub in subdomains:
            log(output_file, sub)

        log(output_file, f'\n[+] Found {len(subdomains)} Subdomains')

    except Exception as e:
        log(output_file, f'\n[!] {e}')

    print('\n')

    try:
        fallback_url = f'https://api.hackertarget.com/hostsearch?q={target}'
        r = requests.get(fallback_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        subdomains = sorted(set(r.text.strip().split('\n')))
        for sub in subdomains:
            sub = sub.split(',')[0]
            log(output_file, sub)

        log(output_file, f'\n[+] Found {len(subdomains)} Subdomains')

    except Exception as e:
        log(output_file, f'\n[!] {e}')
    return [sub.split(',')[0] for sub in subdomains]


def check_alive(subdomains, output_file,alive_file):
    alive = []
    log(output_file, '_'*40)
    log(output_file,'\n Checking Alive Domains')
    log(output_file, '_'*40)

    for sub in subdomains:
        try:
            r = requests.get(f'https://{sub}', timeout=5, allow_redirects=True)
            log(output_file, termcolor.colored(f' {sub}', 'green'))
            if r.status_code == 200:
                log(output_file, termcolor.colored(f' Alive Domains: [{r.status_code}]', 'cyan'))
            elif r.status_code in [301, 302]:
                log(output_file, termcolor.colored(f' Redirecting Some Ware: [{r.status_code}]', 'blue'))
            elif r.status_code == 404:
                log(output_file, termcolor.colored(f'Check The CNAME: [{r.status_code}]', 'red'))
            else:
                pass
            alive.append(sub)

        except:
            log(output_file, termcolor.colored(f' [!] Dead {sub}', 'red'))
    log(output_file, f'\n[+] {len(alive)} alive out of {len(subdomains)}')
    for sub in alive:
         save(alive_file, sub)
    return alive




def main():
    if len(sys.argv) < 2:
        print(termcolor.colored('[!]usage: python recon.py <target>', 'red'))
        exit(1)

    target = sys.argv[1]
    alive_file = f'{target}alive.txt'
    output_file = f'{target}_sub.txt'
    open(output_file, 'w').close()
    banner(target)
    log(output_file, '[*] Script is Working')
    subdomains = sub_domains(target, output_file)
    check_alive(subdomains, output_file,alive_file)



if __name__ == '__main__':
    main()




