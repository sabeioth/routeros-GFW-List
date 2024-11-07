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
    ]
    
    # 编译正则表达式模式
    filter_regex = [re.compile(pattern) for pattern in filter_patterns]
    
    # 过滤规则
    filtered_lines = []
    for line in decoded_content.splitlines():
        if not any(regex.match(line) for regex in filter_regex):
            # 替换 || 为 |
            line = line.replace('||', '|')
            filtered_lines.append(line)
    
    return filtered_lines

# 动态调整提取规则
def adjust_patterns(filtered_lines, patterns):
    adjusted_patterns = {}
    for key, pattern in patterns.items():
        # 提取子域名
        subdomains = re.findall(r'\|(.*?)\|', pattern)
        valid_subdomains = []
        for subdomain in subdomains:
            if any(subdomain in line for line in filtered_lines):
                valid_subdomains.append(subdomain)
        # 重新构建调整后的模式
        adjusted_pattern = pattern
        for subdomain in subdomains:
            if subdomain not in valid_subdomains:
                adjusted_pattern = adjusted_pattern.replace(f"|{subdomain}|", "")
        adjusted_patterns[key] = adjusted_pattern
    return adjusted_patterns

# 提取特定的正则表达式模式
def extract_specific_patterns(filtered_lines, patterns):
    extracted_lines = {key: [] for key in patterns}
    
    for line in filtered_lines:
        for key, pattern in patterns.items():
            if re.match(pattern, line):
                extracted_lines[key].append(line)
                break
    
    return extracted_lines

# 生成 .rsc 文件内容
def generate_rsc_content(filtered_lines, extracted_lines, patterns):
    rsc_content = "/ip dns static\n"
    
    def add_rule(comment, domain_pattern):
        nonlocal rsc_content
        rsc_content += f'add comment="{comment}" forward-to=198.18.0.1 regexp="{domain_pattern}" type=FWD\n'
    
    # 添加特定模式的条目
    for key, lines in extracted_lines.items():
        if lines:
            add_rule(key, patterns[key])
    
    # 处理未提取的条目
    for line in filtered_lines:
        if not any(line in v for v in extracted_lines.values()) and not line.startswith('!') and not line.startswith('@@'):
            domain_pattern = line.replace('.', '\\.').replace('*', '.*')
            add_rule("GFW", domain_pattern)
    
    return rsc_content

# 写入 .rsc 文件
def write_rsc_file(rsc_content, filename):
    with open(filename, 'w') as file:
        file.write(rsc_content)

def main():
    try:
        encoded_content = fetch_gfwlist()
        decoded_content = decode_gfwlist(encoded_content)
        
        # 保存解码后的 gfwlist.rsc 文件
        write_rsc_file(decoded_content, 'gfwlist.rsc')
        
        # 过滤和优化规则
        filtered_lines = optimize_rules(decoded_content)
        
        # 定义提取规则
        patterns = {
            "country_domains": r".*(\\.)\?(.*|\\.)\?\\.(cu|at|ca|nz|br|jp|in|tw|hk|mo|ph|vn|tr|my|sg|it|uk|us|kr|ru)\$",
            "specific_domains": r".*(\\.)\?(google|facebook|blogspot|jav|pinterest|pron|github|bbcfmt|uk-live|hbo).*",
            "dropbox_hbo": r".*(\\.)\?(dropbox|hbo).*",
            "cdn_domains": r".*(\\.)\?(aa|akamai*|cloudfront|tiqcdn|akstat|go-mpulse|2o7).*",
            "amazon_domains": r".*(\\.)\?(amazon|amazonaws|kindle|primevideo).*\\.com",
            "quora_domains": r".*(\\.)\?(quora|quoracdn)\\.(com|net)\$",
            "yahoo_domains": r".*(\\.)\?(yahoo|ytimg|scorecardresearch)\\.com\$",
            "dazn_domains": r".*(\\.)\?dazn.*\\.com\$",
            "docker_domains": r".*(\\.)\?(docker|mysql|mongodb|apache|mariadb|nginx|caddy)\\.(io|com|org|net)\$",
            "oracle_alibaba_domains": r".*(\\.)\?(oraclecloud|alicloud|salesforces|sap|workday)\\.com\$",
            "pandora_pbs_domains": r".*(\\.)\?(pandora|pbs)\\.(com|org)",
            "microsoft_domains": r".*(\\.)\?(azure|bing|live|outlook|msn|surface|1drv|microsoft)\\.(net|com|org)",
            "microsoft_cdn_domains": r".*(\\.)\?(azureedge|msauth|[a-z]-msedge|cd20|office)\\.(net|com|org)",
            "twitch_domains": r".*(\\.)\?(twitch|ttvnw).*(\\.net|\\.tv)",
            "netflix_domains": r".*(\\.)\?(nflx|netflix|fast).*(\\.net|\\.com)",
            "youtube_domains": r".*(\\.)\?(youtube|ytimg)\\.(com)",
            "google_domains": r".*(\\.)\?(android|androidify|appspot|autodraw|blogger)\\.com",
            "google_services_domains": r".*(\\.)\?(capitalg|chrome|chromeexperiments|chromestatus|creativelab5)\\.com",
            "google_debug_domains": r".*(\\.)\?(debug|deepmind|dialogflow|firebaseio|googletagmanager)\\.com",
            "google_media_domains": r".*(\\.)\?(ggpht|gmail|gmail|gmodules|gstatic|gv|gvt0|gvt1|gvt2|gvt3)\\.com",
            "google_other_domains": r".*(\\.)\?(itasoftware|madewithcode|synergyse|tiltbrush|waymo)\\.com",
            "google_widevine_domains": r".*(\\.)\?(widevine|x|app-measurement)\\.(company|com)",
            "google_org_domains": r".*(\\.)\?(ampproject|certificate-transparency|chromium)\\.org",
            "google_org2_domains": r".*(\\.)\?(getoutline|godoc|golang|gwtproject)\\.org",
            "google_org3_domains": r".*(\\.)\?(polymer-project|tensorflow)\\.org",
            "facebook_domains": r".*(\\.)\?(messenger|whatsapp|oculus|oculuscdn)\\.(com|net)",
            "instagram_domains": r".*(\\.)\?(cdninstagram|fb|fbcdn|instagram)\\.(com|net|me)",
            "twitter_domains": r".*(\\.)\?(twimg|twitpic|twitter)\\.(co|com)",
            "line_naver_domains": r".*(\\.)\?(line(.*|\\.)|naver)\\.(me|com|net|jp)",
            "openai_discord_domains": r".*(\\.)\?(openai|ai|discord|oaistatic|oaiusercontent)\\.(com|gg)\$",
            "intercom_domains": r".*(\\.)\?(intercom|intercomcdn|featuregates|chatgpt)\\.(io|org|com)\$"
        }
        
        # 动态调整提取规则
        adjusted_patterns = adjust_patterns(filtered_lines, patterns)
        
        # 提取特定的正则表达式模式
        extracted_lines = extract_specific_patterns(filtered_lines, adjusted_patterns)
        
        # 生成并保存转换后的 dns.rsc 文件
        rsc_content = generate_rsc_content(filtered_lines, extracted_lines, adjusted_patterns)
        write_rsc_file(rsc_content, 'dns.rsc')
        
        print("转换完成，已生成 gfwlist.rsc 和 dns.rsc 文件。")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
