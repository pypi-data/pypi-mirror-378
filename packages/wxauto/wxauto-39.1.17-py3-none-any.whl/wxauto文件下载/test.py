from wxautox import WeChat
from wxauto.msgs import FriendMessage
import time

from datetime import datetime



wx = WeChat()

# 消息处理函数
def on_message(msg, chat):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),f"收到->{msg.sender}<-的消息: {msg.content} ")
    if msg.attr in("friend"):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'---开始发送回复信息')
        #chat.SendMsg(msg="收到了")
        chat.SendTypingText(msg="收到了", clear=True, exact=False)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'---结束发送回复信息')

wx.AddListenChat(nickname="好多鱼", callback=on_message)

while True:
    time.sleep(100)