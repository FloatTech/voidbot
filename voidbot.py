import websocket
import time
import json

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


class PluginPool:
    def __init__(self):
        self.pool = []

    def add(self, plugin):
        self.pool.append(plugin)


def on_message(ws, message):
    print(message)
    context = json.loads(message)
    if 'post_type' in context:
        p = Plugin(context)
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
