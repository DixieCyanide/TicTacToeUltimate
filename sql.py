import os
import pyodbc
from configparser import ConfigParser

config_path = os.getcwd() + "/config.txt"
config = ConfigParser(inline_comment_prefixes = ('#', ';'))
config.read(config_path, encoding = "utf-8")

basic_cfg = config["BASIC"]

def Connect():
    return pyodbc.connect(basic_cfg["DBpath"])

def RetrieveData(table_name: str, column_name: str, ServerID: int):
    conn = Connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE ServerID = {ServerID}")
    return cursor.fetchval()
    conn.close()

def UpdateData(table_name: str, column_name: str, value: str, ServerID: int):
    conn = Connect()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET {column_name} = '{value}' WHERE ServerID = {ServerID}")
    conn.commit()
    conn.close()

def CreateRow(serverID: int):
    conn = Connect()
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO ServerSettings (ServerID) VALUES ({serverID})")
    except:
        print("Tried to add existing server") #change to ApplyServerSetting()
    conn.commit()
    conn.close()
    return

def test():
    conn = Connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ServersSettings")
    out = cursor.fetchone()
    print(out)
    return