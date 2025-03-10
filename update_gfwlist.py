import os
import requests
import base64
import tempfile
import re

# 下载并解码 GFWList 文件
def download_gfwlist(url, output_file):
    print("Downloading and decoding gfwlist...")
    response = requests.get(url)
    if response.status_code == 200:
        content = base64.b64decode(response.content).decode('utf-8')
        with open(output_file, 'w') as f:
            f.write(content)
        print("Decoded content saved to gfwlist.txt")
        return content
    else:
        print("Failed to download or decode gfwlist")
        return None

# 处理 GFWList 文件
def process_gfwlist(content, output_file):
    print("Processing gfwlist...")
    ignore_pattern = re.compile(r'^\!|\[|^@@|(https?://){0,1}[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
    head_filter_pattern = re.compile(r'^(\|\|?)?(https?://)?')
    tail_filter_pattern = re.compile(r'/.*$|%2F.*$')
    domain_pattern = re.compile(r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)')
    handle_wildcard_pattern = re.compile(r'^(([a-zA-Z0-9]*\*[-a-zA-Z0-9]*)?(\.))?([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)(\*[a-zA-Z0-9]*)?')

    lines = content.splitlines()

    domains = set()  # 使用集合去重
    for line in lines:
        if not ignore_pattern.match(line):
            line = head_filter_pattern.sub('', line)
            line = tail_filter_pattern.sub('', line)
            line = handle_wildcard_pattern.sub(r'\4', line)
            if domain_pattern.match(line):
                domain = line.strip()
                if domain:
                    domains.add(domain)

    # 将集合转换为列表并排序
    domains = sorted(domains)

    with open(output_file, 'w') as f:
        f.write('\n'.join(domains))

# 创建 GFWList RSC 文件
def create_gfwlist_rsc(input_file, output_file, dnsserver):
    print("Creating gfwlist.rsc...")
    with open(input_file, 'r') as f:
        domains = f.read().splitlines()

    with open(output_file, 'w') as f:
        f.write(f':global dnsserver "{dnsserver}"\n')
        f.write('/ip dns static remove [/ip dns static find forward-to=$dnsserver]\n')
        f.write('/ip dns static\n')
        f.write(':local domainList {\n')
        for domain in domains:
            f.write(f'    "{domain}";\n')
        f.write('}\n')
        f.write(':foreach domain in=$domainList do={\n')
        f.write('    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain\n')
        f.write('}\n')
        f.write('/ip dns cache flush\n')

# 比较新旧 gfwlist.rsc 文件
def compare_rsc_files(old_file, new_file):
    print("Comparing old and new gfwlist.rsc files...")

    with open(old_file, 'r') as f:
        old_content = f.read()
    with open(new_file, 'r') as f:
        new_content = f.read()

    old_domains = set(re.findall(r'"([^"]+)"', old_content))
    new_domains = set(re.findall(r'"([^"]+)"', new_content))

    to_add = new_domains - old_domains
    to_remove = old_domains - new_domains

    return to_add, to_remove

# 生成差异化的 DNS RSC 文件
def create_diff_dns_rsc(to_add, to_remove, output_file, dnsserver):
    print("Creating diff dns.rsc...")
    with open(output_file, 'w') as f:
        if to_add or to_remove:
            f.write(f':global dnsserver "{dnsserver}"\n')

            # 删除需要删除的记录
            if to_remove:
                for domain in to_remove:
                    f.write('/ip dns static remove [/ip dns static find forward-to=$dnsserver regexp="{}"]\n'.format(domain))

            # 添加需要添加的记录
            if to_add:
                f.write('/ip dns static\n')
                f.write(':local domainList {\n')
                for domain in to_add:
                    f.write(f'    "{domain}";\n')
                f.write('}\n')
                f.write(':foreach domain in=$domainList do={\n')
                f.write('    /ip dns static add forward-to=$dnsserver type=FWD address-list=gfw_list match-subdomain=no regexp=$domain\n')
                f.write('}\n')

            # 只有在有需要添加或删除的条目时才刷新缓存
            f.write('/ip dns cache flush\n')

# 主函数
def main():
    url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
    gfwlist_txt = 'gfwlist.txt'
    processed_domains_file = 'processed_domains.txt'
    gfwlist_rsc = 'gfwlist.rsc'
    dns_rsc = 'dns.rsc'
    dnsserver = '192.18.0.1'  # 在这里定义 DNS 服务器地址

    # 创建临时目录
    tmp_dir = tempfile.mkdtemp()
    print(f"Temporary directory created: {tmp_dir}")

    # 下载并解码 GFWList 文件
    content = download_gfwlist(url, os.path.join(tmp_dir, gfwlist_txt))
    if content is None:
        return

    # 处理 GFWList 文件
    process_gfwlist(content, os.path.join(tmp_dir, processed_domains_file))

    # 创建新的 gfwlist.rsc 文件
    create_gfwlist_rsc(os.path.join(tmp_dir, processed_domains_file), os.path.join(tmp_dir, gfwlist_rsc), dnsserver)

    # 比较新旧 gfwlist.rsc 文件
    old_gfwlist_rsc = 'gfwlist.rsc'
    if os.path.exists(old_gfwlist_rsc):
        to_add, to_remove = compare_rsc_files(old_gfwlist_rsc, os.path.join(tmp_dir, gfwlist_rsc))
    else:
        to_add, to_remove = set(), set()

    # 生成差异化的 dns.rsc 文件
    create_diff_dns_rsc(to_add, to_remove, dns_rsc, dnsserver)

    # 将新的 gfwlist.rsc 文件移动到当前目录
    os.replace(os.path.join(tmp_dir, gfwlist_rsc), gfwlist_rsc)

    # 将 gfwlist.txt 文件移动到当前目录
    os.replace(os.path.join(tmp_dir, gfwlist_txt), gfwlist_txt)

    print("dns.rsc 文件已创建。")

if __name__ == "__main__":
    main()
