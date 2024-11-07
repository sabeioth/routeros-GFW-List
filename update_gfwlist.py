import requests
import re

# 下载 gfw.txt 文件
url = 'https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/gfw.txt'
response = requests.get(url)

if response.status_code == 200:
    # 将响应内容保存到 gfwlist.rsc 文件
    with open('gfwlist.rsc', 'w') as f:
        f.write(response.text)
    
    # 将响应内容分割成列表
    domains = response.text.splitlines()
    
    # 创建输出文件 dns.rsc
    with open('dns.rsc', 'w') as f:
        for domain in domains:
            if domain and not domain.startswith('#'):  # 跳过注释行和空行
                # 对域名进行正则表达式转义
                escaped_domain = re.escape(domain)
                # 确保正则表达式字符串正确格式化
                f.write(f'/ip dns static\n')
                f.write(f'add forward-to=198.18.0.1 regexp=\\\n')
                f.write(f'    "{escaped_domain}" type=FWD\n')
    
    print("gfwlist.rsc 和 dns.rsc 文件已创建。")
else:
    print("无法从服务器下载 gfw.txt。")
