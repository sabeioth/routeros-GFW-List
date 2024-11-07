import base64
import requests
import re

def fetch_gfwlist():
    # GitHub 上 GFWList 的 raw 链接
    url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception('Failed to download gfwlist')

def decode_base64(data):
    # 解码 Base64 数据
    return base64.b64decode(data).decode('utf-8')

def convert_to_routeros_format(data, forward_to):
    lines = data.splitlines()
    output = ['ip dns static']
    for line in lines:
        # 注释直接跳过
        if line == '' or line.startswith('!') or line.startswith('@@') or line.startswith('[AutoProxy'):
            continue

        # 清除前缀
        line = re.sub(r'^\|?https?://', '', line)
        line = re.sub(r'^\|\|', '', line)
        line = line.lstrip('.*')

        # 清除后缀
        line = line.rstrip('/^*')

        # 替换 . 为 \\. 并添加正则表达式格式
        line = line.replace('.', '\\.')

        # 确保生成的正则表达式有效
        if line:
            # 对于 IP 地址，直接匹配整个 IP 地址
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', line):
                output.append(f'add regexp="^{line}$" forward-to={forward_to} type=FWD')
            else:
                # 对于域名，使用 ^.*\.domain\.tld$ 格式
                output.append(f'add regexp="^.*\\.{line}$" forward-to={forward_to} type=FWD')
    return '\n'.join(output)

def main():
    # 前向 DNS 地址，根据实际情况修改
    gfwdns = '198.18.0.1'  # 修改为您的 DNS 服务器地址
    
    # 获取并解码 GFWList
    gfwlist_data = fetch_gfwlist()
    decoded_data = decode_base64(gfwlist_data)
    
    # 将数据转换为 RouterOS 格式
    routeros_data = convert_to_routeros_format(decoded_data, gfwdns)
    
    # 写入 gfwlist.rsc 和 dns.rsc 文件
    with open('gfwlist.rsc', 'w') as f:
        f.write(decoded_data)
    
    with open('dns.rsc', 'w') as f:
        f.write(routeros_data)

if __name__ == '__main__':
    main()
