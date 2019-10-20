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
        cur.execute('''CREATE TABLE IF NOT EXISTS online
                        (name text UNIQUE, level int, world text, deathdate text, online int, status int, date text)''')

        cur.execute('''CREATE TABLE IF NOT EXISTS whitelist
                        (name text UNIQUE, world text, level int, date text)''')
        self.conn.commit()

    def addWhitelist(self, name, world, level):
        cur = self.conn.cursor()
        val = [name, world, level, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        sql = cur.execute("INSERT OR IGNORE INTO whitelist values (?,?,?,?)", val)
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

    def getOnlineList(self):
        cur = self.conn.cursor()
        result = cur.execute("SELECT * FROM online").fetchall()
        onlinelist = []
        for row in result:
            onlinelist.append(row)
        return onlinelist
    
    def getOnlineListName(self):
        cur = self.conn.cursor()
        result = cur.execute("SELECT name FROM online").fetchall()
        onlinelist = []
        for row in result:
            onlinelist.append(row[0])
        return onlinelist

    def getOnline(self, name):
        cur = self.conn.cursor()
        n = [name]
        r = cur.execute("SELECT online FROM online WHERE name=?", n).fetchone()[0]
        if r == None:
            return False
        return bool(r)

    def getStatus(self, name):
        cur = self.conn.cursor()
        val = [name]
        r = cur.execute("SELECT status FROM online WHERE name=?", val).fetchone()[0]
        if r == None:
            return False
        return bool(r)

    def getLevel(self, name):
        cur = self.conn.cursor()
        val = [name]
        return str(cur.execute("SELECT level FROM online WHERE name=?", val).fetchone()[0])
    
    def getDeathdate(self, name):
        cur = self.conn.cursor()
        val = [name]
        ret = cur.execute("SELECT deathdate FROM online WHERE name=?", val).fetchone()
        if ret is not None:
            return str(ret[0])
        return ret
    
    def addLastDeathTime(self, name, deathdate):
        cur = self.conn.cursor()
        val = [deathdate, name]
        sql = cur.execute("UPDATE online SET deathdate=? WHERE name=?", val)
        self.conn.commit()
        return sql
    
    def addToOnlinelist(self, name, level, world, deathdate, online=1, status=0):
        cur = self.conn.cursor()
        val = [name, level, world, deathdate, online, status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        sql = cur.execute("INSERT OR IGNORE INTO online values (?, ?, ?, ?, ?, ?, ?)", val)
        self.conn.commit()
        return sql
    
    def updateOnlinelist(self, name, level, online=0, status=0):
        cur = self.conn.cursor()
        val = [level, online, status, name]
        sql = cur.execute("UPDATE online SET level=?, online=?, status=? WHERE name=?", val)
        self.conn.commit()
        return sql
    
    def removeFromOnlinelist(self, name):
        cur = self.conn.cursor()
        val = [name]
        sql = cur.execute("DELETE FROM online WHERE name=?", val)
        self.conn.commit()
        return sql

    def removeFromWhitelist(self, name):
        cur = self.conn.cursor()
        val = [name]
        sql = cur.execute("DELETE FROM whitelist WHERE name=?", val)
        self.conn.commit()
        return sql

    def onlineCount(self):
        cur = self.conn.cursor()
        return int(cur.execute("SELECT COUNT(1) FROM online WHERE online=1").fetchone()[0])
