import os
import requests
import base64
import tempfile
import re

# 颜色输出函数
def log_info(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}")

# 排序包含和排除的域名列表
def sort_files(include_file, exclude_file):
    log_info("Sorting include and exclude domain lists...")
    # 如果文件不存在，创建空文件
    if not os.path.exists(include_file):
        with open(include_file, 'w') as f:
            pass
    if not os.path.exists(exclude_file):
        with open(exclude_file, 'w') as f:
            pass

    with open(include_file, 'r') as f:
        include_domains = sorted(set(f.read().splitlines()))
    with open(exclude_file, 'r') as f:
        exclude_domains = sorted(set(f.read().splitlines()))
    with open(include_file, 'w') as f:
        f.write('\n'.join(include_domains))
    with open(exclude_file, 'w') as f:
        f.write('\n'.join(exclude_domains))

# 下载并解码 GFWList 文件
def download_gfwlist(url, output_file):
    log_info("Downloading and decoding gfwlist...")
    response = requests.get(url)
    if response.status_code == 200:
        content = base64.b64decode(response.content).decode('utf-8')
        with open(output_file, 'w') as f:
            f.write(content)
        log_info("Decoded content saved to gfwlist.txt")
        return content
    else:
        log_error("Failed to download or decode gfwlist")
        return None

# 处理 GFWList 文件
def process_gfwlist(content, output_file):
    log_info("Processing gfwlist...")
    ignore_pattern = re.compile(r'^\!|\[|^@@|(https?://){0,1}[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
    head_filter_pattern = re.compile(r'^(\|\|?)?(https?://)?')
    tail_filter_pattern = re.compile(r'/.*$|%2F.*$')
    domain_pattern = re.compile(r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)')
    handle_wildcard_pattern = re.compile(r'^(([a-zA-Z0-9]*\*[-a-zA-Z0-9]*)?(\.))?([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)(\*[a-zA-Z0-9]*)?$')

    lines = content.splitlines()

    domains = []
    for line in lines:
        if not ignore_pattern.match(line):
            line = head_filter_pattern.sub('', line)
            line = tail_filter_pattern.sub('', line)
            if domain_pattern.match(line):
                domain = handle_wildcard_pattern.sub(r'\4', line).strip()
                if domain:
                    domains.append(domain)

    with open(output_file, 'w') as f:
        f.write('\n'.join(domains))

# 获取现有的 DNS 静态记录
def get_existing_records():
    log_info("Fetching existing DNS static records...")
    # 假设你有一个方法可以从 RouterOS 设备获取现有的 DNS 静态记录
    # 这里只是一个示例，实际情况下你可能需要通过 API 或其他方式获取
    existing_records = [
        "85.17.73.31",
        "afreecatv.com",
        "agnesb.fr",
        "example.com"
    ]
    return existing_records

# 生成新的 DNS RSC 文件
def create_dns_rsc(input_file, output_file, dns_server):
    log_info("Creating dns.rsc...")
    with open(input_file, 'r') as f:
        new_domains = set(f.read().splitlines())

    existing_records = set(get_existing_records())

    # 找出需要添加、删除和保留的记录
    to_add = new_domains - existing_records
    to_remove = existing_records - new_domains
    to_keep = existing_records & new_domains

    with open(output_file, 'w') as f:
        f.write(':global dnsserver "{}"\n'.format(dns_server))

        # 删除需要删除的记录
        for domain in to_remove:
            f.write('/ip dns static remove [/ip dns static find name="{}"]\n'.format(domain))

        # 添加需要添加的记录
        for domain in to_add:
            f.write('/ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=yes name="{}"\n'.format(domain))

        # 保留现有的记录
        for domain in to_keep:
            f.write('/ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=yes name="{}"\n'.format(domain))

        f.write('/ip dns cache flush\n')

# 主函数
def main():
    url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
    gfwlist_txt = 'gfwlist.txt'
    processed_domains_file = 'processed_domains.txt'
    dns_rsc = 'dns.rsc'
    dns_server = '198.18.0.1'
    include_list = 'include_list.txt'
    exclude_list = 'exclude_list.txt'

    # 创建临时目录
    tmp_dir = tempfile.mkdtemp()
    log_info(f"Temporary directory created: {tmp_dir}")

    # 下载并解码 GFWList 文件
    content = download_gfwlist(url, os.path.join(tmp_dir, gfwlist_txt))
    if content is None:
        return

    # 处理 GFWList 文件
    process_gfwlist(content, os.path.join(tmp_dir, processed_domains_file))

    # 排序包含和排除的域名列表
    sort_files(include_list, exclude_list)

    # 创建 DNS RSC 文件
    create_dns_rsc(os.path.join(tmp_dir, processed_domains_file), dns_rsc, dns_server)

    log_info("dns.rsc 文件已创建。")

if __name__ == "__main__":
    main()
