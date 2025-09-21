from typing import Optional

def force_ip4(src:Optional[str], default:str="0.0.0.0") -> str:
    if src == None:
        return default
    if src.strip() == "":
        return default
    try:
        int_cols = [int(x.strip()) for x in src.strip().split(".")]
        return "%d.%d.%d.%d" % (int_cols[0] % 256, int_cols[1] % 256, int_cols[2] % 256, int_cols[3] % 256)
    except:
        return default
