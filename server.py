import paramiko
import socket
import threading
import subprocess

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # В данном примере разрешаем аутентификацию любым паролем
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        # В данном примере разрешаем все запросы на открытие канала
        return paramiko.OPEN_SUCCEEDED

    def check_channel_exec_request(self, channel, command):
        # Выполняем команду и отправляем вывод обратно клиенту
        output = subprocess.check_output(command, shell=True)
        channel.sendall(output)
        channel.shutdown(1)

def run_ssh_server():
    host_key = paramiko.RSAKey(filename='host_key.pem')
    server = SSHServer()

    ssh_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssh_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssh_socket.bind(('0.0.0.0', 22))
    ssh_socket.listen(5)
    print('[+] SSH server is running')

    while True:
        client_socket, client_address = ssh_socket.accept()
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(host_key)

        try:
            transport.start_server(server=server)
        except paramiko.SSHException as ex:
            print(f'[!] SSH negotiation failed: {str(ex)}')
            continue

        channel = transport.accept(20)
        if channel is None:
            transport.close()
            continue

        server.event.wait(10)
        if not server.event.is_set():
            channel.close()
            transport.close()
            continue

        server.event.clear()
        channel.close()

if __name__ == '__main__':
    run_ssh_server()
