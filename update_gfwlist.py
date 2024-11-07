import base64
import requests
import logging
import re

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 获取 gfwlist.txt 文件
def fetch_gfwlist():
    url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
    logging.info(f"Fetching gfwlist from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        logging.error(f"Failed to fetch gfwlist.txt: {response.status_code}")
        raise Exception(f"Failed to fetch gfwlist.txt: {response.status_code}")

# 解码 base64 编码的内容
def decode_gfwlist(encoded_content):
    logging.info("Decoding gfwlist")
    return base64.b64decode(encoded_content).decode('utf-8')

# 处理 gfwlist 内容
def process_gfwlist(decoded_content):
    lines = []
    for line in decoded_content.splitlines():
        if line.startswith('!'):
            continue  # 跳过注释行
        if line.startswith('@@'):
            continue  # 跳过直连条目
        if '||' in line:
            line = line.replace('||', '|')  # 替换 || 为 |
        if line:
            lines.append(line)
    return lines

# 合并特定国家顶级域名的条目
def merge_tld_rules(lines, tlds):
    tld_patterns = {}
    other_lines = []
    
    for line in lines:
        for tld in tlds:
            if line.endswith(f'.{tld}'):
                if tld not in tld_patterns:
                    tld_patterns[tld] = []
                tld_patterns[tld].append(line)
                break
        else:
            other_lines.append(line)
    
    tld_rules = []
    for tld, patterns in tld_patterns.items():
        if patterns:
            tld_rule = f'(?:{"|".join(map(re.escape, patterns))})$'
            tld_rules.append((tld_rule, f"Country {tld}"))
    
    return tld_rules, other_lines

# 合并特定域名模式的条目（例如 youtube）
def merge_special_domain_rules(lines, special_domains):
    special_patterns = {}
    other_lines = []
    
    for line in lines:
        for domain in special_domains:
            if domain in line:
                if domain not in special_patterns:
                    special_patterns[domain] = []
                special_patterns[domain].append(line)
                break
        else:
            other_lines.append(line)
    
    special_rules = []
    for domain, patterns in special_patterns.items():
        if patterns:
            domain_rule = f'(?:{"|".join(map(re.escape, patterns))})'
            special_rules.append((domain_rule, f"Domain {domain}"))
    
    return special_rules, other_lines

# 生成 .rsc 文件内容
def generate_rsc_content(tld_rules, special_rules, other_lines):
    rsc_content = "/ip dns static\n"
    
    def add_rule(comment, domain_pattern):
        nonlocal rsc_content
        rsc_content += f'add comment="{comment}" forward-to=198.18.0.1 regexp="{domain_pattern}" type=FWD\n'
    
    # 添加特定国家顶级域名的规则
    for domain_pattern, comment in tld_rules:
        add_rule(comment, domain_pattern)
    
    # 添加特定域名模式的规则
    for domain_pattern, comment in special_rules:
        add_rule(comment, domain_pattern)
    
    # 添加其他规则
    for line in other_lines:
        domain_pattern = line.replace('.', '\\.').replace('*', '.*')
        add_rule("GFW", domain_pattern)
    
    return rsc_content

# 写入 .rsc 文件
def write_rsc_file(content, filename):
    logging.info(f"Writing {filename}")
    with open(filename, 'w') as file:
        file.write(content)

def main():
    try:
        encoded_content = fetch_gfwlist()
        decoded_content = decode_gfwlist(encoded_content)
        
        # 保存解码后的 gfwlist.rsc 文件
        write_rsc_file(decoded_content, 'gfwlist.rsc')
        
        # 处理 gfwlist 内容
        processed_lines = process_gfwlist(decoded_content)
        
        # 定义特定国家顶级域名
        tlds = ['cu', 'at', 'ca', 'nz', 'br', 'jp', 'in', 'tw', 'hk', 'mo', 'ph', 'vn', 'tr', 'my', 'sg', 'it', 'uk', 'us', 'kr', 'ru', 'fr', 'de', 'ms', 'be', 'fi']
        
        # 合并特定国家顶级域名的条目
        tld_rules, remaining_lines = merge_tld_rules(processed_lines, tlds)
        
        # 定义特定域名模
        special_domains = ['youtube','netflix'，'telegram'，'instagram'，'spotify'，'facebook'，'twitter'，'twitch'，'steam'，'tumblr'，'google'，'pornHub'，'xvideo'，'gmail'，'google maps'，'android'，'deepmind'，'openai'，'midjourney'，'amazon'，'whatsapp'，'wikipedia'，'yahoo'，'chatgt'，'tikTok'，'quora']
        
        # 合并特定域名模式的条目
        special_rules, other_lines = merge_special_domain_rules(remaining_lines, special_domains)
        
        # 生成并保存转换后的 dns.rsc 文件
        rsc_content = generate_rsc_content(tld_rules, special_rules, other_lines)
        write_rsc_file(rsc_content, 'dns.rsc')
        
        logging.info("Conversion complete, generated gfwlist.rsc and dns.rsc files.")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
