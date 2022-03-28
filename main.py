from smb.SMBConnection import SMBConnection
import config
import subprocess
import socket


servers = ['10-file-srv', '36-file-srv', '10-sqltest-vsrv']

patch=config.patch

userID = config.username
password = config.password
client_machine_name = 'localpcname'

# Создает папку "share" в папке "server", по пути "home"
def mkdir(server='', share=''):
    cmd = f"""mkdir -p '{patch}/{server}/{share}'"""
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Монтирует сетевой диск "server" в папку "share"
def mount(server='', share=''):
    credentials=config.credentials
    cmd = f"""sudo mount -t cifs -o vers=2.0,sec=ntlmssp,credentials={credentials},uid=1000,gid=1000 '//{server}/{share}' '{patch}/{server}/{share}'"""
    # print(cmd)
    r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.communicate()[0].decode('utf-8')



for server in servers:      # Перебираем список серверов
    # Получаем обьект коннекта к самбе
    smb_conn = SMBConnection(
        userID,
        password,
        client_machine_name,
        f'''{server}.{config.domain}''',
        domain=config.domain,
        use_ntlm_v2=True,
        is_direct_tcp=True
    )

    
    server_ip = socket.gethostbyname(server)    # Для подключения к самбе нужен ip адрес сервера, получаем его:
    smb_conn.connect(server_ip, 445)            # Подключаемя к самбе


    shares = smb_conn.listShares()              # Список шар на сервере
    for share in shares:
        if not share.isSpecial and share.name not in ['NETLOGON', 'SYSVOL']:
            share_name = share.name
            # print(share_name.replace(' ', '\ '))
            mkdir(server=server, share=share_name)  # Создаем папку шары
            mount(server=server, share=share_name)  # Монтируем шару
    smb_conn.close()