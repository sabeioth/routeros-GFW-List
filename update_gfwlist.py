import base64
import requests

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

# 生成 .rsc 文件内容
def generate_rsc_content(decoded_content):
    rsc_content = "/ip dns static\n"
    
    def add_rule(comment, domain_pattern):
        nonlocal rsc_content
        rsc_content += f'add comment="{comment}" forward-to=198.18.0.1 regexp="{domain_pattern}" type=FWD\n'
    
    for line in decoded_content.splitlines():
        if line and not line.startswith('!') and not line.startswith('@@'):
            # 假设每行都是一个需要添加到 DNS 静态记录中的域名模式
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
        
        # 生成并保存转换后的 dns.rsc 文件
        rsc_content = generate_rsc_content(decoded_content)
        write_rsc_file(rsc_content, 'dns.rsc')
        
        print("转换完成，已生成 gfwlist.rsc 和 dns.rsc 文件。")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
