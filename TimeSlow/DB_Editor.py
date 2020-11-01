import sqlite3

data = sqlite3.connect("Data.db")
cursor = data.cursor()

data.execute('''CREATE TABLE IF NOT EXISTS guilds (
id INT, 
name TEXT,
mod INT,
time_joined DATETIME,
is_initialised BOOL,
mute_role_id INT,
log_channel_id INT
language TEXT
)''')

data.commit()
cursor.close()
