#!/usr/bin/python
"""
TP-LINK M5350 connection tool
"""

from base64 import standard_b64encode
from urllib import quote
from urllib2 import build_opener, Request
from argparse import ArgumentParser
from getpass import getpass

class M5350Control(object):
    """
    TP-Link M5350 connector class
    """
    def __init__(self, passwd, host='192.168.0.1'):
        """
        M5350 connector constructor
        """
        self.passwd = passwd
        self.host = host

    def http_get_parameter(self, parameters):
        """
        Build get Parameters for a http get request
        """
        returnvalues = []
        for (key, value) in parameters:
            returnvalues.append('='.join([quote(key), quote(value)]))
        return '&'.join(returnvalues)

    def connect(self, connect=True):
        """
        Make a Connect Request
        """

        if connect:
            btn_id = 'connBtnId'
            btn_value = 'Connect'
        else:
            btn_value = 'Disconnect'
            btn_id = 'disConnBtnId'

        getparameter = self.http_get_parameter([(btn_id, btn_value)])
        encpasswd = standard_b64encode(':'.join(['admin', self.passwd]))
        headers = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:15.0) Gecko/20100101 Firefox/15.0.1'),
                   ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                   ('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3'),
                   ('Accept-Encoding', 'gzip, deflate'),
                   ('DNT', '1'),
                   ('Referer', ''.join(['http://', self.host, '/userRpm/linkStatus.htm']))]
        cookielist =  [('Authorization', quote(' '.join(['Basic', encpasswd]))),
                    ('subType', 'pcSub'),
                    ('TPLoginTimes', '1')]
        opener = build_opener()
        request = Request(''.join(['http://', self.host, '/userRpm/linkStatus.htm', '?', getparameter]))
        for (key, value) in headers:
            request.add_header(key, value)
        cookies = []
        for (key, value) in cookielist:
            cookies.append('='.join([key, value]))
        opener.addheaders.append(('Cookie', '; '.join(cookies)))
        return opener.open(request)


def main():
    """
    CommandLine Innterface to M5350 connection tool
    """
    argpars = ArgumentParser(prog='TP-Link M5350 connection tool')
    argpars.add_argument('--host',  help='host', default='192.168.0.1')
    argpars.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    argpars.add_argument('-p', '--password', help='password')
    argpars.add_argument('action', help='connect, disconnect')
    args = argpars.parse_args()
    if args.password is None:
        args.password = getpass()

    connector = M5350Control(args.password, args.host)
    if args.action.lower() == 'connect':
        connector.connect(True)
    elif args.action.lower() == 'disconnect':
        connector.connect(False)
    else:
        print 'unknown action'
        exit(1)
if __name__ == "__main__":
    main()
