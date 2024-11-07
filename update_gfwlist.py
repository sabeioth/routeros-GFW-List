import requests
import base64
import re
import os

# 配置
DNS_FORWARD_IP = "198.18.0.1"
GFWLIST_URL = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
OUTPUT_FILE = "gfwlist_rules.rsc"

def fetch_gfwlist(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64decode(response.content).decode('utf-8')
    else:
        raise Exception(f"Failed to fetch GFW list: {response.status_code}")

def process_gfwlist(gfwlist):
    processed_rules = []
    for line in gfwlist.splitlines():
        if line.startswith('!') or not line.strip():
            continue
        if line.startswith('||'):
            domain = line[2:].strip('^')
            rule = f'/ip dns static add comment="GFW" forward-to={DNS_FORWARD_IP} regexp="^{domain}$" type=FWD'
            processed_rules.append(rule)
    return "\n".join(processed_rules)

def save_rules(rules, filename):
    with open(filename, "w") as f:
        f.write(rules)

def main():
    try:
        gfwlist = fetch_gfwlist(GFWLIST_URL)
        processed_rules = process_gfwlist(gfwlist)
        save_rules(processed_rules, OUTPUT_FILE)
        print(f"Rules saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
