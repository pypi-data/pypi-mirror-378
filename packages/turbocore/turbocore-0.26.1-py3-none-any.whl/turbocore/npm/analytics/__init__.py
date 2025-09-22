import sys
import turbocore
import json
import requests
from rich.pretty import pprint as PP
import os
import os.path

CACHE_DIR = os.environ.get("TC_NPM_VCACHE_DIR", "/tmp/turbocore-version-cache")
CACHE_DIR_VERSIONS = os.path.join(CACHE_DIR, "VERSIONS")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(CACHE_DIR_VERSIONS, exist_ok=True)


def npmgraph_url(q):
    return "https://npmgraph.js.org/?q=%s" % q


def npma_versions(NAME):
    x = requests.get("https://registry.npmjs.org/%s" % NAME).json()
    with open(os.path.join(CACHE_DIR_VERSIONS, "NPMVERSION.%s.ALL" % NAME), 'w') as out:
        out.write(json.dumps(x, indent=4))


def npma_latest(NAME):
    x = requests.get("https://registry.npmjs.org/%s/latest" % NAME).json()
    with open(os.path.join(CACHE_DIR_VERSIONS, "NPMVERSION.%s.LATEST" % NAME), 'w') as out:
        out.write(json.dumps(x, indent=4))



def npma_full(PACKAGEJSON, PACKAGELOCKJSON):
    """Read package.json and package-lock.json and calc all dependencies.
    """
    pass


def npma_info(PACKAGEJSON):
    src = None
    with open(PACKAGEJSON, 'r') as f:
        src = f.read()
    package_json = json.loads(src)
    deps = package_json.get("dependencies", {})
    dev_deps = package_json.get("devDependencies", {})

    named_deps = list(sorted(deps.keys()))
    named_dev_deps = list(sorted(dev_deps.keys()))

    print("DEPS")
    print(npmgraph_url(",".join(named_deps)))
    print()
    print("DEV-DEPS")
    print(npmgraph_url(",".join(named_dev_deps)))
    print()


def main():
    turbocore.cli_this(__name__, 'npma_')
