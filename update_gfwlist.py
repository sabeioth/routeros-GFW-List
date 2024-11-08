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

    lines = content.splitlines()

    domains = []
    for line in lines:
        if not ignore_pattern.match(line):
            line = head_filter_pattern.sub('', line)
            line = tail_filter_pattern.sub('', line)
            if domain_pattern.match(line):
                domain = line.strip()
                if domain:
                    domains.append(domain)

    with open(output_file, 'w') as f:
        f.write('\n'.join(domains))

# 添加额外域名
def add_extra_domains(output_file, extra_domains):
    log_info("Adding extra domains...")
    with open(output_file, 'a') as f:
        for domain in extra_domains:
            f.write(f'{domain}\n')
    log_info("Extra domains added.")

# 创建 GFWList RSC 文件
def create_gfwlist_rsc(input_file, output_file, dnsserver):
    log_info("Creating gfwlist.rsc...")
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
    log_info("Comparing old and new gfwlist.rsc files...")

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
    log_info("Creating diff dns.rsc...")
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
    include_list = 'include_list.txt'
    exclude_list = 'exclude_list.txt'
    dnsserver = '192.18.0.1'  # 在这里定义 DNS 服务器地址

    # 创建临时目录
    tmp_dir = tempfile.mkdtemp()
    log_info(f"Temporary directory created: {tmp_dir}")

    # 下载并解码 GFWList 文件
    content = download_gfwlist(url, os.path.join(tmp_dir, gfwlist_txt))
    if content is None:
        return

    # 处理 GFWList 文件
    process_gfwlist(content, os.path.join(tmp_dir, processed_domains_file))

    # 添加额外域名
    extra_domains = [
        'google.com',
        'google.ad',
        'google.ae',
        'google.com.af',
        'google.com.ag',
        'google.com.ai',
        'google.al',
        'google.am',
        'google.co.ao',
        'google.com.ar',
        'google.as',
        'google.at',
        'google.com.au',
        'google.az',
        'google.ba',
        'google.com.bd',
        'google.be',
        'google.bf',
        'google.bg',
        'google.com.bh',
        'google.bi',
        'google.bj',
        'google.com.bn',
        'google.com.bo',
        'google.com.br',
        'google.bs',
        'google.bt',
        'google.co.bw',
        'google.by',
        'google.com.bz',
        'google.ca',
        'google.cd',
        'google.cf',
        'google.cg',
        'google.ch',
        'google.ci',
        'google.co.ck',
        'google.cl',
        'google.cm',
        'google.cn',
        'google.com.co',
        'google.co.cr',
        'google.com.cu',
        'google.cv',
        'google.com.cy',
        'google.cz',
        'google.de',
        'google.dj',
        'google.dk',
        'google.dm',
        'google.com.do',
        'google.dz',
        'google.com.ec',
        'google.ee',
        'google.com.eg',
        'google.es',
        'google.com.et',
        'google.fi',
        'google.com.fj',
        'google.fm',
        'google.fr',
        'google.ga',
        'google.ge',
        'google.gg',
        'google.com.gh',
        'google.com.gi',
        'google.gl',
        'google.gm',
        'google.gp',
        'google.gr',
        'google.com.gt',
        'google.gy',
        'google.com.hk',
        'google.hn',
        'google.hr',
        'google.ht',
        'google.hu',
        'google.co.id',
        'google.ie',
        'google.co.il',
        'google.im',
        'google.co.in',
        'google.iq',
        'google.is',
        'google.it',
        'google.je',
        'google.com.jm',
        'google.jo',
        'google.co.jp',
        'google.co.ke',
        'google.com.kh',
        'google.ki',
        'google.kg',
        'google.co.kr',
        'google.com.kw',
        'google.kz',
        'google.la',
        'google.com.lb',
        'google.li',
        'google.lk',
        'google.co.ls',
        'google.lt',
        'google.lu',
        'google.lv',
        'google.com.ly',
        'google.co.ma',
        'google.md',
        'google.me',
        'google.mg',
        'google.mk',
        'google.ml',
        'google.com.mm',
        'google.mn',
        'google.ms',
        'google.com.mt',
        'google.mu',
        'google.mv',
        'google.mw',
        'google.com.mx',
        'google.com.my',
        'google.co.mz',
        'google.com.na',
        'google.com.nf',
        'google.com.ng',
        'google.com.ni',
        'google.ne',
        'google.nl',
        'google.no',
        'google.com.np',
        'google.nr',
        'google.nu',
        'google.co.nz',
        'google.com.om',
        'google.com.pa',
        'google.com.pe',
        'google.com.pg',
        'google.com.ph',
        'google.com.pk',
        'google.pl',
        'google.pn',
        'google.com.pr',
        'google.ps',
        'google.pt',
        'google.com.py',
        'google.com.qa',
        'google.ro',
        'google.ru',
        'google.rw',
        'google.com.sa',
        'google.com.sb',
        'google.sc',
        'google.se',
        'google.com.sg',
        'google.sh',
        'google.si',
        'google.sk',
        'google.com.sl',
        'google.sn',
        'google.so',
        'google.sm',
        'google.sr',
        'google.st',
        'google.com.sv',
        'google.td',
        'google.tg',
        'google.co.th',
        'google.com.tj',
        'google.tk',
        'google.tl',
        'google.tm',
        'google.tn',
        'google.to',
        'google.com.tr',
        'google.tt',
        'google.com.tw',
        'google.co.tz',
        'google.com.ua',
        'google.co.ug',
        'google.co.uk',
        'google.com.uy',
        'google.co.uz',
        'google.com.vc',
        'google.co.ve',
        'google.vg',
        'google.co.vi',
        'google.com.vn',
        'google.vu',
        'google.ws',
        'google.rs',
        'google.co.za',
        'google.co.zm',
        'google.co.zw',
        'google.cat',
        'blogspot.ca',
        'blogspot.co.uk',
        'blogspot.com',
        'blogspot.com.ar',
        'blogspot.com.au',
        'blogspot.com.br',
        'blogspot.com.by',
        'blogspot.com.co',
        'blogspot.com.cy',
        'blogspot.com.ee',
        'blogspot.com.eg',
        'blogspot.com.es',
        'blogspot.com.mt',
        'blogspot.com.ng',
        'blogspot.com.tr',
        'blogspot.com.uy',
        'blogspot.de',
        'blogspot.gr',
        'blogspot.in',
        'blogspot.mx',
        'blogspot.ch',
        'blogspot.fr',
        'blogspot.ie',
        'blogspot.it',
        'blogspot.pt',
        'blogspot.ro',
        'blogspot.sg',
        'blogspot.be',
        'blogspot.no',
        'blogspot.se',
        'blogspot.jp',
        'blogspot.in',
        'blogspot.ae',
        'blogspot.al',
        'blogspot.am',
        'blogspot.ba',
        'blogspot.bg',
        'blogspot.ch',
        'blogspot.cl',
        'blogspot.cz',
        'blogspot.dk',
        'blogspot.fi',
        'blogspot.gr',
        'blogspot.hk',
        'blogspot.hr',
        'blogspot.hu',
        'blogspot.ie',
        'blogspot.is',
        'blogspot.kr',
        'blogspot.li',
        'blogspot.lt',
        'blogspot.lu',
        'blogspot.md',
        'blogspot.mk',
        'blogspot.my',
        'blogspot.nl',
        'blogspot.no',
        'blogspot.pe',
        'blogspot.qa',
        'blogspot.ro',
        'blogspot.ru',
        'blogspot.se',
        'blogspot.sg',
        'blogspot.si',
        'blogspot.sk',
        'blogspot.sn',
        'blogspot.tw',
        'blogspot.ug',
        'blogspot.cat',
        'twimg.edgesuite.net'
    ]
    add_extra_domains(os.path.join(tmp_dir, processed_domains_file), extra_domains)

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

    log_info("dns.rsc 文件已创建。")

if __name__ == "__main__":
    main()
