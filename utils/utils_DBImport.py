"""
version: v0.1.1
author: inferno0303@github

本程序用于导入语料库*.txt文件到sqlite数据库
"""
import sqlite3

# sqlite路径
conn = sqlite3.connect('../store.db')
c = conn.cursor()
# 创建数据表
c.execute('''CREATE TABLE IF NOT EXISTS QA_Library
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                Q TEXT,
                A TEXT);''')
conn.commit()

# 读取当前目录下的*.txt文件
with open(file="./simsimi_QA.txt", mode="r", encoding="UTF8") as f:
    data = f.readlines()
    # 存放k-v的list
    result = []
    # 每一项
    item = {"Q": None, "A": None}
    # 当前读取的是问题还是回答，问题："Q"，回答"A"
    now = "Q"
    for i in data:
        i = i.strip('\n').strip().replace('"', '')
        # 如果是空行，就读完了
        if len(i) == 0:
            result.append(item)
            # 重置一下状态
            now = "Q"
            item = {"Q": None, "A": None}
            continue
        print("[INFO] 读取：", i)
        if now == "Q":
            item["Q"] = i
            now = "A"
        elif now == "A":
            item["A"] = i
            now = "Q"

count = 0
total = len(result)
for i in result:
    sql = f'''INSERT INTO QA_Library (Q, A) VALUES ("{i['Q']}", "{i['A']}");'''
    print("[INFO] INSERT数据库：", i, sql, "已完成：", count, "总数：", total)
    c.execute(sql)
print("[INFO] COMMIT数据库...")
conn.commit()
print("[INFO] DONE.")

