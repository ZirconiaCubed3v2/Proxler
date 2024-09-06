import time
import proxmoxer
from dotenv import load_dotenv
import os

def cloneVM(dbcurs, api, vm, userid):
    dbcurs.execute(f"SELECT * FROM USERDATA WHERE USERID = '{userid}';")
    check = dbcurs.fetchone()
    if check != None:
        return False
    dbcurs.execute("SELECT MAX(VMID) FROM USERDATA;")
    try:
        newid = dbcurs.fetchone()[0] + 1
    except TypeError:
        newid = 110
    dbcurs.execute("SELECT MAX(VNCPORT) FROM USERDATA;")
    try:
        vncport = dbcurs.fetchone()[0] + 1
    except TypeError:
        vncport = 1
    newNode = min(scoreNodes(api), key = scoreNodes(api).get)
    if vm == "ubuntu":
        vmid = 104
        pool = "linux"
    elif vm == "win10":
        vmid = 103
        pool = "windows"
    elif vm == "winserv-19":
        vmid = 102
        pool = "winserv"
    elif vm == "mint":
        vmid = 105
        pool = "linux"
    newName = api.nodes(os.getenv("TEMPLATENODE")).qemu(vmid).config().get()["name"]
    api.nodes(os.getenv("TEMPLATENODE")).qemu(vmid).clone().post(vmid=vmid, name=newName, target=newNode, pool=pool, node=os.getenv("TEMPLATENODE"), newid=newid)
    time.sleep(3)
    api.nodes(newNode).qemu(newid).config().post(args=f"-vnc 0.0.0.0:{vncport}")
    dbcurs.execute(f"INSERT INTO USERDATA VALUES ('{userid}', {newid}, {vncport}, '{newNode}');")
    return [newid, vncport, newNode]

def powerVM(dbcurs, api, userid, action):
    dbcurs.execute(f"SELECT * FROM USERDATA WHERE USERID = '{userid}';")
    vm = dbcurs.fetchone()
    if vm == None:
        return False
    match action:
        case "shutdown":
            api.nodes(vm[3]).qemu(vm[1]).status().shutdown().post(node=vm[3], vmid=vm[1])
        case "start":
            api.nodes(vm[3]).qemu(vm[1]).status().start().post(node=vm[3], vmid=vm[1])
        case "reboot":
            api.nodes(vm[3]).qemu(vm[1]).status().reboot().post(node=vm[3], vmid=vm[1])
        case "stop":
            api.nodes(vm[3]).qemu(vm[1]).status().stop().post(node=vm[3], vmid=vm[1])
        case "reset":
            api.nodes(vm[3]).qemu(vm[1]).status().reset().post(node=vm[3], vmid=vm[1])
        case _:
            return

def delVM(dbcurs, api, userid):
    dbcurs.execute(f"SELECT * FROM USERDATA WHERE USERID = '{userid}';")
    vm = dbcurs.fetchone()
    if vm == None:
        return False
    try:
        api.nodes(vm[3]).qemu(vm[1]).delete()
        dbcurs.execute(f"DELETE FROM USERDATA WHERE USERID = '{userid}';")
    except proxmoxer.core.ResourceException:
        return 10

def vmstat(dbcurs, userid):
    dbcurs.execute(f"SELECT * FROM USERDATA WHERE USERID = '{userid}';")
    vm = dbcurs.fetchone()
    if vm == None:
        return False
    return [vm[1], vm[2], vm[3]]

def scoreNodes(api):
    nodes = {}
    for node in api.nodes().get():
        if node["status"] == "online":
            nodes[node["node"]] = node["cpu"] * node["mem"]
    return nodes
