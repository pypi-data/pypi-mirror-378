from rich.pretty import pprint as PP
import os
import os.path
import turbocore
import subprocess
import json


class NoBolt:

    def __init__(self):
        self._gnupghome = os.path.expanduser(os.environ.get("GNUPGHOME", "~/.gnupg"))
        self._nobolt = os.path.expanduser(os.environ.get("NOBOLT", "~/.nobolt"))
        self._id = self._gpg_usable_secret_keys()
        self._me = self._id[0]
        if len(self._id) > 1:
            self._me = os.environ.get("NOBOLT_ME", "")
            if self._me == "":
                raise Exception("Too many secret keys available, set keyID with NOBOLT_ME")


    def _exist(self):
        if not os.path.isfile(self._nobolt):
            emptydb = {
                "items": []
            }
            with open(self._nobolt, 'w') as f:
                f.write(self._gpg_enc(json.dumps(emptydb, indent=4)))


    def update(self, data):
        self._exist()
        pass


    def _gpg_enc(self, src) -> str:
        o = subprocess.check_output(
            "GNUPGHOME=%s gpg --encrypt --sign --armor --recipient %s --local-user %s --trust-model always" % (self._gnupghome, self._me, self._me),
            shell=True,
            universal_newlines=True,
            input=src
        ).strip()
        return o

    def _gpg_verify(self, src) -> str:
        #gpg --decrypt .nobolt 2>&1 1>/dev/null
        #"GNUPGHOME=%s gpg --status-fd 1 --decrypt >/dev/null" % (self._gnupghome),
        lines = subprocess.check_output(
            "GNUPGHOME=%s gpg --decrypt 2>&1 1>/dev/null" % (self._gnupghome),
            shell=True,
            universal_newlines=True,
            input=src
        ).strip().split("\n")

        pre_line = ""
        for line in lines:
            if line.upper().startswith("GPG: GOOD SIGNATURE FROM "):
                keyid = pre_line.strip().split(" ")[-1].upper()
                return keyid
            pre_line = line

        return ""


    def _gpg_dec(self, src) -> str:
        o = subprocess.check_output(
            "GNUPGHOME=%s gpg --decrypt" % (self._gnupghome),
            shell=True,
            universal_newlines=True,
            input=src
        ).strip()
        return o


    def _gpg_usable_secret_keys(self):
        o_all = subprocess.check_output(
            "GNUPGHOME=%s gpg -K --with-colons" % self._gnupghome,
            shell=True,
            universal_newlines=True
        ).strip().split("\n")
        
        o2 = [l for l in o_all if l.startswith("uid:u:") or l.startswith("sec:u:")]

        o = [ f"{a}:{b}" for a,b in zip(o2[::2], o2[1::2]) ]
        res = []
        for oo in o:
            ocols = oo.split(":")
            keyid = ocols[4]
            mailetc = ocols[30]
            res.append(keyid.upper())

        return res


def cli_test():
    NB = NoBolt()
    NB.update(None)


def cli_test2():
    NB = NoBolt()
    txt = open(NB._nobolt, 'r').read()
    y = NB._gpg_verify(txt)
    print("signed with: [%s]" % y)


def main():
    turbocore.cli_this(__name__, 'cli_')
