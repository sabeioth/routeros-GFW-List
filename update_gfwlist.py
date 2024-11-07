import requests
import base64
import re
import os

# 配置
DNS_FORWARD_IP = "198.18.0.1"
GFWLIST_URL = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
OUTPUT_FILE = "dns.rsc"
GFWLIST_RSC_FILE = "gfwlist.rsc"

def fetch_gfwlist(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch GFW list: {response.status_code}")

def save_base64_gfwlist(gfwlist, filename):
    with open(filename, "wb") as f:
        f.write(base64.b64decode(gfwlist))

def extract_general_list(gfwlist):
    start_marker = "!##############General List Start###############"
    end_marker = "!##############General List End#################"
    start_index = gfwlist.find(start_marker)
    end_index = gfwlist.find(end_marker)

    if start_index == -1 or end_index == -1:
        raise Exception("Markers not found in the GFW list")

    return gfwlist[start_index + len(start_marker):end_index].strip()

def parse_groups(gfwlist):
    groups = {}
    current_group = None
    lines = gfwlist.splitlines()

    for line in lines:
        if line.startswith("!!---"):
            group_name = line[5:].strip()  # Remove leading "!---" and trailing spaces
            current_group = group_name
            groups[current_group] = []
        elif current_group is not None and line.strip():
            domain = line.strip().lstrip('|').strip('/')  # Remove leading '||' and trailing '/'
            if domain and not domain.startswith("!") and not domain.startswith("@@"):
                groups[current_group].append(domain)

    return groups

def generate_dns_rules(groups):
    rules = ["/ip dns static"]
    for group, domains in groups.items():
        if domains:
            combined_regex = "|".join(re.escape(domain) for domain in domains)
            rule = f'add comment="{group}" forward-to={DNS_FORWARD_IP} regexp="^({combined_regex})$" type=FWD'
            rules.append(rule)
    return "\n".join(rules)

def save_rules(rules, filename):
    with open(filename, "w") as f:
        f.write(rules)

def main():
    try:
        gfwlist = fetch_gfwlist(GFWLIST_URL)
        
        # 保存解码后的 GFW 列表为 gfwlist.rsc 文件
        save_base64_gfwlist(gfwlist, GFWLIST_RSC_FILE)
        print(f"GFW list saved as decoded file: {GFWLIST_RSC_FILE}")

        # 提取 General List 范围内的内容
        general_list = extract_general_list(gfwlist)

        # 解析分组信息
        groups = parse_groups(general_list)

        # 生成 DNS 规则
        dns_rules = generate_dns_rules(groups)

        # 保存 DNS 规则到 dns.rsc 文件
        save_rules(dns_rules, OUTPUT_FILE)
        print(f"DNS rules saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
