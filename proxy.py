import socket
import socks
import requests
import configurations

class Proxy:
    def __init__(self):
        self.default_proxy_settings = socket.socket

    def set_default_proxy_settings(self, proxy=None):
        if proxy is not None:
            socks.setdefaultproxy(
                socks.PROXY_TYPE_SOCKS5,
                configurations.proxy['host'],
                configurations.proxy['port'],
                True,
                configurations.proxy['username'],
                configurations.proxy['password']
            )
        else:
            socket.socket = self.default_proxy_settings

    def check_proxy_connection(self, number_of_times):
        socks.setdefaultproxy(
            socks.PROXY_TYPE_SOCKS5,
            configurations.proxy['host'],
            configurations.proxy['port'],
            True,
            configurations.proxy['username'],
            configurations.proxy['password']
        )
        iteration = 1
        while iteration <= number_of_times:
            try:
                socket.socket = socks.socksocket
                response = requests.get('https://www.google.com')
                if response.status_code == 200:
                    self.set_default_proxy_settings()
                    self.change_proxy_ip()
                    return True
                else:
                    self.change_proxy_ip()
                    iteration += 1
            except requests.exceptions.RequestException as e:
                iteration += 1
        self.set_default_proxy_settings()
        return False

    def change_proxy_ip(self):
        self.set_default_proxy_settings()
        while True:
            try:
                response = requests.get(configurations.proxy['change_ip_link'], verify=False)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException as e:
                pass