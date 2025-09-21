import datetime
import xler8
import hashlib
import urllib.parse
import turbocore
import requests
import sys
import textwrap
import json
import time
from rich.pretty import pprint as PP
import sqlite3
import os
import os.path


g_DBCX = None
g_SETUP_SQL3 = []

# for i in range(0, 10):
#     g_DBCX.execute("INSERT INTO info (col1, col2) VALUES (?, ?)", ("txt%d" % i, i))
# g_DBCX.commit()


# scols = ["col1", "col2"]
# for row in cx.execute("SELECT %s from info WHERE col1 LIKE ? LIMIT 3" % ",".join(scols), ('t%',)):
#     data = dict(zip(scols, row))
#     PP(data)



def db_up():
    global g_DBCX
    dbfilename = "data.sql3"

    if not os.path.isdir("issues"):
        os.makedirs("issues")

    # if os.path.isfile(dbfilename):
    #     os.unlink(dbfilename)

    if not os.path.isfile(dbfilename):
        cx = sqlite3.connect(dbfilename)
        for line in g_SETUP_SQL3:
            cx.execute(line)
        cx.commit()
        cx.close()

    g_DBCX = sqlite3.connect(dbfilename)


def db_down():
    g_DBCX.commit()
    g_DBCX.close()



def debug_object(src):
    if os.environ.get("DEBUG", "") != "":
        filename = "debug-%d-%d.json" % (int(time.time()), time.time_ns())
        with open(filename, 'w') as f:
            f.write(json.dumps(src, indent=4))


def sha256file(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(8192*4), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def get_base_url():
    host = get_base_host()
    return "https://%s" % host


def get_base_host():
    host = os.environ.get("TJI_HOST")
    return host


def get_token():
    token = os.environ.get("TJI_TOKEN")
    return token


def get_user():
    token = os.environ.get("TJI_USER")
    return token


def req(verb, route, data=None, stream=False) -> requests.Response:
    
    if not route.startswith("/") and not route.startswith("http://") and not route.startswith("https://"):
        raise Exception("parameter 'route' must start with a '/'")

    f_ = {
        "GET": requests.get,
        "POST": requests.post,
    }

    if not verb.upper() in f_.keys():
        raise Exception("Unsupported http verb '%s'" % verb)

    hdr = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    #    "Authorization": "Bearer %s" % get_token()

    auth=(get_user(), get_token())
    url = get_base_url() + route
    
    # special case we have a full url
    if not route.startswith("/"):
        url = route

    url_host_actual = url.split("//")[1].split("/")[0].split(":")[0]
    if url_host_actual is None or url_host_actual == "" or url_host_actual != get_base_host():
        raise Exception("Unsafe host in API call detected, %s" % str(url_host_actual))
    
    #res = f_[verb](url=url, headers=hdr, data=data)
    res = f_[verb](url=url, headers=hdr, data=data, auth=auth)
    return res


def ji_test():
    """test function.
    """
    print("test it is")

    res = req(verb="GET", route="/rest/api/3/myself")
    x = res.json()
    PP(x)
    sys.exit(0)


def apiget(src):
    res = req(verb="GET", route=src)
    return res.json()


def apistream(src, local_filename):
    res = req(verb="GET", route=src, stream=True)
    with open(local_filename, "wb") as f:
        for chunk in res.iter_content(chunk_size=8192*8):
            f.write(chunk)


def project_key():
    the_key = ""
    if os.path.isfile(".key"):
        with open(".key", "r") as f:
            the_key = f.read().split("\n")[0].strip()
            return the_key
    else:
        the_key = os.getcwd().split(os.sep)[-1]
    print("project context is [%s]" % the_key)
    return the_key


def compat_alpha_num(src: str) -> str:
    alpha = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    res = ""
    for i in range(0, len(src)):
        c = src[i]
        if c in alpha:
            res += c
    while "  " in res:
        res = res.replace("  ", " ")
    return res.strip()


def parse_adf(doc_node):
    if isinstance(doc_node, dict):
        if doc_node.get("type") == "text":
            return doc_node.get("text", "")
        elif doc_node.get("type") == "mention":
            return doc_node.get("attrs", {}).get("text", "")
        elif "content" in doc_node:
            calbr = ""
            if doc_node.get("type") == "paragraph":
                calbr = "\n"
            return "".join(parse_adf(child) for child in doc_node["content"]) + calbr
    elif isinstance(doc_node, list):
        return "\n".join(parse_adf(child) for child in doc_node)
    return ""


def ji_customs():
    res = req(verb="GET", route="/rest/api/2/field")
    reso = res.json()
    data = [ ["id", "name", "type"] ]
    for field in reso:
        if field["custom"] == True:
            field_id = field["id"]
            field_name = field["name"]
            field_type = field["schema"]["type"]
            data.append([field_id, field_name, field_type])
    xler8.xlsx_out(filename="customs.xlsx", sheets={
        "sheet1": {
            "data": data,
            "cw": xler8.cw_gen(data)
        }
    })

    sep = ","
    with open("customs.csv", "w") as f:
        for row in data:
            f.write(sep.join(row))
            f.write("\n")


# def ji_issue_data(issue_key):
#     res = req(verb="GET", route="/rest/api/3/issue/%s?fields=description,attachment,fields.comment" % issue_key)
#     reso = res.json()
#     desc_adf = reso["fields"].get("description", {})
#     txt = parse_adf(desc_adf)
#     wrapper = textwrap.TextWrapper(width=64, break_long_words=False, break_on_hyphens=False, replace_whitespace=False)
#     print("\n".join(wrapper.wrap(txt)))
#     print("-"*80)
#     #PP(reso["fields"]["attachment"])
#     atti=0
#     for att in reso["fields"]["attachment"]:
#         atti+=1
#         att_content = att["content"]
#         att_filename = att["filename"]
#         att_mime = att["mimeType"]
#         att_size = int(att["size"])
#         att_who = compat_alpha_num(att["author"]["displayName"])

#         print(att_content)
#         print(att_filename)
#         print(att_mime)
#         print(att_size)
#         print(att_who)
#         filename = "attach-%d" % atti
#         apistream(att_content, filename)
#         print(sha256file(filename))

#     sys.exit(0)


def ji_todo():
    db_up()

    select_cols = ["issue_key", "ts"]
    for row in g_DBCX.execute("SELECT %s from changes_todo" % ",".join(select_cols)):
        data = dict(zip(select_cols, row))
        PP(data)
        dump_issue(safe_issue_key(data["issue_key"]))
        dump_issuelinks(safe_issue_key(data["issue_key"]))
        time.sleep(0.5)
    db_down()


def safe_issue_key(src):
    res = ""
    for c in src:
        if c in "abcdefghijklmnopqrstuvwxyz-1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            res += c
        else:
            raise Exception("invalid character [%s] in issue_key [%s]" % (c, src))
    if res == "":
        raise Exception("unable to safe parse reasonable issue key, is empty")
    return res


def dump_issuelinks(issue_key):
    res = req(verb="GET", route="/rest/api/2/issue/%s?fields=issuelinks" % issue_key)
    reso = res.json()
    os.makedirs(os.path.join("issues", issue_key), exist_ok=True)

    filename_links = os.path.join("issues", issue_key, "LINKS.json")
    with open(filename_links, 'w') as f:
        f.write(json.dumps(reso, indent=4))

    related = []
    #if reso["fields"]["issuelinks"].keys():
    for issuelink in reso["fields"]["issuelinks"]:
        if "inwardIssue" in issuelink.keys():
            related.append(safe_issue_key(issuelink["inwardIssue"]["key"]))
        if "outwardIssue" in issuelink.keys():
            related.append(safe_issue_key(issuelink["outwardIssue"]["key"]))

    related = list(sorted(related))

    filename_issues = os.path.join("issues", issue_key, "ISSUES")
    with open(filename_issues, 'w') as f:
        for r in related:
            f.write("%s\n" % r)

def dump_issue(issue_key):
    res = req(verb="GET", route="/rest/api/3/issue/%s?fields=summary,description,attachment,comment,reporter,status,assignee" % issue_key)
    reso = res.json()

    desc_adf = reso["fields"].get("description", {})
    txt = parse_adf(desc_adf)
    wrapper = textwrap.TextWrapper(width=64, break_long_words=False, break_on_hyphens=False, replace_whitespace=False)
    
    os.makedirs(os.path.join("issues", issue_key), exist_ok=True)

    filename_desc = os.path.join("issues", issue_key, "DESC")
    with open(filename_desc, 'w') as f:
        f.write("\n".join(wrapper.wrap(txt)))

    filename_summary = os.path.join("issues", issue_key, "SUMMARY")
    with open(filename_summary, 'w') as f:
        f.write(reso["fields"]["summary"])

    filename_reporter = os.path.join("issues", issue_key, "REPORTER")
    with open(filename_reporter, 'w') as f:
        f.write(reso["fields"]["reporter"]["displayName"])

    filename_assignee = os.path.join("issues", issue_key, "ASSIGNEE")
    with open(filename_assignee, 'w') as f:
        try:
            f.write(reso["fields"]["assignee"]["displayName"])
        except:
            f.write("not-assigned")

    filename_status = os.path.join("issues", issue_key, "STATUS")
    with open(filename_status, 'w') as f:
        f.write(reso["fields"]["status"]["name"])

    filename_comments = os.path.join("issues", issue_key, "COMMENTS")
    with open(filename_comments, 'w') as f:
        comments=[]
        try:
            comments = reso["fields"]["comment"]["comments"]
        except:
            comments=[]
        for comment in comments:
            body = parse_adf(comment["body"])
            author = comment["author"]["displayName"]
            created = comment["created"]
            f.write("%s %s\n%s\n\n" % (created, author, body))

    filename_debug = os.path.join("issues", issue_key, "debug.json")
    with open(filename_debug, 'w') as f:
        f.write(json.dumps(reso, indent=4))

    #PP(reso["fields"]["attachment"])
    atti=0
    for att in reso["fields"]["attachment"]:
        atti+=1
        att_content = att["content"]
        att_filename = att["filename"]
        att_mime = att["mimeType"]
        att_size = int(att["size"])
        att_who = compat_alpha_num(att["author"]["displayName"])

        # print(att_content)
        # print(att_filename)
        # print(att_mime)
        # print(att_size)
        # print(att_who)
        # filename = "attach-%d" % atti
        # apistream(att_content, filename)
        # print(sha256file(filename))




def ji_changes(minutes_back):
    db_up()
    minutes = int(minutes_back)
    proj = project_key()
    res = req(verb="GET", route="/rest/api/3/search?maxResults=250&jql=" + urllib.parse.quote('created >= -%dm and project = %s' % (minutes, proj)))
    x = res.json()
    tsnow = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%S+0000")


    for iss in x["issues"]:
        i_k = safe_issue_key(iss["key"])
        issue_dir = os.path.join("issues", i_k)
        os.makedirs(issue_dir, exist_ok=True)

        # filename_issue_summary = os.path.join(issue_dir, "SUMMARY")
        # i_summary = iss["fields"]["summary"]
        # with open(filename_issue_summary, 'w') as f:
        #     f.write(i_summary)

        i_self = iss["self"]
        i_labels = iss["fields"]["labels"]
        i_status = iss["fields"]["status"]["name"]
        i_type = iss["fields"]["issuetype"]["name"]
        i_browse = get_base_url() + "/browse/" + i_k

        g_DBCX.execute("INSERT INTO changes_todo(issue_key, ts) VALUES (?, ?)", (i_k, tsnow))

        # print(i_k)
        # print(i_self)
        # print(i_labels)
        # print(i_summary)
        # print(i_status)
        # print(i_type)
        # print(i_browse)
        # print("--")
    
    add_manual = os.environ.get("ISSUE", "")
    if add_manual != "":
        g_DBCX.execute("INSERT INTO changes_todo(issue_key, ts) VALUES (?, ?)", (add_manual, tsnow))

    g_DBCX.commit()
    db_down()


# def ji_status(status, project):
#     res = req(verb="GET", route="/rest/api/3/search?maxResults=250&jql=" + urllib.parse.quote('project = "%s" and status = "%s"' % (project, status)))
#     x = res.json()
#     debug_object(x)
#     for iss in x["issues"]:
#         i_k = iss["key"]
#         i_self = iss["self"]
#         i_labels = iss["fields"]["labels"]
#         i_summary = iss["fields"]["summary"]
#         i_status = iss["fields"]["status"]["name"]
#         i_type = iss["fields"]["issuetype"]["name"]
#         i_browse = get_base_url() + "/browse/" + i_k

#         print(i_k)
#         print(i_self)
#         print(i_labels)
#         print(i_summary)
#         print(i_status)
#         print(i_type)
#         print(i_browse)
#         print("--")


# def ji_dev():
#     """test dev function.
#     """
#     proj = project_key()
#     last_int_hours = 48
#     res = req(verb="GET", route="/rest/api/3/search?maxResults=250&jql=" + urllib.parse.quote('created >= -%dh and project = %s' % (last_int_hours, proj)))
#     x = res.json()
#     PP(x)

#     sys.exit(0)


def main():
    global g_SETUP_SQL3
    g_SETUP_SQL3 = [
        "CREATE TABLE changes_todo (id INTEGER PRIMARY KEY, issue_key TEXT, ts TEXT)"
    ]
    #    "CREATE TABLE changes (id INTEGER PRIMARY KEY, issue_key TEXT, issue_summary TEXT)"
    turbocore.cli_this(__name__, 'ji_')
    return
