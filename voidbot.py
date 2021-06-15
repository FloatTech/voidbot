import websocket
import time
import json
import re

# WebSocket 地址
websocket_url = 'ws://127.0.0.1:6700/ws'


class Plugin:
    def __init__(self, context: dict):
        self.ws = ws
        self.context = context
        self.echo = 0

    def match(self):
        return self.on_full_match("xxx")

    def handle(self):
        self.send_group_msg("ok")

    def on_full_match(self, keyword=''):
        return self.context['post_type'] == 'message' and self.context['message'] == keyword

    def on_reg_match(self, pattern=''):
        return self.context['post_type'] == 'message' and re.search(pattern, self.context['message'])

    def send_group_msg(self, message: str):
        dic = {
            "action": "send_group_msg",
            "params": {
                "group_id": self.context["group_id"],
                "message": message,
            },
            "echo": ""
        }
        self.ws.send(json.dumps(dic))

    def send_private_msg(self, message: str):
        dic = {
            "action": "send_private_msg",
            "params": {
                "user_id": self.context["user_id"],
                "message": message,
            },
            "echo": ""
        }
        self.ws.send(json.dumps(dic))


'''
在下面加入你自定义的插件
1.写一个Plugin的子类，重写match和handle方法
2.将类对象加入Plugins
'''

class TestPlugin(Plugin):
    def match(self):
        return self.on_full_match("123")
    
    def handle(self):
        self.send_group_msg("yes")


class TestPlugin2(Plugin):
    def match(self):
        return self.on_reg_match(r'321')
    
    def handle(self):
        self.send_group_msg("yes2")


Plugins = [
    TestPlugin,
    TestPlugin2,
]

'''
在上面自定义你的插件
'''

class PluginPool:
    def __init__(self):
        self.pool = []

    def add(self, plugin):
        self.pool.append(plugin)


def on_message(ws, message):
    print(message)
    context = json.loads(message)
    if 'post_type' in context:
        for P in Plugins:
            p = P(context)
            if p.match():
                p.handle()


def on_close(ws):
    print('### close ###')


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        websocket_url,
        on_message=on_message,
        on_close=on_close,
    )
    while True:
        ws.run_forever()
        time.sleep(1)
        print('重连中......')
