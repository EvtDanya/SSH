import paramiko
import time
import argparse
import getpass
import select

class Validation:
    '''
    Class for args validation
    '''
    @staticmethod
    def validate_num(count):
        if not count or int(count) <= 0:
            raise argparse.ArgumentTypeError('Port number must be a positive (> 0)!')
        return int(count)
    
def parse_args() -> argparse.Namespace:
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser(
        description='SSH client by d00m_r34p3r',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=56)
    )
    parser.add_argument( 
        '-ip', '--ip-address',
        type=str,
        required=True,
        help='hostname or ip address to connect to'
    )
    parser.add_argument( 
        '-p', '--port',
        type=Validation.validate_num,
        default=22,
        help='port number'
    )
    parser.add_argument( 
        '-u', '--username',
        type=str,
        required=True,
        help='username'
    )
    parser.add_argument( 
        '-k', '--key',
        type=str,
        help='path to secret key file'
    )   
         
    return parser.parse_args()

def receive_output(session):
    '''
    Get output from connection
    '''
    while True:
        if session.recv_ready():
            output = session.recv(1024).decode()
            print(output, end='')
        elif session.recv_stderr_ready():
            stderr = session.recv_stderr(1024).decode()
            print(stderr, end='')
        else:
            channel = session.fileno()
            r, _, _ = select.select([channel], [], [], 0.1)
            if channel in r:
                continue
            else:
                break

def ssh_client(hostname, port, username, password=None, key_path=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if key_path:
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(hostname, port=port, username=username, pkey=private_key)
        else:
            client.connect(hostname, port=port, username=username, password=password)

        session = client.get_transport().open_session()
        session.invoke_shell()
        session.set_combine_stderr(True)
        
        session.send('')
        receive_output(session)
        
        while True:
            command = input(f'{username}# ')
            session.send(command + '\n')
            
            receive_output(session)
            
    except KeyboardInterrupt:
        print('\n[i] Quitting...')
    except Exception as e:
        print(f'[!] {e}')
        
    finally:
        client.close()
        
if __name__ == '__main__':   
    args = parse_args()
    
    if not args.key:
        password = getpass.getpass()
        
    ssh_client(args.ip_address, args.port, args.username, password, args.key)