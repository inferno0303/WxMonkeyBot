import sqlite3

conn = sqlite3.connect('../store.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS QA_Library
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                Q TEXT,
                A TEXT);''')
conn.commit()

with open(file="./simsimi回答.txt", mode="r", encoding="UTF8") as f:
    data = f.readlines()
    result = []
    item = {"Q": None, "A": None}
    now = "Q"
    for i in data:
        i = i.strip('\n').replace('"', '')
        if len(i) == 0:
            result.append(item)
            now = "Q"
            item = {"Q": None, "A": None}
            continue
        print(i)
        if now == "Q":
            item["Q"] = i
            now = "A"
        elif now == "A":
            item["A"] = i
            now = "Q"
    for i in result:
        sql = f'''INSERT INTO QA_Library (Q, A) VALUES ("{i['Q']}", "{i['A']}");'''
        print(sql)
        c.execute(sql)
        print(i)
    conn.commit()
