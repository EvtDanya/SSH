import paramiko
import getpass

def create_ssh_connection(ip, port, user, passwd):
    client = paramiko.SSHClient()
    # client.load_host_keys("/home/user/.ssh/known_host")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    return client

def execute_commands(client, user):
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        while True:
            cmd = input(f'{user}$ ')
            if not cmd:
                break
            elif cmd.lower() == 'exit':
                break
            ssh_session.exec_command(cmd)
            output = ssh_session.recv(1024).decode('utf-8')
            print(output, end='')
    client.close()
    
if __name__ ==  '__main__':
    user = input('Username: ')
    passwd = getpass.getpass()
    
    ip = input('Enter server IP: ') or '192.168.0.1'
    port = int(input('Enter server port: ') or 22)
    
    client = create_ssh_connection(ip, port, user, passwd)
    execute_commands(client, user)