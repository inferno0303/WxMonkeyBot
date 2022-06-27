import re
import time
import random
import sqlite3
import pywinauto.controls.uia_controls
from pywinauto import application, handleprops, timings

# 配置
# 触发关键词
reply_keyword = "@小香菜"
# 轮询间隔秒
sleep_sec = 1


# 返回单独的微信聊天窗口消息，返回列表
class GetWxMsg:
    def __init__(self, program_name):
        self.program_name = program_name

    # 寻找以name结尾的进程，例如：WeChat.exe
    @staticmethod
    def __get_process_id(name):
        process_list = application.process_get_modules()
        for process in process_list:
            match = re.match(".*" + name + "$", str(process[1]))
            if match:
                return process[0]

    @staticmethod
    def __get_app_instance(pid):
        # 连接到进程
        _app = application.Application(backend="uia").connect(process=pid)
        # 查找微信主窗口+聊天窗口
        _dialogs = []
        for dialog in _app.windows():
            if handleprops.classname(dialog) == "WeChatMainWndForPC" or handleprops.classname(dialog) == "ChatWnd":
                _dialogs.append(dialog)
        return _dialogs, _app

    @staticmethod
    def __parse_msg_wrapper(msg_wrapper):
        # 遍历消息wrapper，得到List<HashMap> => [{"edit": _edit, "button": _button, "visible_text": _visible_text}]
        parse_result = []
        for i in msg_wrapper.children():
            _visible_text = i.window_text()  # 获取可见的文本
            _edit = []
            _button = []
            _msg_type = "未知类型"
            for j in i.descendants():  # 遍历子对象，判断是不是文本消息，包含edit和button的元素，那就暂存起来
                if type(j) == pywinauto.controls.uia_controls.EditWrapper:
                    _edit.append(j)
                elif type(j) == pywinauto.controls.uia_controls.ButtonWrapper:
                    _button.append(j)
            if len(_edit) == 1 and len(_button) == 1:
                _msg_type = "文本消息"
            elif len(_edit) == 0 and len(_button) == 1 and _visible_text == '[动画表情]':
                _msg_type = "动画表情"
            elif len(_edit) == 0 and len(_button) == 2 and _visible_text == '[图片]':
                _msg_type = "图片"
            elif len(_edit) == 0 and len(_button) == 2 and _visible_text == '[视频]':
                _msg_type = "视频"
            elif len(_edit) == 1 and len(_button) == 3 and _visible_text == '[音乐]':
                _msg_type = "音乐"
            elif len(_edit) == 2 or 1 and len(_button) == 2 and re.match(".*引用.*消息.*", _visible_text, re.S):
                _msg_type = "引用"
            elif len(_edit) == 1 and len(_button) == 0 and re.match(".*拍了拍.*", _edit[0].window_text(), re.S):
                _msg_type = "拍一拍"
            elif len(_edit) == 1 and len(_button) == 0 and re.match(".*撤回了一条.*", _edit[0].window_text(), re.S):
                _msg_type = "撤回"
            elif len(_edit) == 0 and len(_button) == 0:
                _msg_type = "时间"
            parse_result.append(
                {"edit": _edit, "button": _button, "visible_text": _visible_text, "msg_type": _msg_type})
        return parse_result

    @staticmethod
    def __sort_msg_data(parse_result):
        sort_result = []
        for i in parse_result:
            if i["msg_type"] == "文本消息":
                _sender = i["button"][0].window_text()
                _msg = i["edit"][0].window_text()
                sort_result.append({
                    "msg_type": "文本消息",
                    "sender": _sender,
                    "msg": _msg
                })
            elif i["msg_type"] == "动画表情":
                _sender = i["button"][0].window_text()
                sort_result.append({
                    "msg_type": "动画表情",
                    "sender": _sender,
                    "msg": i["visible_text"]
                })
            elif i["msg_type"] == "图片":
                pass
            elif i["msg_type"] == "视频":
                pass
            elif i["msg_type"] == "音乐":
                pass
            elif i["msg_type"] == "引用":
                pass
            elif i["msg_type"] == "拍一拍":
                pass
            elif i["msg_type"] == "撤回":
                pass
            elif i["msg_type"] == "时间":
                pass
            elif i["msg_type"] == "未知类型":
                # print("[WARN] 未知类型消息：", i)
                pass
        return sort_result

    # 返回整理好的信息
    def do(self):
        pid = self.__get_process_id(name=self.program_name)
        if pid is None:
            print("[ERROR] " + self.program_name + " 未启动")
            return -1
        dialogs, app = self.__get_app_instance(pid=pid)
        r = []
        for i in dialogs:
            if handleprops.classname(i) == "ChatWnd":
                chat_room = handleprops.text(i)
                print("[INFO] 开始搜索聊天窗口消息：", chat_room + "...")
                msg_spec = app.window(class_name=handleprops.classname(i), title=handleprops.text(i)).child_window(
                    title="消息")
                msg_wrapper = msg_spec.wrapper_object()
                parse_result = self.__parse_msg_wrapper(msg_wrapper=msg_wrapper)
                msg_list = self.__sort_msg_data(parse_result=parse_result)
                r.append({
                    "chat_room": chat_room,
                    "msg_list": msg_list
                })
        return r


class MsgDAO:
    store = []

    def __init__(self):
        self.conn = sqlite3.connect('store.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS MESSAGE
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_room TEXT NOT NULL,
        msg_type TEXT NOT NULL,
        sender TEXT NOT NULL,
        msg TEXT NOT NULL,
        insert_time NUMERIC,
        flag_1 TEXT,
        flag_2 TEXT,
        flag_3 TEXT);''')
        self.conn.commit()

    def update_db(self, data):
        new_count = 0
        for each_chat in data:
            chat_room = each_chat["chat_room"]
            each_chat["msg_list"].reverse()
            count = 0
            for j in each_chat["msg_list"]:
                msg_type = j["msg_type"]
                sender = j["sender"]
                msg = j["msg"]
                sql = f'''SELECT * FROM MESSAGE WHERE chat_room="{chat_room}" and msg_type="{msg_type}" and
                                        sender="{sender}" and msg="{msg}"'''

                record = self.c.execute(sql)
                # 去重，如果sqlite在过去没有这条记录，就push到new_msg[]里
                if record.fetchone() is None:
                    sql2 = f'''INSERT INTO MESSAGE (chat_room, msg_type, sender, msg, insert_time)
                                        VALUES ("{chat_room}", "{msg_type}", "{sender}", "{msg}", "{int(time.time())}");'''
                    self.c.execute(sql2)
                    self.conn.commit()
                    count += 1
                else:
                    # 因为列表是反向的，所以一旦有重复，那就不要继续查找了，接下来都是重复的
                    new_count += count
                    break
            print(f"[INFO] 来自“{chat_room}”的新消息数：{count}条")
        return new_count


class ReplyMsgMonkey:
    def __init__(self):
        self.conn = sqlite3.connect('store.db')
        self.c = self.conn.cursor()

    @staticmethod
    def __get_process_id(name):
        process_list = application.process_get_modules()
        for process in process_list:
            match = re.match(".*" + name + "$", str(process[1]))
            if match:
                return process[0]

    @staticmethod
    def __get_app_instance(pid):
        # 连接到进程
        _app = application.Application(backend="uia").connect(process=pid)
        # 查找聊天窗口
        _dialogs = []
        for dialog in _app.windows():
            if handleprops.classname(dialog) == "ChatWnd":
                _dialogs.append(dialog)
        return _dialogs, _app

    # 检查有没有需要回复的消息
    def interval_check_msg(self):
        sql = f'''SELECT * FROM 
         (SELECT * FROM MESSAGE ORDER BY id desc LIMIT 5) temp
         WHERE temp.msg LIKE "%{reply_keyword}%" AND temp.flag_1 IS NULL;'''
        res = self.c.execute(sql).fetchall()
        return res

    # 执行回复消息逻辑
    def do(self, id, chat_room, sender, original_msg):
        pid = self.__get_process_id(name="WeChat.exe")
        if pid is None:
            print("[ERROR] WeChat.exe 未启动")
            return -1
        dialogs, app = self.__get_app_instance(pid=pid)
        edit_box = None
        # send_button = None
        for dialog in dialogs:
            if handleprops.classname(dialog) == "ChatWnd" and handleprops.text(dialog) == chat_room:
                for children_wrapper in dialog.descendants():
                    # 寻找输入框
                    if children_wrapper.window_text() == "输入" and type(children_wrapper) == pywinauto.controls.uia_controls.EditWrapper:
                        # 如果在名为 "输入" 的 EditWrapper 控件的 父节点.父节点.子节点 找到一个 ToolbarWrapper 控件
                        # 那么名为 "输入" 的 EditWrapper 控件 就是 消息输入框
                        for _t in children_wrapper.parent().parent().children():
                            if pywinauto.controls.uia_controls.ToolbarWrapper == type(_t):
                                edit_box = children_wrapper
                                break
                if edit_box is not None:
                    break

        if edit_box is None:
            return -1

        # 模拟键盘输入信息
        timings.Timings.slow()
        edit_box.type_keys("^a")
        edit_box.type_keys("{BACKSPACE}")
        timings.Timings.defaults()

        # 准备回复内容
        search_key = str(original_msg).replace(reply_keyword, '').strip().replace(' ', '')
        if len(search_key) > 5:
            search_key = search_key[0: 4]
        _sql1 = f'''SELECT * FROM QA_Library WHERE Q LIKE "%{search_key}%" OR A LIKE "%{search_key}%";'''
        print("[INFO] ", _sql1)
        answers = self.c.execute(_sql1).fetchall()
        print("[INFO] 回答命中候选数量：", len(answers))
        if len(answers) > 0:
            answer = answers[random.randint(0, len(answers)-1)]
            a_1 = str(answer[1]).strip().replace('`', '').replace('~', '').replace('+', '').replace('%', '').replace('^', '')
            a_2 = str(answer[2]).strip().replace('`', '').replace('~', '').replace('+', '').replace('%', '').replace('^', '')
            edit_box.type_keys(f"{a_1}，{a_2}", with_spaces=True)
        else:
            edit_box.type_keys("=。=", with_spaces=True)
        edit_box.type_keys("{VK_SHIFT down}{ENTER}{VK_SHIFT up}", with_spaces=True)
        edit_box.type_keys(f"@{sender}  ", with_spaces=True)
        edit_box.type_keys("{ENTER}")
        edit_box.type_keys("{ENTER}")
        timings.Timings.slow()
        self.c.execute(f'''UPDATE MESSAGE SET flag_1="已回复" WHERE id={id}''')
        self.conn.commit()


if __name__ == '__main__':
    getWxMsg = GetWxMsg("WeChat.exe")
    msgDAO = MsgDAO()
    replyMsgMonkey = ReplyMsgMonkey()
    while True:
        # 监听消息
        msg_list = getWxMsg.do()
        # 存入数据库（带去重）
        new_msg_count = msgDAO.update_db(msg_list)

        print("\n[INFO] ---")
        print(f"[INFO] 总新消息数：{new_msg_count}条")

        # 检查有没有人叫我
        reply_task = replyMsgMonkey.interval_check_msg()

        if len(reply_task) != 0:
            print("[INFO] 回复以下消息：", reply_task)

        # 如果有人叫我，就回复信息
        for i in reply_task:
            replyMsgMonkey.do(id=i[0], chat_room=i[1], sender=i[3], original_msg=i[4])

        # 循环
        print("[INFO] ---\n")
        time.sleep(sleep_sec)
