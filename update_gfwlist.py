import base64
import requests

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
        if not line or line.startswith('!'):
            continue
        # 替换 . 为 \\. 并添加正则表达式格式
        line = line.replace('.', '\\.')
        output.append(f'add regexp=".*\\.{line}\$" forward-to={forward_to} type=FWD')
    return '\n'.join(output)

def main():
    # 前向 DNS 地址，根据实际情况修改
    gfwdns = '8.8.8.8'  # 这里填写您希望使用的DNS服务器地址
    
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
