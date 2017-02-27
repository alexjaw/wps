#!/usr/bin/python
import os
import subprocess
import time

class fake_fp:
    def show(self, msg):
        print('fake_fp: ' + msg)

    def reset(self):
        self.show('done')

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

def _scan():
    cmd = ['wpa_cli', 'scan']
    resp = shell_cmd(cmd)
    if resp == -1:
        return -1
    else:
        return 0

def scan():
    # First scan
    # Then get results
    resp = _scan()
    if resp == -1:
        return -1

    # Ok, get results
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

def halt():
    if not is_fake_fp:
        os.system('halt')

def reboot():
    if not is_fake_fp:
        os.system('reboot')

if __name__ == "__main__":
    curr_dir = os.getcwd()
    fname = 'scan_results.txt'
    of = os.path.join(curr_dir, fname)
    try:
        import bap_com
        fp = bap_com.FrontPanel()
        is_fake_fp = False
    except Exception as e:
        print 'Using fake fp'
        fp = fake_fp()
        is_fake_fp = True

    display('wps')
    scan_res = scan()
    if scan_res == -1:
        display('scan error', True)
        exit(1)

    ssids = get_ssids(scan_res)
    if ssids == -1:
        display('ssid error', True)
        exit(1)

    i = 1
    with open(of, 'w') as f:
        for ssid in ssids:
            f.write(ssid + '\n')
            display(ssid + ' - ' + str(i))
            i+=1

    resp = 0
    magic_ssid = 'dont check' #'bohmeraudio'
    if magic_ssid in ssids:
        display('Connecting...')        
        resp = wps_connect(magic_ssid)
        if resp == -1:
            display('Failed.')
        else:
            display('Connected')
            display('Restarting')
            reboot()

    display('Finished')
    display('Start AP')
    time.sleep(1)
    halt()
