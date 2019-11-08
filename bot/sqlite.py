import sqlite3
import sys
import datetime
from sqlite3 import Error

class Sql():
    def __init__(self, name='tibia.db'):
        self.conn = None
        self.cursor = None
        if name:
            self.open(name)
            self.createTables()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print("Error connecting to database!")        
    
    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
    
    def createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS onlinelist
                        (name text UNIQUE, level int, world text, online int, status int, date text)''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS whitelist
                        (name text UNIQUE, world text, level int, date text)''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS lastdeaths
                        (name text UNIQUE, deathdate text, status int, date text)''')
        self.conn.commit()

    def createTable(self, data):
        cur = self.conn.cursor()
        cur.execute(data)
        self.conn.commit()
    
    def executeQuery(self, query, values):
        self.conn.cursor()
        sql = self.conn.execute(query, values)
        self.conn.commit()
        return sql
    
    # online
    def onlineCount(self):
        cur = self.conn.cursor()
        return int(cur.execute("SELECT COUNT(1) FROM onlinelist WHERE online=1").fetchone()[0])
    
    def addOnlinelist(self, name, level, world, online=1, status=0, date=""):
        cur = self.conn.cursor()
        val = [name, level, world, online, status, date]
        sql = cur.execute("INSERT OR IGNORE INTO onlinelist values (?, ?, ?, ?, ?, ?)", val)
        self.conn.commit()
        return sql
    
    def updateOnlinelist(self, name, level, online=0, status=0):
        cur = self.conn.cursor()
        val = [level, online, status, name]
        sql = cur.execute("UPDATE onlinelist SET level=?, online=?, status=? WHERE name=?", val)
        self.conn.commit()
        return sql
    
    def removeOnlinelist(self, name):
        cur = self.conn.cursor()
        val = [name]
        sql = cur.execute("DELETE FROM onlinelist WHERE name=?", val)
        self.conn.commit()
        return sql
    
    def getOnlineList(self):
        cur = self.conn.cursor()
        result = cur.execute("SELECT * FROM onlinelist").fetchall()
        onlinelist = []
        for row in result:
            onlinelist.append(row)
        return onlinelist

    def getOnlinelistNames(self):
        cur = self.conn.cursor()
        result = cur.execute("SELECT name FROM onlinelist").fetchall()
        onlinelist = []
        for row in result:
            onlinelist.append(row[0])
        return onlinelist
    
    def getOnlinelistOnline(self, name):
        cur = self.conn.cursor()
        n = [name]
        ret = cur.execute("SELECT online FROM onlinelist WHERE name=?", n).fetchone()
        if ret == None:
            return False
        return bool(ret[0])

    def getOnlinelistStatus(self, name):
        cur = self.conn.cursor()
        val = [name]
        ret = cur.execute("SELECT status FROM onlinelist WHERE name=?", val).fetchone()
        if ret == None:
            return False
        return bool(ret[0])

    def getOnlinelistLevel(self, name):
        cur = self.conn.cursor()
        val = [name]
        ret = cur.execute("SELECT level FROM onlinelist WHERE name=?", val).fetchone()
        if ret == None:
            return False
        return str(ret[0])
    
    # whitelist
    def addWhitelist(self, name, world, level):
        cur = self.conn.cursor()
        val = [name, world, level, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        sql = cur.execute("INSERT OR IGNORE INTO whitelist values (?,?,?,?)", val)
        self.conn.commit()
        return sql

    def removeWhitelist(self, name):
        cur = self.conn.cursor()
        val = [name]
        sql = cur.execute("DELETE FROM whitelist WHERE name=?", val)
        self.conn.commit()
        return sql
    
    def getWhitelist(self):
        cur = self.conn.cursor()
        result = cur.execute("SELECT name, world, level FROM whitelist").fetchall()
        whitelist = []
        for name, world, level in result:
            whitelist.append([name, world, level])
        return whitelist

    def getWhitelistNames(self):
        cur = self.conn.cursor()
        result = cur.execute("SELECT name FROM whitelist").fetchall()
        whitelist = []
        for name in result:
            whitelist.append(name[0])
        return whitelist

    def updateWhitelistLevel(self, name, level):
        cur = self.conn.cursor()
        val = [level, name]
        sql = cur.execute("UPDATE whitelist SET level=? WHERE name=?", val)
        self.conn.commit()
        return sql

    # lastdeaths
    def addLastDeath(self, name, deathdate, status=0, date=""):
        cur = self.conn.cursor()
        val = [name, deathdate, status, date]
        sql = cur.execute("INSERT OR IGNORE INTO lastdeaths values (?, ?, ?, ?)", val)
        self.conn.commit()
        return sql

    def removeLastDeath(self, name):
        cur = self.conn.cursor()
        val = [name]
        sql = cur.execute("DELETE FROM lastdeaths WHERE name=?", val)
        self.conn.commit()
        return sql

    def updateLastDeath(self, name, deathdate, status=0):
        cur = self.conn.cursor()
        val = [deathdate, status, name]
        sql = cur.execute("UPDATE lastdeaths SET deathdate=?, status=? WHERE name=?", val)
        self.conn.commit()
        return sql
    
    def getLastDeath(self, name):
        cur = self.conn.cursor()
        val = [name]
        ret = cur.execute("SELECT deathdate, status FROM lastdeaths WHERE name=?", val).fetchone()
        if ret is not None:
            return ret
        return ret
