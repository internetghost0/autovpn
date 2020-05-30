from base64 import b64decode
import requests
import os
import time
import tempfile

URL = 'https://www.vpngate.net/api/iphone/'
DATABASE = 'vpn_configs'
TOR_PROXY = "127.0.0.1 9050"

def update(url=URL, file=DATABASE):
    print('Loading...')
    raw_data = requests.get(url).text.replace('\r','').split('\n')[2:]
    f = open(file, 'w')
    for line in raw_data:
        line = line.split(',')
        if(len(line) > 13):
            f.write("%s:%s\n" % (line[6],line[14]))
    f.close()
    print('Done.')
def delete(n=1, file=DATABASE):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    f = open(file,'w')
    for i in range(len(lines)):
        if n==(i+1): continue
        f.write(lines[i])
    f.close()

def info(file=DATABASE):
    f = open(file, 'r')
    data = f.readlines()
    f.close()
    info = dict()
    for line in data:
        if(line[:2] in info.keys()): info[line[:2]] += 1
        else: info[line[:2]] = 1
    print(time.ctime(os.path.getmtime(DATABASE)))
    print(sum(info.values()),'configs in db')
    print(info)

def connect(tor=False, file=DATABASE,verbose=True):
    config = tempfile.NamedTemporaryFile(delete=False)
    with open(file,'r') as f:
        data = f.readlines()[0]
        config.write(b64decode(data[3:]))
        if verbose: print('[*] Connecting to', data[:2],end=' ')
    config.close()
    if tor:
        if verbose: print('over tor')
        os.system('openvpn --socks-proxy %s --config %s' % (TOR_PROXY, config.name))
    else:
        if verbose: print()
        os.system('openvpn --config %s' % config.name)
    time.sleep(10)
    os.unlink(config.name)


def connect_c(country,tor=False,file=DATABASE,verbose=True):
    with open(file,'r') as f:
        data = f.readlines()
    config = tempfile.NamedTemporaryFile(delete=False)
    for line in data:
        if line[:2] == country:
            config.write(b64decode(line[3:]))
            config.close()
            break
    if tor:
        if verbose: print('connecting over tor')
        os.system('openvpn --socks-proxy %s --config %s' % (TOR_PROXY, config.name))
    else:
        os.system('openvpn --config %s' % config.name)
    time.sleep(10)
    os.unlink(config.name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--update', action='store_true',help='update database')
    parser.add_argument('-d','--delete',type=int,metavar='N' ,help='Delete N string in database')
    parser.add_argument('-i','--info', action='store_true',help='show information about database')
    parser.add_argument('-c','--country', metavar='[JP]')
    parser.add_argument('-t','--tor', action='store_true', help='use tor to connecting')
    args = parser.parse_args()
	
    if args.update:
        update()
        exit()
    if not os.path.isfile(DATABASE):
        print("Couldn't find a db, updating...")
        update()
    exitt = False
    if args.delete:
        delete(args.delete)
        exitt = True
    if args.info:
        info()
        exitt = True
    if exitt: exit()
    if args.country:
        connect_c(args.country,args.tor)
    else:
        connect(args.tor)
