import turbocore
import json
from hcloud import Client
from .dns import Client as DNSClient
import os
import os.path
import sys
import time
import requests
import rich
from rich.pretty import pprint as PP
import datetime
import subprocess


g_token = None
g_token_ns = None


g_client = None
g_client_ns = None
g_ini = None

def load_clients():
    global g_client
    global g_client_ns
    global g_token
    global g_token_ns
    global g_ini
    g_ini = turbocore.UserIni()

    g_token = os.environ.get("HZ_TOKEN", "")
    if g_token != "":
        g_client = Client(token=g_token)
    g_token_ns = os.environ.get("HZ_TOKEN_NS", "")
    if g_token_ns != "":
        g_client_ns = DNSClient(token=g_token_ns)

    if g_client is None and g_client_ns is None:
        raise Exception("No Clients initalized")


def hz_mv(OLD_NAME, NEW_NAME):
    load_clients()
    servers = g_client.servers.get_all()
    for server in servers:
        if server.name == OLD_NAME:
            server.update(NEW_NAME)
            return
    print("no such server")


def hz_ssh(NAME):
    load_clients()
    servers = g_client.servers.get_all()
    for server in servers:
        if server.name == NAME:
            ip4 = server.public_net.ipv4.ip
            cmd = g_ini.gets("hz", "rootsshcmd", "")
            print(cmd)
            subprocess.call("%s %s" % (cmd, ip4), shell=True)
            return
    print("no such server")


def hz_rebuild(NAME):
    """Run installation with profile image.
    """
    load_clients()

    vmid = _vm_id(NAME)
    server = g_client.servers.get_by_id(vmid)
    server.rebuild(image=server.image)


def hz_rdns(NAME):
    load_clients()
    vmid = _vm_id(NAME)
    server = g_client.servers.get_by_id(vmid)
    ip4 = str(server.public_net.primary_ipv4.ip)
    ip6 = str(server.public_net.primary_ipv6.ip)
    import ipaddress
    addr6 = ipaddress.IPv6Network(ip6)
    addr61 = addr6.network_address+1
    print("%s" % (addr61.exploded))
    
    #server.change_dns_ptr(ip4, "mail4.anycx.de")
    server.change_dns_ptr(addr61.exploded, "mail6.anycx.de")
    server.update()



def hz_new(NAME, TYPE):
    """Create new droplet with NAME by .ini template hz::vm.
    for example:
    
    [hz]
    vm=location:nbg1,type:cx22,firewall:firewall-1,os:24.04:x86,ssh:hetz
    """
    load_clients()
    if TYPE == "":
        TYPE = "vm"
    defaults = g_ini.gets("hz", TYPE)
    if defaults != "":
        props = defaults.split(",")
        kv = {}
        for p in props:
            cols = p.split(":")
            kv[cols[0]] = cols[1:]

        _quick_new(
            new_system_name=NAME,
            ssh_match=kv["ssh"][0],
            firewall_match=kv["firewall"][0],
            location_match=kv["location"][0],
            type_match=kv["type"][0],
            sys_name_match=kv["os"][0],
            sys_arch_match=kv["os"][1]
        )


def hz_fw(SUBCMD):
    load_clients()
    all_firewalls = g_client.firewalls.get_all()
    
    if SUBCMD == "help":
        print("ls")
        print("lsfw")


    if SUBCMD == "ls":
        for fw in all_firewalls:
            print(fw.name)
            for res in fw.applied_to:
                if res.type == "server":
                    print(" -> %s" % res.server.name)


    if SUBCMD == "lsfw":
        for fw in all_firewalls:
            print(fw.name)
            for fwrule in fw.rules:
                print(fwrule.direction, fwrule.protocol, "/", fwrule.port, ", ".join(fwrule.source_ips))
                print()
            # for res in fw.applied_to:
            #     if res.type == "server":
            #         print(" -> %s" % res.server.name)



    # for fw in allfw:
    #     print(str(fw.id) + "/" + fw.name)
    #     PP(fw.rules)
    #     print("*"*80)
    #servers = g_client.servers.get_all()




def hz_ip4():
    load_clients()
    servers = g_client.servers.get_all()
    res = []
    for server in servers:
        i = "%d" % server.id
        n = server.name
        ip4 = server.public_net.ipv4.ip
        row = [n, i, ip4]
        res.append(row)
    # sort lowercase first column = name
    res = sorted(res, key=lambda x: x[0].lower())
    for row in res:
        print("\t".join(row))


def _vm_id(name):
    servers = g_client.servers.get_all()
    for server in servers:
        if server.name == name:
            return server.id
    raise Exception("No such VM with name %s found" % name)


def _vm_names():
    servers = g_client.servers.get_all()
    res = []
    for server in servers:
        n = server.name
        res.append(n)
    res = list(sorted(res))
    return res


def hz_ls():
    load_clients()
    for row in _vm_names():
        print(row)


def hz_rm(NAME):
    load_clients()
    all_servers = g_client.servers.get_all()
    
    # selected_servers = turbocore.InteractiveListing(
    #     q="Servers to delete",
    #     choices=all_servers,
    #     detail_field_names=[
    #         "id",
    #         "name"
    #         ]
    #     ).ui_select(multi=True)


    for s in all_servers:
        if s.name == NAME:
            print("will delete %s" % NAME)
            s.delete()
            print("done")
            return
    
    print("no such server")
    # for s in selected_servers:
    #     s.delete()



def hz_lb():
    load_clients()
    lbs = g_client.load_balancers.get_all()
    res = []
    for lb in lbs:
        PP(lb)
        break


def _image_find(needle="ubuntu"):
    all_matches = [ img for img in g_client.images.get_list(type="system", per_page=50).images if needle.lower() in img.name.lower()]
    for img in all_matches:
        print(img.id)
        print(img.name)
        print(img.architecture)
        print()


def _quick_new(new_system_name, ssh_match, firewall_match, location_match, type_match, sys_name_match, sys_arch_match):
    all_keys = g_client.ssh_keys.get_all()
    selected_sshkeys = turbocore.InteractiveListing(
        q="SSH Public Key Selection",
        choices=all_keys,
        detail_field_names=[
            "id",
            "fingerprint",
            "name"
            ]
        ).ui_select(multi=True, default_pre_contains={"name": ssh_match}, auto_select=True)

    all_firewalls = g_client.firewalls.get_all()
    selected_firewalls = turbocore.InteractiveListing(
        q="Firewall Selection",
        choices=all_firewalls,
        detail_field_names=[
            "id",
            "name"
            ]
        ).ui_select(multi=True, default_pre_contains={"name": firewall_match}, auto_select=True)


    all_locations = g_client.locations.get_all() # nbg1
    selected_locations1 = turbocore.InteractiveListing(
        q="Location Selection (only one)",
        choices=all_locations,
        detail_field_names=[
            "id",
            "name"
            ]
        ).ui_select(multi=False, default_pre_contains={"name": location_match}, auto_select=True)

    all_types = g_client.server_types.get_all() # cx22
    selected_types1 = turbocore.InteractiveListing(
        q="Machine Type Selection (only one, mini-shared=cx22 mini-dedicated=ccx13)",
        choices=all_types,
        detail_field_names=[
            "id",
            "name"
            ]
        ).ui_select(multi=False, default_pre_contains={"name": type_match}, auto_select=True)

    all_images = [ img for img in g_client.images.get_list(type="system", per_page=50).images if "ubuntu".lower() in img.name.lower()]
    selected_images1 = turbocore.InteractiveListing(
        q="Machine Type Selection (only one)",
        choices=all_images,
        detail_field_names=[
            "id",
            "architecture",
            "name"
            ]
        ).ui_select(multi=False, default_pre_contains={"name": sys_name_match, "architecture": sys_arch_match}, auto_select=True)

    print()
    print("Summary")

    # new_system_name
    # selected_sshkeys
    # selected_firewalls
    # selected_locations1
    # selected_types1
    # selected_images1

    try:
        create_server_res = g_client.servers.create(
            name=new_system_name,
            image=selected_images1[0],
            ssh_keys=selected_sshkeys,
            server_type=selected_types1[0],
            firewalls=selected_firewalls,
            location=selected_locations1[0]
        )
        #PP(create_server_res)
        if create_server_res.server == None:
            raise Exception("No server object in response")

        s = create_server_res.server
        print(s.id)
        print(s.name)
        print(s.public_net.ipv4.ip)

    except Exception as e:
        print("Failed")
        print(e)


def hz_lbdo():
    data = json.loads(subprocess.check_output("/bin/bash -c 'doctl compute load-balancer list -o json'", shell=True, universal_newlines=True))
    PP(data)


def hz_ip4do():
    data = json.loads(subprocess.check_output("/bin/bash -c 'doctl compute droplet list -o json'", shell=True, universal_newlines=True))
    #PP(data)
    res = []
    for server in data:
        i = "%d" % server["id"]
        n = server["name"]
        v4nets = server["networks"]["v4"]
        ip4 = ""
        for v4net in v4nets:
            if v4net["type"] == "public":
                ip4 = v4net["ip_address"]
        row = [n, i, ip4]
        res.append(row)
    res = sorted(res, key=lambda x: x[0].lower())
    for row in res:
        print("\t".join(row))


def hz_dns(SUBCMD):
    load_clients()
    if SUBCMD == "ls":
        g_client_ns.test()

def hz_dnsa(NAME, DOMAIN, ADDR4):
    load_clients()
    g_client_ns.add_record_a(DOMAIN, NAME, ADDR4)


def hz_dnstxt(NAME, DOMAIN, TEXT):
    load_clients()
    g_client_ns.add_record_txt(DOMAIN, NAME, TEXT)


def hz_dnsrm(FQDN):
    load_clients()
    print("will try to delete %s" % FQDN)
    g_client_ns.rm(fqdn=FQDN)


def hz_keys():
    load_clients()
    all_keys = g_client.ssh_keys.get_all()
    for k in all_keys:
        print(k.id)
        print(k.name)
        print(k.fingerprint)
        print("--")


def hz_snapshot(VM, NAME):
    load_clients()
    all_servers = g_client.servers.get_all()
    for s in all_servers:
        if VM == s.name:
            print(s.name)
            res = s.create_image(NAME)
            PP(res)
            print(res)


def hz_on(VM):
    load_clients()
    all_servers = g_client.servers.get_all()
    for s in all_servers:
        if VM == s.name:
            print(s.status)
            s.power_on()
            print(s.status)

def hz_off(VM):
    load_clients()
    all_servers = g_client.servers.get_all()
    for s in all_servers:
        if VM == s.name:
            print(s.status)
            s.power_off()
            print(s.status)


def hz_example():
    print("""~/tc.ini

[hz]
vm=location:nbg1,type:cx22,firewall:firewall-1,os:24.04:x86,ssh:hetz
""")

def main():
    turbocore.cli_this(__name__, "hz_")
