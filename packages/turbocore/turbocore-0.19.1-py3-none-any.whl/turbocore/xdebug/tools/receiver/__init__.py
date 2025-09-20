import socket
import xml.etree.ElementTree as ET

HOST = "127.0.0.1"
PORT = 9000
IDEKEY = "PHPSTORM"
NS = {'dbgp':'urn:debugger_protocol_v1'}

def _recv_message(conn):
    length_str = b""
    while True:
        c = conn.recv(1)
        if c == b"\x00":
            break
        length_str+=c
    length = int(length_str)
    xml_data = b""
    while len(xml_data) < length:
        xml_data += conn.recv(length-len(xml_data))
    conn.recv(1)
    return xml_data.decode()


def _send_command(conn, cmd, txn_id):
    message = f"{cmd} -i {txn_id}\x00".encode()
    conn.sendall(message)

def _parse_stack(xml_str):
    root = None
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as e:
        return []
    
    frames = []
    for stack in root.findall(".//dbgp:stack", NS):
        frames.append({
            "level":stack.attrib.get("level"),
            "function":stack.attrib.get("where"),
            "file":stack.attrib.get("filename"),
            "line":stack.attrib.get("lineno")
        })
    return frames


def _get_status(xml_str):
    return _xml_attrib(xml_str, "status")


def _strip_file_protocol(src:str):
    if src != None:
        if src.startswith("file://"):
            return src[7:]
    return src


def _xml_attrib(xml_str, name, default=None):
    try:
        root = ET.fromstring(xml_str)
        v = root.attrib.get(name)
        if v == None:
            return default
        else:
            return v
    except ET.ParseError as e:
        return default



def main():
    """vp -m turbocore.xdebug.tools.receiver.
    """
    print("receiving")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            print("waiting for connection...")
            conn, addr = s.accept()
            with conn:
                txn_id = 1
                init_packet = _recv_message(conn)
                file_path = _strip_file_protocol(_xml_attrib(init_packet, "fileuri", ""))
                for line_num in range(1,30):
                    _send_command(conn, f'breakpoint_set -t line -f {file_path} -n {line_num}', txn_id)
                    txn_id+=1
                    _recv_message(conn)
                _send_command(conn, "run", txn_id)
                txn_id+=1
                run_res = _recv_message(conn)

                if _get_status(run_res) != "break":
                    print("no break")
                    return
                
                _send_command(conn, "stack_get", txn_id)
                txn_id+=1
                stack1_res = _recv_message(conn)
                frames1 = _parse_stack(stack1_res)

                current_d = 0
                max_d = 8

                while True:
                    if current_d >= max_d:
                        _send_command(conn, "step_over", txn_id)
                    else:
                        _send_command(conn, "step_into", txn_id)
                    txn_id+=1
                    step_res = _recv_message(conn)
                    step_status = _get_status(step_res)

                    if step_status == "break":
                        _send_command(conn, "stack_get", txn_id)
                        txn_id+=1
                        step_stack_res = _recv_message(conn)
                        frames = _parse_stack(step_stack_res)
                        current_d = len(frames)
                        f = frames[0]
                        print(f['file'])
                    elif step_status in ("stopping", "stopped"):
                        print("STOP")
                        break
                    else:
                        print("UNKNOWN STEP STATUS %s" % step_status)
                        break
