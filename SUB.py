import psutil
import requests
import socket
import os

MAIN_SERVER_URL = 'http://main_server_ip:5000'

def get_server_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage

def register_with_main_server():
    server_info = f"{socket.gethostname()}@{socket.gethostbyname(socket.gethostname())}"
    register_url = f'{MAIN_SERVER_URL}/register'
    data = {'server_info': server_info}
    response = requests.post(register_url, json=data)
    print(response.text)

def reboot_server(server_name):
    os.system('sudo shutdown -r now')

def send_usage_to_main_server(server_name, cpu_usage, ram_usage):
    url = f'{MAIN_SERVER_URL}/update_usage'
    data = {
        'server_name': server_name,
        'cpu_usage': cpu_usage,
        'ram_usage': ram_usage
    }
    response = requests.post(url, json=data)
    print(response.text)

if __name__ == '__main__':
    register_with_main_server()

    while True:
        server_name = socket.gethostname()
        cpu_usage, ram_usage = get_server_usage()
        send_usage_to_main_server(server_name, cpu_usage, ram_usage)
