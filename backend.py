from proxmoxer import ProxmoxAPI
import os
from dotenv import load_dotenv
import time
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

load_dotenv()

ROOTPASS = os.environ["ROOTPASS"]
CONTROLLERADDR = os.environ["CONTROLLERADDR"]

treknet = ProxmoxAPI(CONTROLLERADDR, user="root@pam", password=ROOTPASS, verify_ssl=False)

def cloneVM(dbcurs, api, vm, userid):
    dbcurs.execute("SELECT MAX(VMID) FROM USERDATA;")
    try:
        newid = dbcurs.fetchone()[0] + 1
    except TypeError:
        newid = 110
    dbcurs.execute("SELECT MAX(VNCPORT) FROM USERDATA;")
    try:
        vncport = dbcurs.fetchone()[0] + 1
    except TypeError:
        vncport = 77
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
    newName = api.nodes('stargazer').qemu(vmid).config().get()["name"]
    api.nodes('stargazer').qemu(vmid).clone().post(vmid=vmid, name=newName, target=newNode, pool=pool, node="stargazer", newid=newid)
    time.sleep(3)
    api.nodes(newNode).qemu(newid).config().post(args=f"-vnc 0.0.0.0:{vncport}")
    dbcurs.execute(f"INSERT INTO USERDATA VALUES ('{userid}', {newid}, {vncport}, '{newNode}');")

def delVM(dbcurs, api, userid):
    dbcurs.execute(f"SELECT * FROM USERDATA WHERE USERID = '{userid}';")
    vm = dbcurs.fetchone()
    print(vm)
    api.nodes(vm[3]).qemu(vm[1]).delete()
    dbcurs.execute(f"DELETE FROM USERDATA WHERE USERID = '{userid}';")

def scoreNodes(api):
    nodes = {}
    for node in api.nodes().get():
        if node["status"] == "online":
            nodes[node["node"]] = node["cpu"] * node["mem"]
    return nodes

#delVM(cursor, treknet, "test1")
#delVM(cursor, treknet, "test2")
#delVM(cursor, treknet, "test3")
#cloneVM(cursor, treknet, 104, "test1")
#cloneVM(cursor, treknet, 104, "test2")
#cloneVM(cursor, treknet, 104, "test3")

conn.commit()
conn.close()
