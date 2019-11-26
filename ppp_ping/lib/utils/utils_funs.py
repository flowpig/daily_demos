# -*- coding: utf-8 -*- 
from os import walk
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

COMMASPACE = ', '


def parse_uri(uri):
    """
    Parses an  URL like, 'protocol://user@host:22' and returns a tuple of:
    (user, host, port, password)
    
    NOTE: *password* may be None
    """
    if uri is None:
        return None
    url = uri.encode('ascii', 'ignore')
    scheme_split = "://"
    index = url.find(scheme_split)
    if index < 0:
        return url, None, None, None, None
    protocol_len = index + len(scheme_split)
    protocol = url[:index].lower()
    password = None
    if '@' in url: # user@host[:port]
        host = url.rsplit('@',1)[1].split(':')[0]
        user = url.rsplit('@',1)[0][protocol_len:]
        if ':' in user: # Password was included (not secure but it could be useful)
            password = user.split(':')[1]
            user = user.split(':')[0]
        if len(url.rsplit('@',1)[1].split(':')) == 1: # No port given, assume 22
            if protocol.lower() == 'snmp':
                port = '161'
            elif protocol.lower() == 'telnet':
                port = '23'
            else:
                port = '22'
        else:
            port = url.rsplit('@',1)[1].split(':')[1]
    else: # Just host[:port] (assume $USER)
        user = None
        url = url[protocol_len:] # Remove the protocol
        host = url.split(':')[0]
        if len(url.split(':')) == 2: # There's a port #
            port = url.split(':')[1]
        else:
            port = '22'
    return protocol, host, user, password, port


def ls_files(path):
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        f.extend(filenames)
        break
    return f


