import re
import requests
from collections import Counter
import base64

# 定义初始正则表达式模式
initial_patterns = [
    r".*(\.)\?(.*|\.)\.(cu|at|ca|nz|br|jp|in|tw|hk|mo|ph|vn|tr|my|sg|it|uk|us|kr|ru)$",
    r".*(\.)\?(google|facebook|blogspot|jav|pinterest|pron|github|bbcfmt|uk-live|hbo).*",
    r".*(\.)\?(dropbox|hbo).*",
    r".*(\.)\?(aa|akamai*|cloudfront|tiqcdn|akstat|go-mpulse|2o7).*",
    r".*(\.)\?(amazon|amazonaws|kindle|primevideo).*\.com",
    r".*(\.)\?(quora|quoracdn)\.(com|net)$",
    r".*(\.)\?(yahoo|ytimg|scorecardresearch)\.com$",
    r".*(\.)\?dazn.*\.com$",
    r".*(\.)\?(docker|mysql|mongodb|apache|mariadb|nginx|caddy)\.(io|com|org|net)$",
    r".*(\.)\?(oraclecloud|alicloud|salesforces|sap|workday)\.com$",
    r".*(\.)\?(pandora|pbs)\.(com|org)",
    r".*(\.)\?(azure|bing|live|outlook|msn|surface|1drv|microsoft)\.(net|com|org)",
    r".*(\.)\?(azureedge|msauth|[a-z]-msedge|cd20|office)\.(net|com|org)",
    r".*(\.)\?(twitch|ttvnw).*(\.net|\.tv)",
    r".*(\.)\?(nflx|netflix|fast).*(\.net|\.com)",
    r".*(\.)\?(youtube|ytimg)\.(com)",
    r".*(\.)\?(android|androidify|appspot|autodraw|blogger)\.com",
    r".*(\.)\?(capitalg|chrome|chromeexperiments|chromestatus|creativelab5)\.com",
    r".*(\.)\?(debug|deepmind|dialogflow|firebaseio|googletagmanager)\.com",
    r".*(\.)\?(ggpht|gmail|gmail|gmodules|gstatic|gv|gvt0|gvt1|gvt2|gvt3)\.com",
    r".*(\.)\?(itasoftware|madewithcode|synergyse|tiltbrush|waymo)\.com",
    r".*(\.)\?(widevine|x|app-measurement)\.(company|com)",
    r".*(\.)\?(ampproject|certificate-transparency|chromium)\.org",
    r".*(\.)\?(getoutline|godoc|golang|gwtproject)\.org",
    r".*(\.)\?(polymer-project|tensorflow)\.org",
    r".*(\.)\?(messenger|whatsapp|oculus|oculuscdn)\.(com|net)",
    r".*(\.)\?(cdninstagram|fb|fbcdn|instagram)\.(com|net|me)",
    r".*(\.)\?(twimg|twitpic|twitter)\.(co|com)",
    r".*(\.)\?(line(.*|\.)|naver)\.(me|com|net|jp)",
    r".*(\.)\?(openai|ai|discord|oaistatic|oaiusercontent)\.(com|gg)$",
    r".*(\.)\?(intercom|intercomcdn|featuregates|chatgpt)\.(io|org|com)$"
]

# 获取 GFW 列表
def get_gfwlist():
    url = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Failed to fetch GFW list")

# 解码 Base64 编码的 GFW 列表
def decode_gfwlist(gfwlist):
    return base64.b64decode(gfwlist).decode('utf-8')

# 统计后缀频率
def count_suffixes(gfwlist):
    suffixes = []
    lines = gfwlist.splitlines()
    for line in lines:
        if not line or line.startswith("!") or line.startswith("["):
            continue
        parts = line.split('.')
        if len(parts) > 1:
            suffix = parts[-1]
            suffixes.append(suffix)
    return Counter(suffixes)

# 动态生成新的正则表达式模式
def generate_new_patterns(suffix_counts):
    new_patterns = []
    for suffix, count in suffix_counts.items():
        if count > 10:
            new_patterns.append(rf".*(\.)\?(.*|\.)\.{suffix}$")
    return new_patterns

# 动态调整提取规则
def adjust_patterns(initial_patterns, gfwlist):
    adjusted_patterns = initial_patterns.copy()
    lines = gfwlist.splitlines()
    for pattern in initial_patterns:
        for line in lines:
            if not line or line.startswith("!") or line.startswith("["):
                continue
            match = re.search(r'\|(.*?)\|', line)
            if match:
                domain = match.group(1)
                if domain in pattern:
                    adjusted_pattern = pattern.replace(f"|{domain}|", "|")
                    adjusted_patterns.remove(pattern)
                    adjusted_patterns.append(adjusted_pattern)
                    break
    return adjusted_patterns

# 应用正则表达式过滤域名
def filter_domains(gfwlist, patterns):
    filtered_domains = []
    lines = gfwlist.splitlines()
    for line in lines:
        if not line or line.startswith("!") or line.startswith("["):
            continue
        matched = False
        for pattern in patterns:
            if re.match(pattern, line):
                filtered_domains.append(line)
                matched = True
                break
        if not matched:
            filtered_domains.append(line)
    return filtered_domains

# 生成 gfwlist.rsc 文件
def generate_gfwlist_rsc(domains, filename="gfwlist.rsc"):
    with open(filename, "w") as f:
        f.write("/ip firewall address-list\n")
        for domain in domains:
            f.write(f'add address={domain} list=gfwlist\n')

# 生成 dns.rsc 文件
def generate_dns_rsc(domains, filename="dns.rsc"):
    with open(filename, "w") as f:
        f.write("/ip dns static\n")
        for domain in domains:
            f.write(f'add name={domain} type=FWD forward-to=198.18.0.1\n')

# 主函数
def main():
    try:
        gfwlist = get_gfwlist()
        decoded_gfwlist = decode_gfwlist(gfwlist)
        suffix_counts = count_suffixes(decoded_gfwlist)
        new_patterns = generate_new_patterns(suffix_counts)
        adjusted_patterns = adjust_patterns(initial_patterns, decoded_gfwlist)
        all_patterns = adjusted_patterns + new_patterns
        filtered_domains = filter_domains(decoded_gfwlist, all_patterns)
        generate_gfwlist_rsc(filtered_domains)
        generate_dns_rsc(filtered_domains)
        print("GFW list updated successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
