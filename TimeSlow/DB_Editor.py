import sqlite3

data = sqlite3.connect("Data.db")
cursor = data.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS guilds(
id INT PRIMARY KEY, 
name TEXT,
mod INT,
time_joined INT,
is_initialised BOOL,
mute_role_id INT,
log_channel_id INT,
language TEXT);
''')
data.commit()

guildvalues = (123456789012, 'test', 2, None, bool(1), 0, 0, 'ru')
cur = data.cursor()
cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?, ?, ?);", guildvalues)
data.commit()

cursor.execute("SELECT * FROM guilds;")
print(cursor.fetchone())