import requests
import copy
import json
from rich.pretty import pprint as PP


# https://dns.hetzner.com/api-docs/


class Client:


    def __init__(self, token):
        self._token = token
        self._apihost = 'https://dns.hetzner.com' #'/api/v1/zones'
        self._hdr = {'Auth-API-Token': self._token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        self._zone_ids = {} # mappings from dns name to ID


    def test(self):
        for zone in self._zones():
            print(zone["name"])


    def _api_get(self, route):
        res = requests.get(self._apihost + route, headers=self._hdr)
        reso = res.json()
        return reso

    def _api_del(self, route):
        res = requests.delete(self._apihost + route, headers=self._hdr)
        reso = res.json()
        return reso

    def _api_post(self, route, jsondata_string):
        res = requests.post(self._apihost + route, data=jsondata_string, headers=self._hdr)
        reso = res.json()
        return reso


    def add_record_a(self, domain, name, addr4):
        self._zones()
        zone_id = self._zone_ids[domain]
        data = {
            "value": addr4,
            "ttl": 7200,
            "type": "A",
            "name": name,
            "zone_id": zone_id
        }
        reso = self._api_post(route='/api/v1/records', jsondata_string=json.dumps(data))
        PP(reso)

    def add_record_txt(self, domain, name, text):
        self._zones()
        zone_id = self._zone_ids[domain]
        data = {
            "value": text,
            "ttl": 7200,
            "type": "TXT",
            "name": name,
            "zone_id": zone_id
        }
        reso = self._api_post(route='/api/v1/records', jsondata_string=json.dumps(data))
        PP(reso)


    def rm(self, fqdn:str):
        zones = self._zones()
        for zone in zones:
            if fqdn.endswith("." + zone["name"]):
                localpart = fqdn[:fqdn.find(zone["name"])-1]
                print("Trying to delete record [%s]" % localpart)
                all_zone_records = self._zonerecords(zone_id=self._zone_ids[zone["name"]])
                todel = []
                for r in all_zone_records:
                    if r["name"] == localpart:
                        todel.append(r["id"])
                        reso = self._api_del(route='/api/v1/records/%s' % r["id"])
                        PP(reso)

                PP(todel)

                return


    def _zonerecords(self, zone_id:str):
        reso = self._api_get(route='/api/v1/records?zone_id=%s' % zone_id)["records"]
        return reso


    def _zones(self):
        reso = self._api_get(route='/api/v1/zones')
        cpage = reso["meta"]["pagination"]["page"]
        npage = reso["meta"]["pagination"]["next_page"]
        if not (cpage == 1 and cpage == npage):
            raise Exception("Soo many domains, pagination not implemented yet.")
        zones = reso["zones"]
        self._zone_ids = {}
        for zone in zones:
            self._zone_ids[zone["name"]] = zone["id"]
        return zones
