import sqlite3

conn = sqlite3.connect('website/database.db')
c = conn.cursor()

# c.execute("DROP TABLE IF EXISTS users")
c.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        username TEXT,
        password TEXT,
        quick_login INTEGER,
        display_name TEXT,
        friends TEXT,
        friend_requests TEXT
    )""")

# c.execute("""CREATE TABLE 'chat.1.3' (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         sent_by TEXT,
#         content TEXT,
#         time_sent TEXT,
#         read INTEGER
#     )""")

# c.execute("UPDATE users SET friend_requests = ? WHERE id = ?", ("2", 1))
# c.execute("DELETE FROM chats")
# c.execute("ALTER TABLE 'chat.2.1' ADD COLUMN read INTEGER")
# c.execute("INSERT INTO messages (sent_by, content, time_sent, read) VALUES (?, ?, ?, ?)", ("1", "Hello", "12:00", 0))
# c.execute("DROP TABLE IF EXISTS 'chat.2.1'")

# c.execute("INSERT INTO 'chat.2.1' (sent_by, content, time_sent, read) VALUES (?, ?, ?, ?)", ("1", "Hello", "12:00", 0))
# c.execute("INSERT INTO 'chat.2.1' (sent_by, content, time_sent, read) VALUES (?, ?, ?, ?)", ("3", "Hi Jem", "12:07", 0))

conn.commit()
conn.close()