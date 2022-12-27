#!/usr/bin/env python3
# TODO: Add comments

from base64 import b64decode
from hashlib import md5
import requests
import os
import time
import tempfile
import argparse
import subprocess

URL = 'https://www.vpngate.net/api/iphone/'
DATABASE = 'vpn_configs.db'
TOR_PROXY = "127.0.0.1 9050"

# if you have an error `OPTIONS ERROR: failed to negotiate cipher with server.  Add the server's cipher ('AES-128-CBC') to --data-ciphers`
IS_UNSAFE_CIPHER = True
UNSAFE_CIPHER_CMD = ['--data-ciphers', 'AES-128-CBC']

def md5hash(msg):
    return md5(msg.encode()).hexdigest()

def update(url=URL, file=DATABASE):
    print('Connecting to ...', URL)
    raw_data = requests.get(url).text.replace('\r','').split('\n')[2:]
    f = open(file, 'w')
    for line in raw_data:
        line = line.split(',')
        if(len(line) > 13):
            f.write("%s:%s\n" % (line[6],line[14]))
    f.close()
    print('Done.')
def delete(index=0, file=DATABASE):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    f = open(file,'w')
    for i in range(len(lines)):
        if index==i: continue
        f.write(lines[i])
    f.close()

def info(file=DATABASE, verbose=True):
    f = open(file, 'r')
    data = f.readlines()
    f.close()
    info = dict()
    for line in data:
        if(line[:2] in info.keys()): info[line[:2]] += 1
        else: info[line[:2]] = 1
    if verbose:
        print(time.ctime(os.path.getmtime(DATABASE)))
        print(sum(info.values()),'configs in db')
        print(info)
    return info

def lookup(index, country, file=DATABASE):
    if not country:
        country = 'any'
    i = 0
    idx_in_db = 0
    print('[*] Lookup to a config-vpn in country `%s` at index `%s` in db...' % (country, index))
    with open(file,'r') as f:
        data = f.readlines()
    for line in data:
        if (country == 'any') or (line[:2] == country):
            if index == i:
                print('COUNTRY:', line[:2])
                print('INDEX:', idx_in_db)
                return idx_in_db
            i += 1
        idx_in_db += 1
    print('ERROR: index is out of range')

def connect(index, tor=False, country=None, file=DATABASE,verbose=True):
    config = tempfile.NamedTemporaryFile(delete=False)
    if country == None:
        with open(file,'r') as f:
            data = f.readlines()
            if len(data) <= index:
                print('ERROR: index out of range')
                exit()
            data = data[index]
            config.write(b64decode(data[3:]))
            if verbose: print(f'[*] Connecting to `{data[:2]}` hash({md5hash(data[3:])})')
        config.close()
    else:
        print(country)
        i = 0
        is_config_found  = False
        with open(file,'r') as f:
            data = f.readlines()
        for line in data:
            if line[:2] == country:
                # if you specify `country` + `index`
                if i >= index:
                    print(f'[*] Connecting to specific `{country}` hash({md5hash(line[3:])})')
                    config.write(b64decode(line[3:]))
                    config.close()
                    is_config_found = True
                    break
                i += 1
        if not is_config_found:
            print('\nERROR: index is out of range')
            exit()

    openvpn_cmd = ['openvpn','--config', config.name]
    if IS_UNSAFE_CIPHER:
        openvpn_cmd += UNSAFE_CIPHER_CMD
    if tor:
        openvpn_cmd += ['--socks-proxy', TOR_PROXY]
        if verbose: print('over tor\n')

    # Execute openvpn
    execute(openvpn_cmd)
    os.unlink(config.name)

def execute(cmd):
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='') # process line here

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, ' '.join(p.args))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--index', type=int, metavar='N', nargs='?', const=0, help=' choose Nth element (index=0 default)')
    parser.add_argument('-c','--country', metavar='[JP]', help='choose country (country=any default)')
    parser.add_argument('-u','--update', action='store_true', help='update database')
    parser.add_argument('-l','--lookup', action='store_true', help='return index of [country] at Nth [index] or if country=any, prints whats country at [index]')
    parser.add_argument('-d','--delete', action='store_true', help='delete Nth element in database (use --index)') 
    parser.add_argument('-t','--tor', action='store_true', help='connect to vpn-server through TOR proxy')
    parser.add_argument('--info', action='store_true', help='show information about database')
    args = parser.parse_args()

    if args.index == None:
        args.index = 0
	
    if args.update:
        update()
        exit()
    exitt = False
    if args.delete:
        delete(index=args.index) 
        exitt = True 
    if args.lookup:
        inf = info(verbose=False)
        print(sum(inf.values()),'configs in db')
        print(inf)
        print()
        lookup(index=args.index, country=args.country)
        exitt = True
    if args.info:
        info()
        exitt = True
    if exitt: 
        exit()
    else:
        print('[0] No args are provide, trying to connect...')
        print('(hint: autovpn.py --help)')
        if not os.path.isfile(DATABASE):
            print("Couldn't find a db, updating...")
            update()
        i = 0
        while True:
            try:
                connect(index=args.index, country=args.country, tor=args.tor)
            except Exception as e:
                print('ERROR:', e)
            finally:
                i += 1
                print()
                choice = input(f'[{i}] Continue? [Y/n]: ')
                if choice in ['n', 'N']:
                    break
                else:
                    args.index += 1
                    continue
