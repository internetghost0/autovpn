# autovpn
script to save vpn confing from [vpngate.net](https://www.vpngate.net/) to your local machine and automatically connect to them 

# usage
'''
usage: autovpn.py [-h] [-i [N]] [-c [JP]] [-u] [-l] [-d] [-t] [--info]

options:
  -h, --help            show this help message and exit
  -i [N], --index [N]   choose Nth element (index=0 default)
  -c [JP], --country [JP]
                        choose country (country=any default)
  -u, --update          update database
  -l, --lookup          return index of [country] at Nth [index] or if country=any, prints whats country at [index]
  -d, --delete          delete Nth element in database (use --index)
  -t, --tor             connect to vpn-server through TOR proxy
  --info                show information about database
'''

# install
$ git clone https://github.com/internetghost0/autovpn


# errors: 
if you have the error `OPTIONS ERROR: failed to negotiate cipher with server.  Add the server's cipher ('AES-128-CBC') to --data-ciphers`, then change `IS_UNSAFE_CIPHER` to `True`
