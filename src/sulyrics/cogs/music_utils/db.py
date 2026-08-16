import os
import sqlite3


class DB:
    def __enter__(self):
        self.con = sqlite3.connect('data/sulyrics.db')
        self.con.execute("PRAGMA foreign_keys = 1")
        return self.con.cursor()
    def __exit__(self, type, value, traceback):
        self.con.commit()
        self.con.close()

def get_data(query):
    with DB() as cur:
        cur.execute(query)
        return cur.fetchall()

def add_new_guild(guild_id, guild_name, channel_id, message_id):
    with DB() as cur:
        cur.execute("REPLACE INTO MUSIC Values(:GuildID, :GuildName, :ChannelID, :MessageID);", {"GuildID": guild_id, "GuildName": guild_name, "ChannelID": channel_id, "MessageID": message_id})

def add_log(title, url, requester, guild_id):
    with DB() as cur:
        cur.execute("INSERT INTO MUSICLOG(Title, URL, Requester, GuildID) Values(:Title, :URL, :Requester, :GuildID);", {"Title": title, "URL": url, "Requester": requester, "GuildID": guild_id})
