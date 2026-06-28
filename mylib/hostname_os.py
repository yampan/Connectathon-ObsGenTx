import socket
import platform
import os
import sys

def get_hostname(deb=0):
    hostname = socket.gethostname()
    if deb:
        print("Hostname:", hostname)
    return hostname

def get_os(deb=0):
    os_name = platform.system()
    
    # Windows, Linux, Darwin
    if deb:
        #print("OS:", os_name)
        if os_name == "Windows":
            print("os: Windows")
        elif os_name == "Linux":
            print("os: Linux")
        elif os_name == "Darwin":
            print("os: macOS")
    return os_name

def get_local_ip_address():
    """     自ホストのローカルIPアドレスを取得します。    """
    try:
        # 一時的なソケットを作成し、外部に接続することで自身のIPアドレスを取得
        # 実際に接続は行われません
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # GoogleのDNSサーバーに接続を試みる（外部へのルーティングパスを得るため）
        ip_address = s.getsockname()[0]
        s.close()
        print(f"IPアドレス: {ip_address}")
        return ip_address
    except Exception as e:
        print(f"ローカルIPアドレスの取得中にエラーが発生しました: {e}")
    return None 


def get_env(deb=0):
    script_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)
    print(f"スクリプトのパス: {script_dir}")
    print(f"スクリプト名: {script_name}")
    env = {"host": get_hostname()}
    env["ip"] = get_local_ip_address()
    env["os"] = get_os()
    env["script_path"] = script_path
    env["script_dir"] = script_dir
    env["script_name"] = script_name
    return env

# ---------
if __name__ == '__main__':
    get_hostname(1)
    get_os(1)
    print(get_env())
"""
Hostname: X1Pro
これは Windows です
スクリプトのパス: c:\home\github\my-IHE-client\mylib
スクリプト名: hostname_os.py
{'host': 'X1Pro', 'ip': '192.168.16.31', 'os': 'Windows', 
'script_path': 'c:\\home\\github\\my-IHE-client\\mylib\\hostname_os.py', 
'script_dir': 'c:\\home\\github\\my-IHE-client\\mylib', '
script_name': 'hostname_os.py'}
(my-ihe-client) PS C:\home> 
"""