import os
import sys
import inspect
import site
import configparser


class UserIni:

    def __init__(self):
        self._filename = os.path.expanduser("~/tc.ini")
        self._ini = configparser.ConfigParser()
        if os.path.isfile(self._filename):
            self._ini.read(self._filename)

    def gets(self, section, key, default="") -> str:
        if section in self._ini.sections():
            return str(self._ini.get(section=section, option=key))
        else:
            return ""

class InteractiveListing:

    def __init__(self, q, choices=[], id_field_name="id", detail_field_names=[]):
        self._q = " ".join(q)
        self._info = ["  q:abort", "  s:return-selection (or a single SPACE)", "  N:toggle-option-N (multiple possible with SPACES)", "  0:clear-all"]
        self._choices = choices
        self._indexed = []
        self._selected = [] # only index
        self._detail_field_names = detail_field_names
        for item in choices:
            self._indexed.append(item)

    
    def ui_select(self, multi=False, field=None, default_pre_contains=None, auto_select=False):
        self._selected = []
        if type(default_pre_contains) == dict:
            for i in range(0, len(self._indexed)):
                x = self._indexed[i]
                matchcount = 0

                for k in list(default_pre_contains.keys()):
                    v = str(default_pre_contains[k]).lower()
                    if v in str(getattr(x, k)).lower():
                        matchcount+=1

                if matchcount == len(list(default_pre_contains.keys())):
                    self._selected = [i]
                    if multi == False:
                        break

        while True:
            self.show_all()
            x = None
            
            if not auto_select:
                x = input("> ")
            else:
                if len(self._selected) > 0:
                    x = "s"
                else:
                    auto_select = False
            
            if x == "s" or x == " ":
                res = None
                if field is None:
                    res = [ self._indexed[y] for y in self._selected ]
                else:
                    res = [ getattr(self._indexed[y], field) for y in self._selected ]
                return res
            if x == "q":
                return []

            if x == "0":
                self._selected = []
                continue

            #check for numbers
            numbers_ = x.split(" ")
            numbers = []
            for n in numbers_:
                try:
                    n_number = int(n)
                    numbers.append(n_number-1)
                except:
                    pass

            for n in numbers:
                if n in self._selected:
                    self._selected.remove(n)
                else:
                    if multi == False:
                        self._selected = []
                    self._selected.append(n)


    def show_all(self):
        print()
        print()
        print("-"*len(self._q))
        print(self._q)
        print("-"*len(self._q))
        print()
        for info in self._info:
            print(info)
        print()
        for i in range(0, len(self._indexed)):
            
            details = [ x + ":" + str(getattr(self._indexed[i], x)) for x in self._detail_field_names ]
            si = "   " # selection indicator
            if i in self._selected:
                si = " * "
            print(si, (i+1), " ".join(details))
        print()


def this_sitepackages():
    print(site.getusersitepackages())
    print(sys.path)


def this_platform():
    if sys.platform.upper().startswith("DARWIN"):
        return "m"
    if sys.platform.upper().startswith("WIN32"):
        return "w"
    if sys.platform.upper().startswith("LINUX"):
        return "l"
    return "u"


def cli_this(module_name, f_prefix="", build_manual=False):

    program_name = sys.argv[0].split(os.sep)[-1]
    all_f_map = {}
    for m,o in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(o) and m.startswith(f_prefix):
            f_name = m[len(f_prefix):]
            all_f_map[f_name] = o
    for f_current in sorted(all_f_map.keys()):
        f_sig = str(inspect.signature(all_f_map[f_current])).replace("(", "").replace(")", "").upper()
        f_sig = [ "<" + xx.strip() + ">" for xx in f_sig.split(" ") if xx.strip() != "" ]
        f_sig = " ".join(f_sig).replace(",", "")
        f_doc = inspect.getdoc(all_f_map[f_current])
        f_docfull = inspect.getdoc(all_f_map[f_current])
        if f_docfull == None:
            f_docfull = ""
        f_docfull = f_docfull.split("\n")
        if f_doc == None:
            f_doc = "undocumented method"
        f_doc = f_doc.split("\n")[0].strip()




    if build_manual:
        if program_name.endswith("__main__.py"):
            program_name = os.environ.get("BASH_SRC", "PROGRAM").split(os.sep)[-1]

        lines = ["Syntax:", ""]
        for f_current in sorted(all_f_map.keys()):
            f_sig = str(inspect.signature(all_f_map[f_current])).replace("(", "").replace(")", "").upper()
            f_sig = [ "<" + xx.strip() + ">" for xx in f_sig.split(" ") if xx.strip() != "" ]
            f_sig = " ".join(f_sig).replace(",", "")

            f_doc = inspect.getdoc(all_f_map[f_current])
            if f_doc == None:
                f_doc = ""
            f_doc = f_doc.split("\n")[0].strip()

            f_docfull = inspect.getdoc(all_f_map[f_current])
            if f_docfull == None:
                f_docfull = "undocumented function %s\nundocumented" % f_current
            f_docfull = f_docfull.split("\n")

            lines.append("  %s %s %s" % (program_name, f_current, f_sig))
            line_idx = 1
            lines.append("")
            for doc_line in f_docfull:
                if line_idx in [1,2]:
                    lines.append("    " + "="*(3+len(f_docfull[0])))
                lines.append("    >> %s" % doc_line)
                line_idx+=1
            lines.append("")
            lines.append("")
        return "\n".join(lines)

    if len(sys.argv) <= 1:
        print("No args given")
        print("")
        print(cli_this(module_name, f_prefix, build_manual=True))
        sys.exit(1)
        return

    action = sys.argv[1]
    help_check = action.strip().replace("-", "")
    if help_check == "h" or help_check == "help":
        print(cli_this(module_name, f_prefix, build_manual=True))
        sys.exit(0)

    opts = sys.argv[2:]
    f_actual = None

    for m,o in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(o) and m.startswith(f_prefix) and m == f_prefix+action:
            f_actual = o
            break

    if f_actual is not None:
        # f_actual()
        #print("would call %s with %s" % (f_actual, str(opts)))
        f_actual(*opts)
        sys.exit(0)
    else:
        print("unknown action %s" % action)
        sys.exit(1)
