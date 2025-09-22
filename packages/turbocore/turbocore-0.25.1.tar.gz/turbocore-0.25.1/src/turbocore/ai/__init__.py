import sys
import json
from rich.pretty import pprint as PP


def main():
    ofilename = sys.argv[2]
    filename = sys.argv[1]
    with open(ofilename, 'w') as of:
        data = None
        try:
            data = json.loads(open(filename, 'r').read())

            hosts_actual = []


            results = []

            for k in data["stats"].keys():
                hosts_actual.append(k)
                results.append([k])

            of.write("* Results\n")

            cols = data["stats"][hosts_actual[0]].keys()
            results.insert(0, ["", *cols])

            fresults = []
            import copy
            for row in results:
                if row[0] == "":
                    fresults.append(row)
                    continue
                frow = copy.deepcopy(row)
                h = frow[0]
                for col in cols:
                    marker1 = ""
                    marker2 = ""
                    if col == "ok":
                        marker1 = " ( "
                        marker2 = " ) "
                    frow.append(marker1 + str(data["stats"][h][col]) + marker2)
                fresults.append(frow)

            for row in fresults:
                of.write("| ")
                of.write(" | ".join(row))
                of.write(" |\n")



        except:
            pass
        print("lets look at ansible json output...")


        of.write("* Tasklog\n\n")

        for h in hosts_actual:
            of.write("** Tasks run on host =%s=\n\n" % h)

            for p in data["plays"]:
                play_file = p["play"]["path"].split("/")[-1]
                for t in p["tasks"]:
                    task_file = t["task"]["path"].split("/")[-1]
                    if h in t["hosts"].keys():
                        task_action = t["hosts"][h]["action"]
                        is_failed = False
                        if "failed" in t["hosts"][h].keys():
                            if t["hosts"][h]["failed"] == True:
                                is_failed = True
                        
                        fail_s = ""
                        if is_failed:
                            fail_s = "TODO "
                        of.write("*** %s=%s= / =%s= / =%s=\n\n" % (fail_s, play_file, task_file, task_action))

                        if is_failed:
                            of.write("#+begin_src \n")
                            if "msg" in t["hosts"][h].keys():
                                of.write("%s\n" % (t["hosts"][h]["msg"]).strip())
                            of.write("#+end_src\n")


        #PP(data)
