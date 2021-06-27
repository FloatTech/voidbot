# VoidBot
支持 OneBot 标准的 能跑就行 Python SDK 

- 极致轻量：一个文件，200 行代码实现了 80％ 常用开发功能
- 部署简单：Python环境上，只需再安装一个 `websocket-client` 库
- 代码简单：只需要 Python 入门即可读懂源码，参考[菜鸟教程](https://www.runoob.com/python3/python3-tutorial.html)
- 入门快速：无需文档即可直接接触到 OneBot 标准


### How to use

1. 安装 [Python](https://www.python.org/downloads/) 3.7 或以上 环境
2. 命令行中执行 `pip install websocket-client`
3. 启动任意一个 [OneBot](https://github.com/botuniverse/onebot/blob/master/ecosystem.md#onebot-%E5%AE%9E%E7%8E%B0) 实现，如 `go-cqhttp` ，并打开 `正向WS`
4. 在 `voidbot.py` 文件中 注释位置编写你的插件
5. 使用 `Python` 直接运行 `voidbot.py` 文件

你的插件通过基类 **Plugin** 的一个子类来实现。你只需要写一个继承 **Plugin** 的子类并重写 **match** 和 **handle** 方法就能快速实现插件功能


### 说明


###### API

|       API        |      功能      | 说明 |
| ---------------- | ------------- | ---- |
| send_msg         | 发送消息       |      |
| send_group_msg   | 发送群聊消息   |      |
| send_private_msg | 发送私聊消息   |      |

###### 消息段

| 消息段 |  功能   | 说明 |
| ------ | ------ | ---- |
| text   | 纯文本  |      |
| image  | 图片   |      |
| record | 语音   |      |
| at     | 艾特   |      |
| xml    | XML    |      |
| json   | JSON   |      |


###### 匹配

|       RULE        |       功能       | 说明 |
| ---------------- | ---------------- | ---- |
| on_full_match    | 完全匹配消息      |      |
| on_reg_match     | 正则匹配消息      |      |
| only_to_me       | 被艾特或者被喊名字 |      |
| super_user       | 发送者为主人      |      |
| admin_user       | 发送者为群管理    |      |


以上提供常用的封装，可按例子自行仿照扩充。你可以在[这里](https://github.com/botuniverse/onebot)查看 `OneBot` 标准的文档