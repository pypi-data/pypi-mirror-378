import os
import subprocess
from rich.pretty import pprint as PP


def main():
    """TARGET_SSH_HOST=blog vp -m turbocore.xdebug.tools.serverconfig"""
    host = os.environ.get("TARGET_SSH_HOST", "")
    etc_issue_net = subprocess.check_output("ssh %s 'cat /etc/issue.net; exit 0' 2>/dev/null" % host, shell=True, universal_newlines=True).split("\n")[0].strip().lower()

    cfg = {}

    if etc_issue_net.startswith("ubuntu 24") and etc_issue_net.endswith("lts"):
        cfg['host'] = host
        cfg['os'] = 'lts24'
        cfg['xdebug.ini'] = '/etc/php/8.3/apache2/conf.d/20-xdebug.ini'
        cfg['pkgs'] = ['apache2', 'libapache2-mod-php', 'php-xdebug']
        run(cfg)


def run(cfg:dict):
    print("running")
    PP(cfg)