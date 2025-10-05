import sqlite3
import os

path = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(path + '/cogs/data/sulyrics.db')

con.execute("PRAGMA foreign_keys = 1")

cur = con.cursor()

#테이블 생성
cur.execute('''CREATE TABLE IF NOT EXISTS MUSIC(
            GuildID     int     PRIMARY KEY, 
            GuildlName  text, 
            ChannelID   int, 
            MessageID   int)''')

cur.execute('''CREATE TABLE IF NOT EXISTS MUSICLOG(
            Title       text, 
            URL         text, 
            Requester   text, 
            Date        DATETIME DEFAULT (strftime('%m/%d %H:%M', DATETIME('now', 'localtime'))), 
            GuildID     int,
            FOREIGN KEY (GuildID) REFERENCES Music(GuildID))''')

data = input("input message link: ")

GuildID = int(data.split("/")[-3])
ChannelID = int(data.split("/")[-2])
MessageID = int(data.split("/")[-1])

GuildName = input("input GuildName: ")

print(f"GuildID: {GuildID}")
print(f"GuildName: {GuildName}")
print(f"ChannelID: {ChannelID}")
print(f"MessageID: {MessageID}")

cur.execute("REPLACE INTO MUSIC Values(:GuildID, :GuildName, :ChannelID, :MessageID);", {"GuildID": GuildID, "GuildName": GuildName, "ChannelID": ChannelID, "MessageID": MessageID})

con.commit()
con.close()

print("완료")