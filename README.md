# 微信猴子机器人 - WxMonkeyBot

> 版本：v0.1.1  
> 作者：inferno0303@github  
> 开源许可证：MIT License

关联：微信机器人，微信客服，微信自动回复，聊天机器人

**实现了在Windows上自动 「读取、回复」 微信消息**  
微信猴子机器人，寓意为：**一只训练有素的猴子🐵**

## 截图

<img src="https://cdn.jsdelivr.net/gh/inferno0303/assets@main/README图床/WxMonkeyBot_01.4u8ricooadc0.webp" alt="截图01" width="500px">

点这里：[视频演示](https://cdn.jsdelivr.net/gh/inferno0303/assets@main/README图床/WxMonkeyBot_02.mp4)

## 原理

依赖pywinauto库进行自动化操作，UIA可帮助我们访问win32程序控件  
依赖sqlite3存储语料库、聊天记录

## 安装依赖

需要Python 3.7以上版本，推荐在virtualvenv下运行

```bash
git clone https://github.com/inferno0303/WxMonkeyBot.git

cd WxMonkeyBot

// 创建虚拟环境
python -m venv ./venv

cd ./venv/Scripts

// 如果你在cmd环境
.\activate

// 如果你在bash shell环境
source ./activate

// 安装依赖
pip install -i http://mirrors.aliyun.com/pypi/simple/ -r requirement.txt
```

## 运行

### 如果您是初次运行

如果您是初次运行，请先执行导入语料库操作。

语料库以`*.txt`格式存档在`./utils`目录中，语料库的格式为：

```text
Question line 1
Answer line 1

Question line 2
Answer line 2

...
...
```

然后执行`utils/utils_DBImport.py`程序导入到sqlite：

```bash
python ./utils/utils_DBImport.py
```

### 启动主程序

启动主程序前，确保您已经正确导入了语料库。运行以下命令启动主程序：

```bash
python WxMonkeyBot.py
```

### 运行时注意事项

1. 程序会获取WeChat.exe的进程ID，获取**独立聊天窗**句柄，并循环监控。
2. 监听内容：微信的独立聊天窗口，**双击会话列表对应联系人**可打开独立聊天窗，独立聊天窗一旦被打开，程序会自动监听消息内容
3. 保持运行：请保持**独立聊天窗一直运行，不要点击 X 关闭，否则会停止监听**
4. 监听多个：如过要监控多个独立聊天窗口，**请打开多个独立聊天窗，你可以将所有窗口最小化。如果想停止监听单个聊天窗口，可以随时关闭对应的独立聊天窗**
5. 自动回信：触发条件后，程序会获取对应窗口焦点，然后模拟键盘输入文字，并按下ENTER回车键发送信息

## 工具

- ./utils/utils_DBImport.py脚本，将同目录下的*.txt文件解析，并导入到sqlite3

## 更新日志

### v0.1

- First commit

### v0.1.1

- fix(main_WxMonkeyBot.py): 修复一些意外退出的问题
- fix(utils_DBImport.py): 优化运行时信息显示
- docs(README.md): 完善README
- add(LICENSE): MIT LICENSE
