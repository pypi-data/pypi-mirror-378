import logging
import os
import sys
import time
import asyncio
import threading
logger = logging.getLogger("uvicorn.access")
from tianxiadatong_wx_robot.wxauto import WeChat
from tianxiadatong_wx_robot import config,robot
from tianxiadatong_wx_robot.db import MessageDB
from tianxiadatong_wx_robot.wxauto.wx import WxParam
from tianxiadatong_wx_robot.models import MessageData

ws_client = None
# wx = None
def redeal_data():
    """掉线后重新处理历史数据"""
    # 4. 清空表
    robot.clear_table("messages")
    robot.clear_table("send_messages")


async def handle_server_message(message):
    robot.reply(message)

def init():
    robot.run_in_root()
    # db = MessageDB("wechat.db")  # SQLite 数据库
    db_path = os.path.join(os.path.dirname(__file__), "wxChat.db")
    db = MessageDB(db_path)  # SQLite
    config.db = db
    redeal_data()
    wx = WeChat()  # 初始化 WeChat
    config.wx = wx
    # 获取自己的微信群名
    config.my_wxName = wx.nickname
    WxParam.FORCE_MESSAGE_XBIAS = True  # 分辨率
    asyncio.create_task(robot.fetch_periodically3(60 * 60 * 24))
    # # 连接群管理工具 连接
    # ws_client = connector(config.ServerWebSocket_URL + config.my_wxName, handle_server_message)
    # config.ws_client = ws_client
    # asyncio.create_task(ws_client.connect())
    # await ws_client.connected_event.wait()

async def run_listening_msg():
    logger.info("开始轮询")
    # 启动后台消费者，千万别 await
    asyncio.create_task(process_wx_tasks())
    try:
        # 轮询 获取循环获取新消息（间隔 1 秒） 执行操作 轮询群
        while True:
            logger.info("----------")
            # await process_wx_tasks()
            result = config.wx.GetNextNewMessage(filter_mute=True)
            if result:
                logger.info(
                    f"新消息：会话: {result.get('chat_name')}-消息类型: {result.get('chat_type')}-消息内容：{result.get('msg')}")
            else:
                await deal_group_members()
                # logger.info("检查是否需要轮询所有群的群成员")
                # if not config.group_members_interval_time == 0 and time.time() - config.check_group_members_time_start > config.group_members_interval_time * 60:
                #     # 到点轮询所有群的群成员
                #     logger.info("开始轮询所有群的群成员")
                #     robot.search_all_groups_member()
                #     config.check_group_members_time_end = config.check_group_members_time_start = time.time()
            if result.get('chat_type') == "friend":
                # msg_data = MessageData(
                #     group_name=result.get('chat_name'),
                #     type="private",
                #     content="私聊消息",
                #     sender=result.get('chat_name'),
                #     msg_id=robot.get_msg_id(),
                #     quote_id="",
                #     quote_content="",
                #     recall_id="",
                #     image_url="",
                #     have_checked="true",
                #     status="",
                #     img_md5="",
                #     timestamp=robot.get_now(),
                # )
                # # 私人消息数据发送至群管
                # robot.robot_send_private_msg(msg_data)
                # # 私人消息数据入库
                # robot.update_db_messages(msg_data)
                await robot.deal_wx_msg(result.get("msg")[0],result.get("chat_name"),"friend")
            elif result.get('chat_type') and result.get('chat_type') == "group":  # 如果群有新消息
                # if result.get('chat_name') in config.groupName_list:
                #     nickname = result.get("chat_name")
                #     logger.info(f"收到群{nickname}的新消息")
                    # for msg in result.get("msg"):
                    #     if robot.is_record(msg) and nickname in config.groupName_list:
                    #         await robot.deal_msg(nickname)
                    # await robot.deal_msg(nickname)
                nickname = result.get("chat_name")
                await robot.deal_msg(nickname)
            else:
                # 轮询群
                await robot.check_group_member()
            await asyncio.sleep(2)
    finally:
        # 只关当前循环的 WebSocket
        if config.ws_client and config.ws_client.ws:
            asyncio.run_coroutine_threadsafe(
                config.ws_client.ws.close()
            )
        # 取消本循环内的任务即可，不要 shield 跨循环对象
        for task in asyncio.all_tasks(loop=asyncio.get_running_loop()):
            if task is not asyncio.current_task():
                task.cancel()
        print("已通知群管机器人下线，程序退出。")

def start_listening_msg(fun):
    # 获取所有群历史记录
    robot.getAllHistoricalNews()
    config.wx.SwitchToChat()
    # 测试执行的时间
    config._start_time = config._end_time = time.time()
    # 轮询群成员的间隔时间
    config.check_group_members_time_end = config.check_group_members_time_start = time.time()
    robot.deal_wx_msg = fun
    # 创建一个新线程来运行 run_listening_msg
    def run_in_new_loop():
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.run_until_complete(run_listening_msg())
        # try:
        #     loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(loop)
        #     config.wx_task_loop = loop
        #     config.wx_task_queue = asyncio.Queue()
        #     loop.create_task(process_wx_tasks())
        #     loop.run_until_complete(run_listening_msg())
        # except Exception as e:
        #     logger.exception("【致命】子线程协程崩溃：%s", e)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            config.wx_task_loop = loop
            config.wx_task_queue = asyncio.Queue()
            loop.create_task(process_wx_tasks())
            loop.run_until_complete(run_listening_msg())
        except Exception as e:
            logger.exception("【致命】子线程协程崩溃：%s", e)

    threading.Thread(target=run_in_new_loop, name="run_listening_msg", daemon=True).start()

def start_listening_group_members(fun):
    global deal_group_members  # 确保修改全局变量
    deal_group_members = fun

async def deal_group_members():
    print("deal_group_members")

# ==================== 任务消费者 ====================
async def process_wx_tasks():
    while True:
        task = await config.wx_task_queue.get()
        try:
            action = task["action"]
            kw   = task["kwargs"]
            if action == "SendMsg":
                _real_send_msg(**kw)
            elif action == "reply_with_quote":
                _real_reply_with_quote(**kw)
            elif action == "get_group_memberlist":
                # 只拿业务参数，去掉 task_id
                chat_name = kw["chat_name"]
                members = _real_get_group_memberlist(chat_name)  # 真列表
                task_id = kw["task_id"]
                fut = config.task_futures.pop(task_id, None)
                if fut and not fut.done():  # 关键：只写一次
                    fut.set_result(members)
            elif action == "get_img_md5":
                # 只拿业务参数，去掉 task_id
                content = kw["content"]
                task_id = kw["task_id"]
                md5_str = _real_get_img_md5(content)  # 返回 str
                fut = config.task_futures.pop(task_id, None)
                if fut and not fut.done():
                    fut.set_result(md5_str)
            # 后续扩展继续 elif ...
        except Exception as e:
            logger.exception("[wx-task] 执行失败: %s", e)

def _real_send_msg(content, who, at=None):
    config.wx.SendMsg(content, who=who, at=at)

def _real_reply_with_quote(msg_id, reply_text, chat_name, at=None):
    # robot.reply_with_quote(msg_id=msg_id, reply_text=reply_text, chat_name=chat_name, at=at)
    try:
        robot.reply_with_quote(msg_id=msg_id, reply_text=reply_text, chat_name=chat_name, at=at)
    except Exception as e:
        logger.exception("[wx-task] reply_with_quote 失败")

def _real_get_group_memberlist(chat_name: str):
    members = robot.get_group_memberlist(chat_name)   # 你已实现
    return members

def _real_get_img_md5(content: str):
    members = robot.get_img_md5(content)  # 你已实现
    return members