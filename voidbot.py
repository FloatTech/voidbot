import websocket
import threading
import time
import re
import queue
import logging
import json as json_
from collections import deque

# WebSocket 地址
websocket_url = 'ws://127.0.0.1:6700/ws'
# 日志设置
logging.basicConfig(level=logging.DEBUG,
                    format='[void] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Plugin:
    def __init__(self, context: dict):
        self.ws = ws
        self.context = context

    def match(self):
        return self.on_full_match("xxx")

    def handle(self):
        self.send_group_msg("ok")

    def on_message(self):
        return self.context['post_type'] == 'message'

    def on_full_match(self, keyword=''):
        return self.on_message() and self.context['message'] == keyword

    def on_reg_match(self, pattern=''):
        return self.on_message() and re.search(pattern,
                                               self.context['message'])

    def call_api(self, action: str, params: dict) -> dict:
        echo_num, q = echo.get()
        data = json_.dumps({
            "action": action,
            "params": params,
            "echo": echo_num,
        })
        logger.info(data)
        self.ws.send(data)
        # 阻塞至响应或者等待30s超时
        try:
            ret = q.get(timeout=30)
            return ret
        except queue.Empty:
            logger.error("API调用[{echo_num}] 超时......")

    def send_msg(self, *message):
        if self.context['group_id']:
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
在下面加入你自定义的插件
1.写一个Plugin的子类，重写match和handle方法
2.将类对象加入Plugins
'''


class TestPlugin(Plugin):
    def match(self):
        return self.on_full_match("hello")

    def handle(self):
        self.send_msg(at(self.context['user_id']), text("hello world!"))


class TestPlugin2(Plugin):
    def match(self):
        return self.on_reg_match(r'\[CQ:at,qq=\d+\] 菜单')

    def handle(self):
        self.send_msg(text("没有菜单"))


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


def on_open(_):
    logger.debug('连接成功......')


def on_close(_):
    logger.debug('重连中......')


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
        websocket_url,
        on_message=on_message,
        on_open=on_open,
        on_close=on_close,
    )
    while True:  # 掉线重连
        ws.run_forever()
        time.sleep(5)
