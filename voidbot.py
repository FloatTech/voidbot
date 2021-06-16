import websocket
import threading
import time
import re
import queue
import logging
import json as json_
from collections import deque

WS_URL = 'ws://127.0.0.1:6700/ws'  # WebSocket 地址
NICKNAME = ['BOT', 'ROBOT']  # 机器人昵称
SUPER_USER = [12345678, 23456789]  # 主人的 QQ 号
# 日志设置
logging.basicConfig(level=logging.DEBUG, format='[void] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Plugin:
    def __init__(self, context: dict):
        self.ws = ws
        self.context = context

    def match(self):
        return self.on_full_match("hello")

    def handle(self):
        self.send_msg(text("hello world!"))

    def on_message(self):
        return self.context['post_type'] == 'message'

    def on_full_match(self, keyword=''):
        return self.on_message() and self.context['message'] == keyword

    def on_reg_match(self, pattern=''):
        return self.on_message() and re.search(pattern, self.context['message'])

    def to_me(self):
        flag = False
        for nick in NICKNAME + [f"[CQ:at,qq={self.context['self_id']}] "]:
            if self.on_message() and nick in self.context['message']:
                flag = True
                self.context['message'] = self.context['message'].replace(nick, "")
        return flag

    def super_user(self):
        for user in SUPER_USER:
            if user == self.context['user_id']:
                return True
        return False

    def admin_user(self):
        return self.super_user() or self.context['sender']['role'] in ('admin', 'owner')

    def call_api(self, action: str, params: dict) -> dict:
        echo_num, q = echo.get()
        data = json_.dumps({"action": action, "params": params, "echo": echo_num})
        logger.info(data)
        self.ws.send(data)
        # 阻塞至响应或者等待30s超时
        try:
            ret = q.get(timeout=30)
            return ret
        except queue.Empty:
            logger.error("API调用[{echo_num}] 超时......")

    def send_msg(self, *message):
        if 'group_id' in self.context and self.context['group_id']:
            self.send_group_msg(*message)
        else:
            self.send_private_msg(*message)

    def send_group_msg(self, *message):
        params = {"group_id": self.context["group_id"], "message": message}
        ret = self.call_api("send_group_msg", params)
        if ret is None or ret['status'] == 'failed':
            return 0
        else:
            return ret['data']['message_id']

    def send_private_msg(self, *message):
        params = {"user_id": self.context["user_id"], "message": message}
        ret = self.call_api("send_private_msg", params)
        if ret is None or ret['status'] == 'failed':
            return 0
        else:
            return ret['data']['message_id']


def text(string: str) -> dict:
    return {'type': 'text', 'data': {'text': string}}


def at(qq: int) -> dict:
    return {'type': 'at', 'data': {'qq': qq}}


def image(file: str, cache=True) -> dict:
    return {'type': 'image', 'data': {'file': file, 'cache': cache}}


def record(file: str, cache=True) -> dict:
    return {'type': 'record', 'data': {'file': file, 'cache': cache}}


def json(data: str) -> dict:
    return {'type': 'json', 'data': {'data': data}}


def xml(data: str) -> dict:
    return {'type': 'xml', 'data': {'data': data}}


'''
在下面加入你自定义的插件，自动加载本文件所有的 Plugin 的子类
只需要写一个 Plugin 的子类，重写 match() 和 handle()
match() 返回 True 则自动回调 handle()
'''


class TestPlugin(Plugin):
    def match(self):  # 说 hello 则回复
        return self.on_full_match('hello')

    def handle(self):
        self.send_msg(at(self.context['user_id']), text('hello world!'))


class TestPlugin2(Plugin):
    def match(self):  # 艾特机器人说菜单则回复
        return self.to_me() and self.on_full_match('菜单')

    def handle(self):
        self.send_msg(text('没有菜单'))


class TestPlugin3(Plugin):
    def match(self):  # 戳一戳机器人则回复
        return self.context['post_type'] == 'notice' and self.context['sub_type'] == 'poke'\
            and self.context['target_id'] == self.context['self_id']

    def handle(self):
        self.send_msg(text('请不要戳我 >_<'))


'''
在上面自定义你的插件
'''


def on_message(_, message):
    context = json_.loads(message)
    if 'echo' in context:
        logger.debug(message)
        # 响应报文通过队列传递给调用 API 的函数
        echo.match(context)
    elif 'meta_event_type' in context:
        logger.debug(message)
    else:
        logger.info(message)
        # 消息事件，开启线程
        t = threading.Thread(target=plugin_pool, args=(context, ))
        t.start()


def plugin_pool(context: dict):
    # 遍历所有的 Plugin 的子类，执行匹配
    for P in Plugin.__subclasses__():
        plugin = P(context)
        if plugin.match():
            plugin.handle()


class Echo:
    def __init__(self):
        self.echo_num = 0
        self.echo_list = deque(maxlen=20)

    def get(self):
        self.echo_num += 1
        q = queue.Queue(maxsize=1)
        self.echo_list.append((self.echo_num, q))
        return self.echo_num, q

    def match(self, context: dict):
        for obj in self.echo_list:
            if context['echo'] == obj[0]:
                obj[1].put(context)


if __name__ == "__main__":
    echo = Echo()
    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_open=lambda _: logger.debug('连接成功......'),
        on_close=lambda _: logger.debug('重连中......'),
    )
    while True:  # 掉线重连
        ws.run_forever()
        time.sleep(5)
