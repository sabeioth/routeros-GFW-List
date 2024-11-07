import base64
import requests
import logging

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

# 生成特定国家顶级域名的正则表达式条目
def generate_tld_rules(tlds):
    rules = []
    for tld in tlds:
        rule = f'\\.{tld}$'
        rules.append((rule, f"Country {tld}"))
    return rules

# 生成 .rsc 文件内容
def generate_rsc_content(processed_lines, tld_rules):
    rsc_content = "/ip dns static\n"
    
    def add_rule(comment, domain_pattern):
        nonlocal rsc_content
        rsc_content += f'add comment="{comment}" forward-to=198.18.0.1 regexp="{domain_pattern}" type=FWD\n'
    
    # 添加特定国家顶级域名的规则
    for domain_pattern, comment in tld_rules:
        add_rule(comment, domain_pattern)
    
    # 添加其他规则
    for line in processed_lines:
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
        
        # 生成特定国家顶级域名的规则
        tlds = ['cu', 'at', 'ca', 'nz', 'br', 'jp', 'in', 'tw', 'hk', 'mo', 'ph', 'vn', 'tr', 'my', 'sg', 'it', 'uk', 'us', 'kr', 'ru', 'fr', 'de', 'ms', 'be', 'fi']
        tld_rules = generate_tld_rules(tlds)
        
        # 生成并保存转换后的 dns.rsc 文件
        rsc_content = generate_rsc_content(processed_lines, tld_rules)
        write_rsc_file(rsc_content, 'dns.rsc')
        
        logging.info("Conversion complete, generated gfwlist.rsc and dns.rsc files.")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
