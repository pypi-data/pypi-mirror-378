import os
import requests
from rich.pretty import pprint as PP
import json
import turbocore


CL = None

class Client:

    def __init__(self):
        self._token = os.environ.get("AI_TOKEN", "TOKEN_MISSING")

    def simple(self, question, outfilename):
        data = {
          "model": "gpt-4o-mini",
          "input": question,
          "store": True
        }
        res = requests.post("https://api.openai.com/v1/responses", json=data, headers={"Content-Type":"application/json", "Authorization":"Bearer %s" % self._token})
        reso = res.json()

        with open(outfilename, "w") as f:
            f.write(json.dumps(reso, indent=4))

        try:
            with open(outfilename + ".plain", "w") as f:
                f.write(reso["output"][0]["content"][0]["text"])
        except (KeyError, IndexError):
            with open(outfilename + ".plain", "w") as f:
                f.write("error parsing response")

        print("done")


def init_globals():
    global CL
    CL = Client()


def ai_ask(QUESTION, OUTFILE):
    CL.simple(question=QUESTION, outfilename=OUTFILE)


def main():
    init_globals()
    turbocore.cli_this(__name__, "ai_")
