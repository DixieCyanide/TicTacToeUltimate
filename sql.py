import os
import pyodbc
from configparser import ConfigParser

config_path = os.getcwd() + "/config.txt"
config = ConfigParser(inline_comment_prefixes = ('#', ';'))
config.read(config_path, encoding = "utf-8")

basic_cfg = config["BASIC"]

def Connect():
    return pyodbc.connect(basic_cfg["DBpath"])

def RetrieveData(table_name: str, search_col: str, to_search: str):
    conn = Connect()
    cursor = conn.cursor()
    with cursor.connection:
        cursor.execute('SELECT * FROM TTTUbot WHERE ' + "\"" + search_col + "\"" + '=\'' + to_search + '\'')
    conn.close()
    return cursor.fetchall()

def InsertData(table_name: str, col: str, value: str):
    conn = Connect()
    cursor = conn.cursor()
    print(value)
    with cursor.connection:
        cursor.execute(f"INSERT INTO {table_name} ({col}) VALUES ({value})")
    conn.close()

def CreateRow(serverID: int):
    conn = Connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ServerSettings (ServerID) VALUES (?)", (serverID))
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


#Server[@Name='DESKTOP-1TIAQ2B\DISCORD_SERVER']/Database[@Name='TTTUbot']/Table[@Name='ServersSettings' and @Schema='dbo']/Data