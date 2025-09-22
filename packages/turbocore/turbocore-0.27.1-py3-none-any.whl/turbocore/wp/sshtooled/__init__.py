import json
import subprocess
import base64


__wpbasecmd = "WP "


def __run_ssh(host, bash_cmd, stdinstr=None):
    if stdinstr is None:
        x = subprocess.check_output("""ssh -q %s '/bin/bash -c "%s 2>/dev/null ; exit 0"'""" % (host, bash_cmd), shell=True, universal_newlines=True).strip()
        return x
    else:
        x = subprocess.check_output("""ssh -q %s '/bin/bash -c "%s 2>/dev/null ; exit 0"'""" % (host, bash_cmd), shell=True, universal_newlines=True, input=stdinstr).strip()
        return x


def run_ssh_sudo_stdout(host:str, bash_cmd:str):
    bash_cmd_base64 = base64.b64encode(bash_cmd.encode()).decode()
    x = subprocess.check_output("""ssh %s 'sudo -u root /bin/bash -c "echo -n %s | base64 -d | bash 2>/dev/null ; exit 0"'""" % (host, bash_cmd_base64), shell=True, universal_newlines=True)
    return x


def get_option(host, option_name):
    return __run_ssh(host, __wpbasecmd + "option get %s" % option_name)


def get_option_as_json(host, option_name):
    return json.loads(__run_ssh(host, __wpbasecmd + "option get %s --format=json" % option_name))


def get_mysql_tsv(host, sqluser, sqlpw, dbname, sqlcode):
    common_opts = "--batch"
    if sqlpw is None or sqlpw == "":
        return __run_ssh(host, "mysql %s -u %s %s" % (common_opts, sqluser, dbname), sqlcode)
    else:
        return __run_ssh(host, "mysql %s -u %s -p --password=%s %s" % (common_opts, sqluser, sqlpw, dbname), sqlcode)
