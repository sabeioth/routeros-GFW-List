import base64
import requests
import re

# 获取 gfwlist.txt 文件
def fetch_gfwlist():
    url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch gfwlist.txt: {response.status_code}")

# 解码 base64 编码的内容
def decode_gfwlist(encoded_content):
    return base64.b64decode(encoded_content).decode('utf-8')

# 过滤和优化规则
def optimize_rules(decoded_content):
    # 定义要过滤掉的正则表达式模式
    filter_patterns = [
        r'^!.*$',  # 注释行
        r'^@@.*$',  # 白名单规则
        r'^\|.*',  # 包含管道符的规则
        r'^\*.*',  # 包含星号的规则
        r'^\..*',  # 以点开头的规则
        r'^//.*',  # 以双斜杠开头的规则
        r'^\[A-Z\].*',  # 以大写字母开头的规则
        r'^\$.+',  # 以美元符号开头的规则
        r'^/\*.+\*/',  # 包含注释的规则
        r'^\|\|.*\^',  # 包含 || 和 ^ 的规则
        r'^\.js$',  # 以 .js 结尾的规则
        r'^\.css$',  # 以 .css 结尾的规则
        r'^\.png$',  # 以 .png 结尾的规则
        r'^\.jpg$',  # 以 .jpg 结尾的规则
        r'^\.gif$',  # 以 .gif 结尾的规则
        r'^\.ico$',  # 以 .ico 结尾的规则
        r'^\.svg$',  # 以 .svg 结尾的规则
        r'^\.json$',  # 以 .json 结尾的规则
        r'^\.xml$',  # 以 .xml 结尾的规则
        r'^\.txt$',  # 以 .txt 结尾的规则
        r'^\.html$',  # 以 .html 结尾的规则
        r'^\.pdf$',  # 以 .pdf 结尾的规则
        r'^\.js\?',  # 以 .js? 开头的规则
        r'^\.css\?',  # 以 .css? 开头的规则
        r'^\.png\?',  # 以 .png? 开头的规则
        r'^\.jpg\?',  # 以 .jpg? 开头的规则
        r'^\.gif\?',  # 以 .gif? 开头的规则
        r'^\.ico\?',  # 以 .ico? 开头的规则
        r'^\.svg\?',  # 以 .svg? 开头的规则
        r'^\.json\?',  # 以 .json? 开头的规则
        r'^\.xml\?',  # 以 .xml? 开头的规则
        r'^\.txt\?',  # 以 .txt? 开头的规则
        r'^\.html\?',  # 以 .html? 开头的规则
        r'^\.pdf\?',  # 以 .pdf? 开头的规则
    ]
    
    # 编译正则表达式模式
    filter_regex = [re.compile(pattern) for pattern in filter_patterns]
    
    # 过滤规则
    filtered_lines = []
    for line in decoded_content.splitlines():
        if not any(regex.match(line) for regex in filter_regex):
            filtered_lines.append(line)
    
    return filtered_lines

# 提取特定的正则表达式模式
def extract_specific_patterns(filtered_lines):
    specific_patterns = {
        r'(upgrade|download)\.mikrotik\.com$': "MikroTik",
        r'.*\.(cu|at|ca|nz|br|jp|in|tw|hk|mo|ph|vn|tr|my|sg|it|uk|us|kr|ru)$': "County",
        r'.*\.(fr|de)$': "County",
        r'.*(.*|\\.).*(ms|be|fi)$': "Company",
        r'.*(\\.)\?(google|facebook|blogspot|jav|pinterest|pron|github|bbcfmt|uk-live|hbo).*': "KEYWORD",
        r'.*(\\.)\?(dropbox|hbo).*': "KEYWORD",
        r'.*(\\.)\?(aa|akamai*|cloudfront|tiqcdn|akstat|go-mpulse|2o7).*': "Public CDN",
        r'.*(\\.)\?(cloudflareinsights).*': "Public CDN",
        r'.*\.(icloud|me)\.com$': "Apple Services",
        r'.*(\\.)\?(appsto|appstore|aaplimg|crashlytics|mzstatic).*(\\.com|\\.co|.re)': "Apple Services"
    }
    
    extracted_patterns = {}
    for line in filtered_lines:
        for pattern, comment in specific_patterns.items():
            if re.match(pattern, line):
                if comment not in extracted_patterns:
                    extracted_patterns[comment] = []
                extracted_patterns[comment].append(line)
    
    return extracted_patterns

# 生成 .rsc 文件内容
def generate_rsc_content(filtered_lines, extracted_patterns):
    rsc_content = "/ip dns static\n"
    
    def add_rule(comment, domain_pattern):
        nonlocal rsc_content
        rsc_content += f'add comment="{comment}" forward-to=198.18.0.1 regexp="{domain_pattern}" type=FWD\n'
    
    # 添加特定的正则表达式模式
    for comment, patterns in extracted_patterns.items():
        for pattern in patterns:
            domain_pattern = pattern.replace('.', '\\.').replace('*', '.*')
            add_rule(comment, domain_pattern)
    
    # 添加剩余的规则
    for line in filtered_lines:
        if line and not line.startswith('!') and not line.startswith('@@'):
            # 假设每行都是一个需要添加到 DNS 静态记录中的域名模式
            domain_pattern = line.replace('.', '\\.').replace('*', '.*')
            add_rule("GFW", domain_pattern)
    
    return rsc_content

# 写入 .rsc 文件
def write_rsc_file(content, filename):
    with open(filename, 'w') as file:
        file.write(content)

def main():
    try:
        encoded_content = fetch_gfwlist()
        decoded_content = decode_gfwlist(encoded_content)
        
        # 保存解码后的 gfwlist.rsc 文件
        write_rsc_file(decoded_content, 'gfwlist.rsc')
        
        # 过滤规则
        filtered_lines = optimize_rules(decoded_content)
        
        # 提取特定的正则表达式模式
        extracted_patterns = extract_specific_patterns(filtered_lines)
        
        # 生成并保存转换后的 dns.rsc 文件
        rsc_content = generate_rsc_content(filtered_lines, extracted_patterns)
        write_rsc_file(rsc_content, 'dns.rsc')
        
        print("转换完成，已生成 gfwlist.rsc 和 dns.rsc 文件。")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
