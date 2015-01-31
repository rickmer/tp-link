#!/usr/bin/python
"""
TP-LINK M5350 connection tool
"""

from base64 import standard_b64encode
from urllib import quote
from urllib2 import build_opener, Request
from argparse import ArgumentParser
from getpass import getpass
from datetime import datetime

Class M5350Control(object):
    """
    TP-Link M5350 connector class
    """
    def __init__(self, passwd, host='192.168.0.1'):
        """
        M5350 connector constructor
        """
        self.passwd = passwd
        self.host = host
        encpasswd = standard_b64encode(':'.join(['admin', self.passwd]))
        self.headers = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:15.0) Gecko/20100101 Firefox/15.0.1'),
                        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                        ('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3'),
                        ('Accept-Encoding', 'gzip, deflate'),
                        ('DNT', '1')]
        self.cookies = [('Authorization', quote(' '.join(['Basic', encpasswd]))),
                        ('subType', 'pcSub'),
                        ('TPLoginTimes', '1')]

    def _http_get_parameter_(self, parameters):
        """
        Build get Parameters for a http get request
        """
        returnvalues = []
        for (key, value) in parameters:
            returnvalues.append('='.join([quote(key), quote(value)]))
        return '&'.join(returnvalues)

    def _send_request_(self, path, parameters):
        """
        send request
        """
        # Build url, get parameters and request
        getparameter = self._http_get_parameter_(parameters)
        request = Request(''.join(['http://', self.host, path, '?', getparameter]))

        # Build header
        headers = self.headers
        headers.append(('Referer', ''.join(['http://', self.host, path])))
        for (key, value) in headers:
            request.add_header(key, value) 
        # Build cookie store
        cookies = []
        for (key, value) in self.cookies:
            cookies.append('='.join([key, value]))
        opener = build_opener()
        opener.addheaders.append(('Cookie', '; '.join(cookies)))

        return opener.open(request)

    def send_sms(self, telnr, text):
        """
        send a send_sms request
        """

        if len(text) > 160:
            print ''.join(['message too long (', str(len(text)), ')'])

        now = datetime.now()
        timestring = ','.join([str(now.year),
                               str(now.month),
                               str(now.day),
                               str(now.hour),
                               str(now.minute),
                               str(now.second)])
        parameters = [('parent_path', ''),
                      ('sms_index', '0'),
                      ('numInputBoxId', telnr),
                      ('contentAreaId', text),
                      ('code_type', '0'),
                      ('sendBtnId', '1'),
                      ('sentTime', timestring)]

        return self._send_request_('/userRpm/smsSingle.htm', parameters)

    def connect(self, connect=True):
        """
        send a (dis)connect request
        """

        if connect:
            btn_id = 'connBtnId'
            btn_value = 'Connect'
        else:
            btn_value = 'Disconnect'
            btn_id = 'disConnBtnId'

        return self._send_request_('/userRpm/linkStatus.htm', [(btn_id, btn_value)])


def main():
    """
    CommandLine Innterface to M5350 connection tool
    """
    argpars = ArgumentParser(prog='TP-Link M5350 connection tool')
    argpars.add_argument('--host',  help='host', default='192.168.0.1')
    argpars.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    argpars.add_argument('-p', '--password', help='password')
    argpars.add_argument('action', nargs='+', help='connect, disconnect, sms')
    args = argpars.parse_args()
    if args.password is None:
        args.password = getpass()

    controller = M5350Control(args.password, args.host)
    if args.action[0].lower() == 'connect':
        controller.connect(True)
    elif args.action[0].lower() == 'disconnect':
        controller.connect(False)
    elif args.action[0].lower() == 'sms':
        if len(args.action) != 3:
            print 'usage: tp-link sms <telnr> <message>'
        else:
            controller.send_sms(args.action[1], args.action[2])
    else:
        print 'unknown action'
        exit(1)
if __name__ == "__main__":
    main()
