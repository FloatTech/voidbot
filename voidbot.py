import re
import time
import queue
import logging
import threading
import collections
import json as json_

import websocket

WS_URL = "ws://127.0.0.1:6700/ws"   # WebSocket 地址
NICKNAME = ["BOT", "ROBOT"]         # 机器人昵称
SUPER_USER = [12345678, 23456789]   # 主人的 QQ 号
# 日志设置  level=logging.DEBUG -> 日志级别为 DEBUG
logging.basicConfig(level=logging.DEBUG, format="[void] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Plugin:
    def __init__(self, context: dict):
        self.ws = WS_APP
        self.context = context

    def match(self) -> bool:
        return self.on_full_match("hello")

    def handle(self):
        self.send_msg(text("hello world!"))

    def on_message(self) -> bool:
        return self.context["post_type"] == "message"

    def on_full_match(self, keyword="") -> bool:
        return self.on_message() and self.context["message"] == keyword

    def on_reg_match(self, pattern="") -> bool:
        return self.on_message() and re.search(pattern, self.context["message"])

    def only_to_me(self) -> bool:
        flag = False
        for nick in NICKNAME + [f"[CQ:at,qq={self.context['self_id']}] "]:
            if self.on_message() and nick in self.context["message"]:
                flag = True
                self.context["message"] = self.context["message"].replace(nick, "")
        return flag

    def super_user(self) -> bool:
        return self.context["user_id"] in SUPER_USER

    def admin_user(self) -> bool:
        return self.super_user() or self.context["sender"]["role"] in ("admin", "owner")

    def call_api(self, action: str, params: dict) -> dict:
        echo_num, q = echo.get()
        data = json_.dumps({"action": action, "params": params, "echo": echo_num})
        logger.info("发送调用 <- " + data)
        self.ws.send(data)
        try:    # 阻塞至响应或者等待30s超时
            return q.get(timeout=30)
        except queue.Empty:
            logger.error("API调用[{echo_num}] 超时......")

    def send_msg(self, *message) -> int:
        # https://github.com/botuniverse/onebot-11/blob/master/api/public.md#send_msg-%E5%8F%91%E9%80%81%E6%B6%88%E6%81%AF
        if "group_id" in self.context and self.context["group_id"]:
            return self.send_group_msg(*message)
        else:
            return self.send_private_msg(*message)

    def send_private_msg(self, *message) -> int:
        # https://github.com/botuniverse/onebot-11/blob/master/api/public.md#send_private_msg-%E5%8F%91%E9%80%81%E7%A7%81%E8%81%8A%E6%B6%88%E6%81%AF
        params = {"user_id": self.context["user_id"], "message": message}
        ret = self.call_api("send_private_msg", params)
        return 0 if ret is None or ret["status"] == "failed" else ret["data"]["message_id"]

    def send_group_msg(self, *message) -> int:
        # https://github.com/botuniverse/onebot-11/blob/master/api/public.md#send_group_msg-%E5%8F%91%E9%80%81%E7%BE%A4%E6%B6%88%E6%81%AF
        params = {"group_id": self.context["group_id"], "message": message}
        ret = self.call_api("send_group_msg", params)
        return 0 if ret is None or ret["status"] == "failed" else ret["data"]["message_id"]


def text(string: str) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#%E7%BA%AF%E6%96%87%E6%9C%AC
    return {"type": "text", "data": {"text": string}}


def image(file: str, cache=True) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#%E5%9B%BE%E7%89%87
    return {"type": "image", "data": {"file": file, "cache": cache}}


def record(file: str, cache=True) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#%E8%AF%AD%E9%9F%B3
    return {"type": "record", "data": {"file": file, "cache": cache}}


def at(qq: int) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#%E6%9F%90%E4%BA%BA
    return {"type": "at", "data": {"qq": qq}}


def xml(data: str) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#xml-%E6%B6%88%E6%81%AF
    return {"type": "xml", "data": {"data": data}}


def json(data: str) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#json-%E6%B6%88%E6%81%AF
    return {"type": "json", "data": {"data": data}}


def music(data: str) -> dict:
    # https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#%E9%9F%B3%E4%B9%90%E5%88%86%E4%BA%AB-
    return {"type": "music", "data": {"type": "qq", "id": data}}


"""
在下面加入你自定义的插件，自动加载本文件所有的 Plugin 的子类
只需要写一个 Plugin 的子类，重写 match() 和 handle()
match() 返回 True 则自动回调 handle()
"""


class TestPlugin(Plugin):
    def match(self):  # 说 hello 则回复
        return self.on_full_match("hello")

    def handle(self):
        self.send_msg(at(self.context["user_id"]), text("hello world!"))


class TestPlugin2(Plugin):
    def match(self):  # 艾特机器人说菜单则回复
        return self.only_to_me() and self.on_full_match("菜单")

    def handle(self):
        self.send_msg(text("没有菜单"))


class TestPlugin3(Plugin):
    def match(self):  # 戳一戳机器人则回复
        return self.context["post_type"] == "notice" and self.context["sub_type"] == "poke"\
            and self.context["target_id"] == self.context["self_id"]

    def handle(self):
        self.send_msg(text("请不要戳我 >_<"))


"""
在上面自定义你的插件
"""


def plugin_pool(context: dict):
    # 遍历所有的 Plugin 的子类，执行匹配
    for P in Plugin.__subclasses__():
        plugin = P(context)
        if plugin.match():
            plugin.handle()


class Echo:
    def __init__(self):
        self.echo_num = 0
        self.echo_list = collections.deque(maxlen=20)

    def get(self):
        self.echo_num += 1
        q = queue.Queue(maxsize=1)
        self.echo_list.append((self.echo_num, q))
        return self.echo_num, q

    def match(self, context: dict):
        for obj in self.echo_list:
            if context["echo"] == obj[0]:
                obj[1].put(context)


def on_message(_, message):
    # https://github.com/botuniverse/onebot-11/blob/master/event/README.md
    context = json_.loads(message)
    if "echo" in context:
        logger.debug("调用返回 -> " + message)
        # 响应报文通过队列传递给调用 API 的函数
        echo.match(context)
    elif "meta_event_type" in context:
        logger.debug("心跳事件 -> " + message)
    else:
        logger.info("收到事件 -> " + message)
        # 消息事件，开启线程
        t = threading.Thread(target=plugin_pool, args=(context, ))
        t.start()


if __name__ == "__main__":
    echo = Echo()
    WS_APP = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_open=lambda _: logger.debug("连接成功......"),
        on_close=lambda _: logger.debug("重连中......"),
    )
    while True:  # 掉线重连
        WS_APP.run_forever()
        time.sleep(5)
