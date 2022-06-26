# 微信猴子机器人 - WxMonkeyBot

微信猴子机器人，寓意为：训练有素的猴子 :D  

基于pywinauto库，在Windows上实现了模拟用户操作，自动读取、回复微信消息

> 版本：Version 0.1  
> 作者：inferno0303@github

## 安装

```bash
pip install -i http://mirrors.aliyun.com/pypi/simple/ -r requirement.txt
```

## 运行

```bash
python WxMonkeyBot.py
```
- 运行后会自动创建sqlite数据库

- 程序会扫描WeChat.exe的进程ID，获取ChatWnd窗口，即微信的独立聊天窗口（双击会话列表），保独立聊天窗口在前台运行（最小化、窗口化、最大化均可）

- 程序会解析独立聊天窗的UI结构，轮询获取message，并去重存入sqlite

- 在达成触发条件后，程序会自动执行窗口化，获取焦点等操作，模拟键盘输入文字，按下ENTER回车键发送信息

## 工具

### 导入语料库到sqlite

运行./utils/utils_DBImport.py脚本，将同目录下的*.txt文件解析，并导入到sqlite

## 更新日志

### Version 0.1

首次提交
