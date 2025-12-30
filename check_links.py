import re
import urllib.request
import sys
import os

def verify_links(filename):
    print(f"Reading {filename}...", flush=True)
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", flush=True)
        return

    links = re.findall(r'https?://[^\s\)]+', content)
    unique_links = list(set(links))
    
    print(f"Found {len(unique_links)} unique links.", flush=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    for link in unique_links:
        link = link.rstrip(')')
        print(f"Checking {link}...", end=" ", flush=True)
        try:
            req = urllib.request.Request(link, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"[OK] {response.status}", flush=True)
        except urllib.error.HTTPError as e:
            print(f"[FAIL] {e.code}", flush=True)
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)

if __name__ == "__main__":
    verify_links("versailles.md")
