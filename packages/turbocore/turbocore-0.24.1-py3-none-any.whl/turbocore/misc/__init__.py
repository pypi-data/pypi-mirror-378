import time
import os
import socket


class NameCache4:

    def __init__(self, filename=None):
        if filename != None:
            self._filename = filename
        else:
            self._filename = "/tmp/name-cache-%s.tsv" % int(time.time())
        self.load()

    def load(self):
        self._address_to_name = {}
        self._name_to_address = {}
        if os.path.isfile(self._filename):
            with open(self._filename, 'r') as f:
                for line in f:
                    if line.strip() == "":
                        continue
                    else:
                        cols = line.strip().split("\t")
                        if len(cols) >= 2:
                            self._address_to_name[cols[0]] = cols[1]
                            self._name_to_address[cols[1]] = cols[0]
                        else:
                            self._address_to_name[cols[0]] = ""

    def save(self):
        with open(self._filename, 'w') as f:
            for ip in self._address_to_name.keys():
                        f.write("%s\t%s\n" % (ip, self._address_to_name[ip]))

    def get_name(self, ip):
        if not ip in self._address_to_name.keys():
            try:
                h, al, ad = socket.gethostbyaddr(ip)
                self._address_to_name[ip] = h
                self._name_to_address[h] = ip
            except:
                self._address_to_name[ip] = ""
                self._name_to_address[""] = ip
        return self._address_to_name[ip]
              
