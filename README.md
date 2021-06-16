# voidbot
支持 OneBot 标准的 能跑就行 Python SDK

你的插件通过基类**Plugin**的一个子类来实现。你只需要写一个继承**Plugin**的子类并重写**match**和**handle**方法就能快速实现插件功能



### How to use

1. 需要 Python3 环境，并 `pip install websocket-client`
2. 启动任意一个 OneBot 实现，如 `go-cqhttp` ,并打开正向 WS
3. 在 `voidbot.py` 文件中 注释位置编写你的插件
4. 直接运行 `voidbot.py` 文件


### 已经实现的API

###### onebot标准

- send_group_msg **发送群聊**
- send_private_msg **发送私聊**

你可以在[这里](https://github.com/botuniverse/onebot)查看onebot标准的文档



###### voidbot

- on_full_match **完全匹配消息**

  - 参数

    | 字段名  | 数据类型 | 说明 |
    | ------- | -------- | ---- |
    | keyword | 字符串   |      |

  - 响应数据

    | 字段名 | 数据类型 | 说明 |
    | ------ | -------- | ---- |
    |        | bool     |      |

- on_reg_match **正则匹配消息**

  - 参数

    | 字段名  | 数据类型 |                  |
    | ------- | -------- | ---------------- |
    | pattern | 字符串   | 匹配的正则表达式 |

  - 响应数据

    | 字段名 | 数据类型 | 说明 |
    | ------ | -------- | ---- |
    |        | bool     |      |

    