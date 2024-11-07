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

# 合并特定国家顶级域名条目
def merge_specific_tlds(processed_lines, tlds):
    tld_regex = '|'.join(map(re.escape, tlds))
    tld_pattern = re.compile(rf'\.(?:{tld_regex})$')
    merged_lines = []
    specific_tld_lines = []

    for line in processed_lines:
        if tld_pattern.search(line):
            specific_tld_lines.append(line)
        else:
            merged_lines.append(line)

    if specific_tld_lines:
        merged_lines.append(f'(?:{tld_regex})$')
    
    return merged_lines, specific_tld_lines

# 生成 .rsc 文件内容
def generate_rsc_content(merged_lines, specific_tld_lines):
    rsc_content = "/ip dns static\n"
    
    def add_rule(comment, domain_pattern):
        nonlocal rsc_content
        rsc_content += f'add comment="{comment}" forward-to=198.18.0.1 regexp="{domain_pattern}" type=FWD\n'
    
    for line in merged_lines:
        if line in specific_tld_lines:
            # 如果是特定 TLD 的条目，添加特定的注释
            tld = line.split('.')[-1]
            comment = f"Country {tld}"
        else:
            comment = "GFW"
        
        # 假设每行都是一个需要添加到 DNS 静态记录中的域名模式
        domain_pattern = line.replace('.', '\\.').replace('*', '.*')
        add_rule(comment, domain_pattern)
    
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
        
        # 合并特定国家顶级域名条目
        tlds = ['cu', 'at', 'ca', 'nz', 'br', 'jp', 'in', 'tw', 'hk', 'mo', 'ph', 'vn', 'tr', 'my', 'sg', 'it', 'uk', 'us', 'kr', 'ru', 'fr', 'de', 'ms', 'be', 'fi']
        merged_lines, specific_tld_lines = merge_specific_tlds(processed_lines, tlds)
        
        # 生成并保存转换后的 dns.rsc 文件
        rsc_content = generate_rsc_content(merged_lines, specific_tld_lines)
        write_rsc_file(rsc_content, 'dns.rsc')
        
        logging.info("Conversion complete, generated gfwlist.rsc and dns.rsc files.")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
