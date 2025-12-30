import re
import requests
import glob
import os
from concurrent.futures import ThreadPoolExecutor

def extract_links_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        links = re.findall(r'\[.*?\]\((http[s]?://[^)]+)\)', content)
        return links
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def check_link(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    try:
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 405 or response.status_code == 403: 
            response = requests.get(url, headers=headers, timeout=10)
        
        if 200 <= response.status_code < 400:
            return url, True, response.status_code
        else:
            return url, False, response.status_code
    except Exception as e:
        return url, False, str(e)

def main():
    with open("validation_report.txt", "w") as log_file:
        def log(msg):
            print(msg)
            log_file.write(msg + "\n")
            
        log("Script starting...")
        md_files = glob.glob("*.md")
        all_links = set()
        
        log(f"Scanning {len(md_files)} markdown files...")
        for file in md_files:
            links = extract_links_from_file(file)
            all_links.update(links)
            log(f"  - {file}: found {len(links)} links")
        
        log(f"\nVerifying {len(all_links)} unique links...")
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(check_link, url): url for url in all_links}
            for future in futures:
                results.append(future.result())
                
        broken_links = [r for r in results if not r[1]]
        
        log("\n--- Validation Results ---")
        if not broken_links:
            log("✅ All links look good!")
        else:
            log(f"❌ Found {len(broken_links)} broken or problematic links:")
            for url, status, code in broken_links:
                log(f"  - {url} (Status: {code})")

if __name__ == "__main__":
    main()
