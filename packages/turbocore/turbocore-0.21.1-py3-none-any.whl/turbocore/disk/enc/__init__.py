from turbocore import cli_this
import subprocess
import os


def enc_new(NAME, MB, K):
    diskfile = "%s.img" % NAME
    kfile = "/tmp/tc-disk-enc-K-tmp"
    devfile = "%s.dev" % NAME
    dd_res = subprocess.check_output("""/bin/bash -c 'dd if=/dev/zero of=%s bs=1M count=%d; exit 0' 2>&1""" % (diskfile, int(MB)), shell=True, universal_newlines=True)
    with open(kfile, 'w') as f:
        f.write(K)
    losetup_res = subprocess.check_output("""/bin/bash -c 'losetup --find --show %s' 2>&1""" % (diskfile), shell=True, universal_newlines=True).strip().split("\n")[0].strip()
    with open(devfile, 'w') as f:
        f.write(losetup_res)

    luksFormat_res = subprocess.check_output("""/bin/bash -c 'cryptsetup luksFormat %s %s' 2>&1""" % (losetup_res, kfile), shell=True, universal_newlines=True, input="YES")
    luksOpen_res = subprocess.check_output("""/bin/bash -c 'cryptsetup luksOpen %s %s --key-file=%s' 2>&1""" % (losetup_res, NAME, kfile), shell=True, universal_newlines=True)
    os.unlink(kfile)
    mkfsext4_res = subprocess.check_output("""/bin/bash -c 'mkfs.ext4 /dev/mapper/%s' 2>&1""" % (NAME), shell=True, universal_newlines=True)
    os.makedirs(NAME, exist_ok=True)
    mount_res = subprocess.check_output("""/bin/bash -c 'mount /dev/mapper/%s %s' 2>&1""" % (NAME, NAME), shell=True, universal_newlines=True)


def enc_open(NAME, K):
    diskfile = "%s.img" % NAME
    kfile = "/tmp/tc-disk-enc-K-tmp"
    devfile = "%s.dev" % NAME
    losetup_res = subprocess.check_output("""/bin/bash -c 'losetup --find --show %s' 2>&1""" % (diskfile), shell=True, universal_newlines=True).strip().split("\n")[0].strip()
    with open(kfile, 'w') as f:
        f.write(K)
    with open(devfile, 'w') as f:
        f.write(losetup_res)
    luksOpen_res = subprocess.check_output("""/bin/bash -c 'cryptsetup luksOpen %s %s --key-file=%s' 2>&1""" % (losetup_res, NAME, kfile), shell=True, universal_newlines=True)
    os.unlink(kfile)
    mount_res = subprocess.check_output("""/bin/bash -c 'mount /dev/mapper/%s %s' 2>&1""" % (NAME, NAME), shell=True, universal_newlines=True)
    # visual confirmation
    subprocess.call("""/bin/bash -c 'ls -al %s' 2>&1""" % NAME, shell=True)
    subprocess.call("""/bin/bash -c '( cd %s && df -h . )' 2>&1""" % NAME, shell=True)


def enc_close(NAME):
    devfile = "%s.dev" % NAME
    dev_actual = ""
    umount_res = subprocess.check_output("""/bin/bash -c 'umount /dev/mapper/%s' 2>&1""" % (NAME), shell=True, universal_newlines=True)
    print(umount_res)
    luksClose_res = subprocess.check_output("""/bin/bash -c 'cryptsetup luksClose %s' 2>&1""" % (NAME), shell=True, universal_newlines=True)
    print(luksClose_res)
    with open(devfile, 'r') as f:
        dev_actual = f.read().split("\n")[0].strip()
    losetup_detach_res = subprocess.check_output("""/bin/bash -c 'losetup -d %s' 2>&1""" % (dev_actual), shell=True, universal_newlines=True)
    # visual confirmation
    subprocess.call("""/bin/bash -c 'losetup -a' 2>&1""", shell=True)


def enc_help():
    print("""How it works:
          
python -m turbocore.disk.enc help
python -m turbocore.disk.enc new   NAME MB K
python -m turbocore.disk.enc open  NAME K
python -m turbocore.disk.enc close NAME
""")


def main():
    cli_this(__name__, 'enc_')
