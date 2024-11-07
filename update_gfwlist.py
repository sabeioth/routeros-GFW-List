import requests
import base64
import re
import os
from collections import defaultdict

# 配置
DNS_FORWARD_IP = "198.18.0.1"
GFWLIST_URL = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
OUTPUT_FILE = "dns.rsc"
GFWLIST_RSC_FILE = "gfwlist.rsc"

# 定义公司及其对应的正则表达式
COMPANY_REGEX_MAP = {
    "Google": [
        r"(youtube|ytimg|android|androidify|appspot|autodraw|blogger|capitalg|chrome|chromeexperiments|chromestatus|creativelab5|debug|deepmind|dialogflow|firebaseio|googletagmanager|ggpht|gmail|gmodules|gstatic|gv|gvt0|gvt1|gvt2|gvt3|itasoftware|madewithcode|synergyse|tiltbrush|waymo|ampproject|certificate-transparency|chromium|getoutline|godoc|golang|gwtproject|polymer-project|tensorflow|waveprotocol|webmproject|webrtc|whatbrowser|material|shattered|recaptcha|abc|admin|getmdl)\.(com|net|org|xyz|io)$",
        r"google\.[a-z]+\.[a-z]+$",  # 匹配所有 google 子域名
        r"google\.[a-z]+$"           # 匹配所有 google 顶级域名
    ],
    "Microsoft": [
        r"(azure|bing|live|outlook|msn|surface|1drv|microsoft|azureedge|msauth|[a-z]-msedge|cd20|office|microsoftonline|msecnd|msftauth|skype|onedrive|modpim)\.(com|net|org)$"
    ],
    "Facebook": [
        r"(messenger|whatsapp|oculus|oculuscdn|cdninstagram|fb|fbcdn|instagram)\.(com|net|me)$"
    ],
    "Twitter": [
        r"(twimg|twitpic|twitter)\.(co|com)$"
    ],
    "Apple": [
        r"(icloud|me|appsto|appstore|aaplimg|crashlytics|mzstatic)\.(com|co|re)$"
    ],
    "Amazon": [
        r"(amazon|amazonaws|kindle|primevideo)\.com$"
    ],
    "Netflix": [
        r"(nflx|netflix|fast)\.(net|com)$"
    ],
    "Spotify": [
        r"(spotify|tidal|pcdn|scdn|pscdn)\.(com|co)$"
    ],
    "Telegram": [
        r"telegram\.org$"
    ],
    "Other": [
        r"(dropbox|hbo|quora|quoracdn|yahoo|ytimg|scorecardresearch|dazn|happyon|itv|itvstatic|pandora|pbs|4gtv|kktv|kfs|kkbox|twitch|ttvnw|viu|my5|channel5|litv|boltdns|encoretvb|mytvsuper|tvb|joox|deezer|dzcdn|bbc|bbci|c4assets|channel4|abema|ameba|hayabusa|fdcservers|yoshis|extride|chinaunicomglobal|ipinfo|ip|edge\.api\.brightcove|videos-f\.jwpsrv|content\.jwplatform)\.(com|net|org|io|tv|jp|co\.uk|me|re|sb)$"
    ]
}

# 定义已知国内可访问的域名列表
DOMESTIC_DOMAINS = [
    "aliyun.com",
    "baidu.com",
    "chinaso.com",
    "chinaz.com",
    "haosou.com",
    "ip.cn",
    "jike.com",
    "gov.cn",
    "qq.com",
    "sina.cn",
    "sogou.com",
    "so.com",
    "soso.com",
    "weibo.com",
    "yahoo.cn",
    "youdao.com",
    "zhongsou.com"
]

def fetch_gfwlist(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64decode(response.content).decode('utf-8')
    else:
        raise Exception(f"Failed to fetch GFW list: {response.status_code}")

def save_base64_gfwlist(gfwlist, filename):
    with open(filename, "wb") as f:
        f.write(base64.b64encode(gfwlist.encode('utf-8')))

def process_gfwlist(gfwlist):
    processed_rules = ["/ip dns static"]
    company_domains = {company: [] for company in COMPANY_REGEX_MAP.keys()}
    unmatched_domains = []

    # 存储已处理的域名以去重
    seen_domains = set()

    for line in gfwlist.splitlines():
        if line.startswith('!') or not line.strip():
            continue
        
        domain = line[2:].strip('^') if line.startswith('||') else line
        if domain in seen_domains or any(domain.endswith(f".{domestic_domain}") for domestic_domain in DOMESTIC_DOMAINS):
            continue

        # 处理子域名合并
        parts = domain.split('.')
        if len(parts) > 2:
            parent_domain = '.'.join(parts[-2:])
            if parent_domain in seen_domains or any(parent_domain.endswith(f".{domestic_domain}") for domestic_domain in DOMESTIC_DOMAINS):
                continue
            domain = parent_domain

        seen_domains.add(domain)

        matched_company = None
        for company, regex_list in COMPANY_REGEX_MAP.items():
            for regex in regex_list:
                if re.match(regex, domain):
                    matched_company = company
                    break
            if matched_company:
                break
        
        if matched_company:
            company_domains[matched_company].append(domain)
        else:
            unmatched_domains.append(domain)
    
    for company, domains in company_domains.items():
        if domains:
            combined_regex = "|".join(re.escape(domain) for domain in domains)
            company_rule = f'add comment={company} forward-to={DNS_FORWARD_IP} regexp="^({combined_regex})$" type=FWD'
            processed_rules.append(company_rule)
    
    for domain in unmatched_domains:
        rule = f'add comment=GFW forward-to={DNS_FORWARD_IP} regexp="^{domain}$" type=FWD"'
        processed_rules.append(rule)
    
    return "\n".join(processed_rules)

def save_rules(rules, filename):
    with open(filename, "w") as f:
        f.write(rules)

def main():
    try:
        gfwlist = fetch_gfwlist(GFWLIST_URL)
        
        # 保存原始 GFW 列表为 Base64 编码的文件
        save_base64_gfwlist(gfwlist, GFWLIST_RSC_FILE)
        print(f"GFW list saved as Base64 encoded file: {GFWLIST_RSC_FILE}")

        processed_rules = process_gfwlist(gfwlist)
        save_rules(processed_rules, OUTPUT_FILE)
        print(f"Rules saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
