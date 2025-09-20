import os
import subprocess


def main():
    """TARGET_SSH_HOST=blog vp -m turbocore.xdebug.tools.forward"""
    host = os.environ.get("TARGET_SSH_HOST", "")
    print("Using env TARGET_SSH_HOST=%s to locally catch 11 ports 9000-9010" % host)
    subprocess.call("""ssh -R 127.0.0.1:9000:127.0.0.1:9000 -R 127.0.0.1:9001:127.0.0.1:9001 -R 127.0.0.1:9002:127.0.0.1:9002 -R 127.0.0.1:9003:127.0.0.1:9003 -R 127.0.0.1:9004:127.0.0.1:9004 -R 127.0.0.1:9005:127.0.0.1:9005 -R 127.0.0.1:9006:127.0.0.1:9006 -R 127.0.0.1:9007:127.0.0.1:9007 -R 127.0.0.1:9008:127.0.0.1:9008 -R 127.0.0.1:9009:127.0.0.1:9009 -R 127.0.0.1:9010:127.0.0.1:9010 %s""" % host, shell=True)
