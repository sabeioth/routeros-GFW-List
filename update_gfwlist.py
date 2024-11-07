import requests
import base64

# 下载 gfwlist.txt 文件
url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
response = requests.get(url)

if response.status_code == 200:
    # 解码 Base64 编码的内容
    content = base64.b64decode(response.content).decode('utf-8')
    
    # 将响应内容保存到 gfwlist.rsc 文件
    with open('gfwlist.rsc', 'w') as f:
        f.write(content)
    
    # 将响应内容分割成列表
    lines = content.splitlines()
    
    # 过滤和清理域名
    domains = []
    for line in lines:
        if line.startswith('!') or line.startswith('@@') or line.startswith('[AutoProxy'):
            continue  # 跳过注释行、例外规则和配置行
        if line.strip():
            # 移除常见的前缀和后缀
            line = line.replace('||', '').replace('http://', '').replace('https://', '').replace('^', '').strip('/')
            domains.append(line)
    
    # 创建输出文件 dns.rsc
    with open('dns.rsc', 'w') as f:
        f.write('/ip dns static\n')
        for domain in domains:
            if domain:  # 确保域名不是空字符串
                # 写入 RouterOS 兼容的命令
                f.write(f'add forward-to=198.18.0.1 regexp="{domain}" type=FWD\n')
    
    print("gfwlist.rsc 和 dns.rsc 文件已创建。")
else:
    print("无法从服务器下载 gfwlist.txt。")
