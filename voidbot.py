import websocket
import threading
import time
import json
import re
import queue
import logging
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

    def on_full_match(self, keyword=''):
        return self.context['post_type'] == 'message' and self.context[
            'message'] == keyword

    def on_reg_match(self, pattern=''):
        return self.context['post_type'] == 'message' and re.search(
            pattern, self.context['message'])

    def call_api(self, action: str, params: dict) -> dict:
        echo_num, q = echo.get()
        data = json.dumps({
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


'''
在下面加入你自定义的插件
1.写一个Plugin的子类，重写match和handle方法
2.将类对象加入Plugins
'''


class TestPlugin(Plugin):
    def match(self):
        return self.on_full_match("123")

    def handle(self):
        self.send_group_msg(ms_text("yes"))


class TestPlugin2(Plugin):
    def match(self):
        return self.on_reg_match(r'321')

    def handle(self):
        self.send_group_msg(ms_text("yes2"))


'''
在上面自定义你的插件
'''


def ms_text(string: str) -> dict:
    return {'type': 'text', 'data': {'text': string}}


def ms_at(qq: int) -> dict:
    return {'type': 'at', 'data': {'qq': qq}}


def ms_image(file: str, cache=True) -> dict:
    return {'type': 'image', 'data': {'file': file, 'cache': cache}}


def ms_record(file: str, cache=True) -> dict:
    return {'type': 'record', 'data': {'file': file, 'cache': cache}}


def ms_json(data: str) -> dict:
    return {'type': 'json', 'data': {'data': data}}


def on_message(ws, message):
    context = json.loads(message)
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


def on_open(ws):
    logger.debug('连接成功......')


def on_close(ws):
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
