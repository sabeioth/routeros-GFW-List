import requests
import base64
import re
import os

# 配置
DNS_FORWARD_IP = "198.18.0.1"
GFWLIST_URL = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
OUTPUT_FILE = "dns.rsc"

# 定义公司及其对应的正则表达式
COMPANY_REGEX_MAP = {
    "Google": [
        r"(youtube|ytimg)\.com$",
        r"(android|androidify|appspot|autodraw|blogger)\.com$",
        r"(capitalg|chrome|chromeexperiments|chromestatus|creativelab5)\.com$",
        r"(debug|deepmind|dialogflow|firebaseio|googletagmanager)\.com$",
        r"(ggpht|gmail|gmail|gmodules|gstatic|gv|gvt0|gvt1|gvt2|gvt3)\.com$",
        r"(itasoftware|madewithcode|synergyse|tiltbrush|waymo)\.com$",
        r"(ampproject|certificate-transparency|chromium)\.org$",
        r"(getoutline|godoc|golang|gwtproject)\.org$",
        r"(polymer-project|tensorflow)\.org$",
        r"(waveprotocol|webmproject|webrtc|whatbrowser)\.org$",
        r"(material|shattered|recaptcha)\.(net|io)$",
        r"(abc|admin|getmdl)\.(xyz|net|io)$"
    ],
    "Microsoft": [
        r"(azure|bing|live|outlook|msn|surface|1drv|microsoft)\.(net|com|org)$",
        r"(azureedge|msauth|[a-z]-msedge|cd20|office)\.(net|com|org)$",
        r"(microsoftonline|msecnd|msftauth|skype|onedrive|modpim)\.(net|com|org)$"
    ],
    "Facebook": [
        r"(messenger|whatsapp|oculus|oculuscdn)\.(com|net)$",
        r"(cdninstagram|fb|fbcdn|instagram)\.(com|net|me)$"
    ],
    "Twitter": [
        r"(twimg|twitpic|twitter)\.(co|com)$"
    ],
    "Apple": [
        r"(icloud|me)\.com$",
        r"(appsto|appstore|aaplimg|crashlytics|mzstatic)\.(com|co|re)$"
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
        r"(dropbox|hbo)\.com$",
        r"(quora|quoracdn)\.(com|net)$",
        r"(yahoo|ytimg|scorecardresearch)\.com$",
        r"(dazn|happyon)\.(com|jp)$",
        r"(itv|itvstatic)\.com$",
        r"(pandora|pbs)\.(com|org)$",
        r"(4gtv|kktv)\.(tv|com|me)$",
        r"(kfs|kkbox)\.(io|com)$",
        r"(twitch|ttvnw)\.(net|tv)$",
        r"(viu|my5|channel5|litv)\.(tv|com)$",
        r"boltdns\.net$",
        r"encoretvb\.com$",
        r"(mytvsuper|tvb|joox)\.com$",
        r"(deezer|dzcdn)\.(com|net)$",
        r"(bbc|bbci)\.(co\.uk|com)$",
        r"(c4assets|channel4)\.com$",
        r"(abema|ameba|hayabusa)\.(jp|io)$",
        r"(fdcservers|yoshis|extride|chinaunicomglobal)\.(net|com)$",
        r"(ipinfo|ip)\.(io|sb)$",
        r"(edge\.api\.brightcove|videos-f\.jwpsrv|content\.jwplatform)\.(com|net)$"
    ]
}

def fetch_gfwlist(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64decode(response.content).decode('utf-8')
    else:
        raise Exception(f"Failed to fetch GFW list: {response.status_code}")

def process_gfwlist(gfwlist):
    processed_rules = ["/ip dns static"]
    for line in gfwlist.splitlines():
        if line.startswith('!') or not line.strip():
            continue
        
        domain = line[2:].strip('^') if line.startswith('||') else line
        matched_company = None
        
        for company, regex_list in COMPANY_REGEX_MAP.items():
            for regex in regex_list:
                if re.match(regex, domain):
                    matched_company = company
                    break
            if matched_company:
                break
        
        comment = matched_company if matched_company else "GFW"
        rule = f'add comment={comment} forward-to={DNS_FORWARD_IP} regexp="^{domain}$" type=FWD'
        processed_rules.append(rule)
    
    return "\n".join(processed_rules)

def save_rules(rules, filename):
    with open(filename, "w") as f:
        f.write(rules)

def main():
    try:
        gfwlist = fetch_gfwlist(GFWLIST_URL)
        processed_rules = process_gfwlist(gfwlist)
        save_rules(processed_rules, OUTPUT_FILE)
        print(f"Rules saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
