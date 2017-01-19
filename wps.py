#!/usr/bin/python
import os
import subprocess
import time
import bap_com

def display(msg=None, reset=False):
    fp.show(msg)
    time.sleep(2)
    if reset:
        fp.reset()

def get_ssids(scan):
    ssids = []
    #print 'TEST:' + scan
    try:
        lines = scan.split('\n')
        n = len(lines)
        #print 'Num of lines: ' + str(n)
        if n <= 2:
            return -1
        #print lines
        i = 0
        for l in lines:
            #print 'line ' + str(i) + ' ' + repr(l)
            _ = l.split()
            if _ == []:
                #print 'Empty line.'
                pass
            elif i > 1:
                #print _
                ssids.append(_[-1])
            i += 1
        #print 'num of ssids: ' + str(len(ssids))
        #for ssid in ssids:
        #    print ssid
        return ssids
    except Exception as e:
        print 'Failed get_ssids()'
        return -1

def shell_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print err
        return -1
    else:
        #print out
        return out

def scan():
    cmd = ['wpa_cli', 'scan_results']
    resp = shell_cmd(cmd)
    if resp == -1:
        return -1
    else:
        #print resp
        return resp

def wps_connect(ssid):
    cmd = ['wpa_cli', 'wps_pbc', ssid]
    resp = shell_cmd(cmd)
    if resp == -1:
        return -1
    else:
        print repr(resp)
        return 0

if __name__ == "__main__":
    fp = bap_com.FrontPanel()
    display('wps')
    scan_res = scan()
    if scan_res == -1:
        display('scan error', True)

    ssids = get_ssids(scan_res)
    if ssids == -1:
        display('ssid error', True)

    i = 1
    of = '/home/pi/websocketserver/scan_results.txt'
    with open(of, 'w') as f:
        for ssid in ssids:
            f.write(ssid + '\n')
            display(ssid + ' - ' + str(i))

    resp = 0
    magic_ssid = 'xxx' #'bohmeraudio'
    if magic_ssid in ssids:
        display('Connecting...')        
        resp = wps_connect(magic_ssid)
        if resp == -1:
            display('Failed.')
        else:
            display('Connected')
            display('Restarting')
            os.system('reboot')

    display('Finished')
    display('Start AP')
    time.sleep(1)
    os.system('halt')

