# Recon Subdomain Enumerator

A lightweight, automated Python script designed for penetration testers and bug bounty hunters to quickly harvest subdomains and verify their live status. 

The tool aggregates subdomains from public Certificate Transparency logs via crt.sh and the HackerTarget API, removes duplicates, and probes each discovery to identify HTTP status responses.

---

## Features

* Dual-Source OSINT: Pulls subdomains seamlessly from both crt.sh and HackerTarget.
* Automatic De-duplication: Filters out duplicate records automatically.
* Liveness Checker: Probes discovered subdomains over HTTPS to evaluate availability.
* Status Code Mapping: Colors and logs responses based on status (e.g., 200 OK, 301/302 Redirect, 404 Not Found).
* Clean Output Management: Automatically isolates and generates targeted log files for valid and broken domains.

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Venu-exe/recon.git](https://github.com/Venu-exe/recon.git)
cd recon
```
2.Install Dependencies

This script relies on requests for network operations and termcolor for terminal formatting. Install them using pip:
```Bash

pip install requests termcolor
```
Usage

Run the script from your terminal by passing the target root domain as an argument:
```Bash

python recon.py <target_domain>
```

Example:
```Bash

python recon.py example.com
```
Output Files

Upon execution, the script generates two clean text files in your current working directory named after your target:

    1  _sub.txt: The complete terminal log output, detailing the enumeration process and structural feedback.

    2  _alive.txt: A clean, line-separated list containing only the subdomains that responded successfully (HTTP 200, 301, 302). Ideal for piping directly into other tools like httpx, nmap, or nuclei.

Disclaimer

This tool is developed strictly for educational purposes, authorized security auditing, and bug bounty scoping. The developer assumes no liability for misuse or damage caused by this program.
