import os
import sys
import time
import json
import asyncio
import  uuid
import aiohttp
from typing import List
from tianxiadatong_wx_robot.wxauto import uiautomation as uia
from datetime import datetime, timedelta
from tianxiadatong_wx_robot import config
# import command
from tianxiadatong_wx_robot.wxauto.utils import (
    FindWindow,
)
from tianxiadatong_wx_robot.wxauto.ui.component import (
    WeChatImage,
)
import logging
logger = logging.getLogger("uvicorn.access")
import base64, hashlib
import requests
import win32clipboard as clip
import urllib.parse
from tianxiadatong_wx_robot.models import MessageData
from tianxiadatong_wx_robot.wxauto.wx import WxParam

def run_in_root():
    def is_admin():
        try:
            return os.getuid() == 0
        except AttributeError:
            # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin():
        # 重新以管理员权限运行
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()


def isOnline():
    """是否在线，异常保护"""
    try:
        hwnd = FindWindow(classname="WeChatMainWndForPC")
        if not hwnd:
            print("没有在线")
            config.offline_msg = "为了你的账号安全，请重新登录。"
            time.sleep(1)
            if click_confirm_button():
                return True
            return False
        print("在线")
        return False
    except Exception as e:
        print("isOnline 检查异常：", e)
        return False

# 主动退出的重登流程 和强制退出的不一样 估计是用不上了
def auto_relogin_wechat():
    """
    检测“你已退出微信”提示，自动点击“确定”按钮，然后点击“进入微信”按钮尝试重新登录。
    支持多开和不同窗口标题。异常保护。
    """
    try:
        # 1. 查找微信主窗口（宽松匹配）
        wx_window = None
        for w in uia.GetRootControl().GetChildren():
            if "微信" in w.Name:
                wx_window = w
                print(f"找到微信主窗口: {w.Name}")
                break
        if not wx_window:
            print("未找到微信主窗口")
            return False

        # 先激活并置顶窗口（可选，部分环境可能无效）
        try:
            wx_window.SetActive()
            wx_window.SetTopmost(True)
        except Exception as e:
            print("窗口激活/置顶异常：", e)

        # 2. 检查是否有“你已退出微信”提示
        logout_tip = wx_window.TextControl(Name='你已退出微信')
        if logout_tip.Exists(0, 0):
            print("检测到已退出微信，自动处理...")
            ok_btn = wx_window.ButtonControl(Name='确定')
            if ok_btn.Exists(0, 0):
                ok_btn.Click()
                print("已点击“确定”按钮")
                time.sleep(0.1)
            else:
                print("未找到“确定”按钮")
                return False
            enter_btn = wx_window.ButtonControl(Name='进入微信')
            if enter_btn.Exists(0, 0):
                enter_btn.Click()
                print("已点击“进入微信”按钮，等待登录")
                return True
            else:
                print("未找到“进入微信”按钮，请手动登录")
                return False
        else:
            print("微信处于登录状态")
            return True
    except Exception as e:
        print("auto_relogin_wechat 异常：", e)
        return False

# 强制下线的重登流程
def click_confirm_button():
    btn = uia.ButtonControl(Name='确定', searchDepth=6)   # 6 足够穿透所有 Pane
    if btn.Exists(2):
        btn.Click()
        time.sleep(1)
        login_btn = uia.ButtonControl(Name='登录', searchDepth=12, Timeout=0)  # 0 = 不等待
        if login_btn.Exists(0):
            login_btn.Click()
            return True
    else:
        print("未找到“确定”按钮")
        return False 


    
async def run_daily_at(hour, minute, func, *args, **kwargs):
    """
    定时每天某一时间执行func函数
    Args:
        :param hour: 某时
        :param minute: 某分
        :param func: 需要执行的函数
        :param *args: 任意数量的位置参数
        :param **kwargs: 任意数量的关键字参数
    """
    while True:
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        print(f"距离下次执行{func.__name__}还有{wait_seconds/3600:.2f}小时")
        await asyncio.sleep(wait_seconds)
        try:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            print(f"定时任务{func.__name__}异常: {e}")

# ========== 工具函数 ==========
def img_key(img_bytes: bytes) -> str:
    """生成可缓存的 32 位哈希"""
    return hashlib.md5(base64.b64encode(img_bytes)).hexdigest()

def get_msg_id():
    """
    生成msg_id
    Returns:
        int: msg_id
    """
    if not hasattr(get_msg_id, "last_ts"):
        get_msg_id.last_ts = 0
        get_msg_id.counter = 0
    ts = int(time.time())
    if ts != get_msg_id.last_ts:
        get_msg_id.last_ts = ts
        get_msg_id.counter = 0
    else:
        get_msg_id.counter += 1
    # 7位时间戳+3位计数器，拼成10位
    msg_id = f"{config.id前缀}{str(ts)[-4:]}{get_msg_id.counter:03d}"
    return msg_id


def is_later_by_2_minutes(time1_str, time2_str):
    """
    判断 time1_str 是否比 time2_str 晚 2 分钟以上。
    参数:
        time1_str (str): 时间字符串，格式为 "%Y-%m-%d-%H:%M:%S"
        time2_str (str): 时间字符串，格式同上
    返回:
        bool: 如果 time1 比 time2 晚 2 分钟以上，返回 True，否则返回 False。
    """
    fmt = "%Y-%m-%d-%H:%M:%S"
    t1 = datetime.strptime(time1_str, fmt)
    t2 = datetime.strptime(time2_str, fmt)
    return t1 > t2 + timedelta(minutes=2)


def get_now():
    """获取最新时间"""
    t = time.localtime()
    year = t.tm_year
    month = t.tm_mon
    day = t.tm_mday
    hour = t.tm_hour
    minute = t.tm_min
    second = t.tm_sec
    time_str = str(year) + "-"+ str(month) +"-"+ str(day) + "-" + str(hour) + ":" + str(minute) + ":"  + str(second)
    return time_str

# 数据库操作
# 更新group_member表 判断群名 无则创建，有则更新
def update_db_group_member(group_name,member):
    config.db.insert_group_member({
        "group_name":group_name,
        "member":json.dumps(member)
    })
    
# 更新messages表 判断群名 无则创建，有则更新
def update_db_messages(params):
    config.db.insert_messages(
        {
            "group_name": params.group_name,
            "type": params.type,
            "content": params.content,
            "sender": params.sender,
            "timestamp": get_now(),
            "msg_id": params.msg_id,
            "quote_id": params.quote_id,
            "quote_content": params.quote_content,
            "recall_id": params.recall_id,
            "image_url": params.image_url,
            "have_checked": params.have_checked,
            "status": params.status,
            "img_md5": params.img_md5,
        }
    )
    

def clear_table(table_name):
    with config.db.lock:
        cur = config.db.conn.cursor()
        cur.execute(f"DELETE FROM {table_name}")
        config.db.conn.commit()
        # print(f"表 '{table_name}' 数据已清空")


def delte_table(table_name):
    config.db.drop_table(table_name)
    print(f"表 '{table_name}' 已删除")


def get_group_message_count(group_name):
    """
    查询指定群名的消息记录数量
    Args:
        group_name (str): 群名，例如 "微信测试"
    Returns:
        int: 记录数量
    """
    count = config.db.get_message_count_by_group(group_name)
    return count


def insert_message_after_record(group_name, target_id, new_message_data):
    """
    在指定群名和id的记录下方插入一条新消息
    Args:
        group_name (str): 群名，例如 "xxxx"
        target_id (int): 目标记录的id，例如 79
        new_message_data (dict): 新消息数据
    """
    try:
        new_msg = {
            "type": new_message_data.get("type", "text"),
            "content": new_message_data.get("content", ""),
            "sender": new_message_data.get("sender", ""),
            "timestamp": get_now(),
            "msg_id": get_msg_id(),
            "quote_id": new_message_data.get("quote_id", ""),
            "quote_content": new_message_data.get("quote_content", ""),
            "recall_id": new_message_data.get("recall_id", ""),
            "image_url": new_message_data.get("image_url", ""),
            "status": "",
            "img_md5": "",
        }
        new_id = config.db.insert_after_record(group_name, target_id, new_msg)
        print(f"插入成功！新记录的id为: {new_id}")
        return new_id
    except ValueError as e:
        print(f"插入失败: {e}")
        return None
    except Exception as e:
        print(f"插入过程中发生错误: {e}")
        return None

# 构建集合，和qq端一样的结构 不过微信端number和name是一样的 例：[{'number': '2797138784', 'name': 'Bot_测试', 'group_id': '933808299'}]
def format_group_member(members, group_name):
    return [{'number': m, 'name': m, 'group_id': group_name} for m in members]
#
# def check_member_isnew(group_name, new_member_name):
#     """
#     检查这个成员是否为新加入
#     Args:
#         :param group_name: 群名
#         :param new_member_name: 成员名
#     """
#     print("检查这个成员是否还在群里")
#     members = config.wx.GetGroupMembers()
#     if new_member_name in members:
#         robot_send_member_increase(new_member_name, group_name)
#         # 先发新人入群消息，再发群成员列表
#         robot_send_group_memberlist(members,group_name)
#         update_db_group_member(group_name, members)

# def get_group_member_info(group_name, member_name):
#     """
#     获取群新成员名称
#     Args:
#         :param group_name: 群名
#         :param member_name: 成员名
#     """
#     try:
#         print(f"获取{group_name}成员{member_name}")
#         config.wx.ChatWith(who=group_name)
#         members = config.wx.GetGroupMembers()
#         for member in members:
#             if member == member_name:
#                 return member
#         return None
#     except Exception as e:
#         print("获取群成员信息失败", str(e))
#         return None

# 其它函数继续迁移...

def is_add(chat_content, db_content):
    """
    与数据库的数据对比，判断新人入群新消息是否需要添加到数据库
    
    Args:
        chat_content (str): 聊天窗口的新人入群消息内容
        db_content (int): 数据库的新人入群消息内容
    """
    if chat_content == db_content:
        return True
    return False

def is_new_member_message(msg):
    """
    识别新成员入群消息
    Args:
        :param msg: 群消息内容
    """
    
    if msg.get("type") == "base" and ("加入群聊" in msg.get('content') or "加入了群聊" in msg.get('content')) :
        return True
    return False

def extract_new_member_names(content):
    """
    从消息内容中提取新成员名称
    Args:
        :param content: 消息内容
    """
    if "加入了群聊" in content or "加入群聊":
        return content.split("\"")[1].replace('"',"")
    return None

async def send(msg_data):
    await config.ws_client.send(json.dumps(msg_data))

# def search_groups_member(chat_name):
#     """
#     查找目标群的群成员
#     Args:
#         :param chat_name: 目标群
#     """
#     # 1. 切换到目标会话
#     config.wx.ChatWith(chat_name)
#     # 2. 查找群成员
#     members = config.wx.GetGroupMembers()
#     # 3. 发送群管
#     robot_send_group_memberlist(members, chat_name)
#     # 4. 数据入库
#     update_db_group_member(chat_name, members)

def get_group_memberlist(chat_name):
    """
    查找目标群的群成员
    Args:
        :param chat_name: 目标群
    """
    # 1. 切换到目标会话
    config.wx.ChatWith(chat_name)
    # 2. 查找群成员
    members = config.wx.GetGroupMembers()
    # 4. 数据入库
    update_db_group_member(chat_name, members)
    return members

# def search_all_groups_member():
#     """查找所有群的群成员"""
#     for name in config.groupName_list:
#         search_groups_member(name)

def reply_with_quote(msg_id, reply_text, chat_name, at=None):
    """
    通过 msg.id 定位消息并引用回复
    Args:
        :param msg_id: 目标消息的 id（字符串）
        :param reply_text: 要回复的文本内容
        :param chat_name: 要回复的群名
    """
    # 1. 切换到目标会话
    try:
        config.wx.ChatWith(chat_name)
        record = config.db.get_latest_messages(1,group_name =chat_name, msg_id=msg_id)
        if record and not record[0].get("recall_id"):
            while True:
                # 2. 获取当前窗口的消息
                messages = config.wx.GetAllMessage()
                # 3. 遍历查找目标消息
                target_msg = None
                reversed_messages = list(reversed(messages))
                for msg in reversed_messages:
                    if record[0].get("sender") == getattr(msg, "sender", None) and record[0].get("content") == getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", "").split("引用  的消息 :")[0].rstrip():
                        target_msg = msg
                        break
                if target_msg:
                    break
                else:
                    # 加载更多信息
                    config.wx.LoadMoreMessage()
            # 4. 引用并回复
            if at:
                getattr(target_msg, "quote", lambda *a, **k: None)(reply_text, at)
            else:
                getattr(target_msg, "quote", lambda *a, **k: None)(reply_text)
            logger.info(f"已在{chat_name} 中引用回复id={msg_id} 的消息。")
        # else:
        #     print("消息不存在")
    except Exception as e:
        print("发送消息失败", str(e))



# def reply(msg_data):
#     command = msg_data.get('command')
#     message = msg_data.get('message')
#     if command == "regular-send": #群管to机器人 发一条普通消息(无@)
#         config.wx.SendMsg(message.get('content'), who=message.get('position'))
#     elif command == "regular-reply": #群管to机器人 发一条引用回复消息
#         reply_with_quote(msg_id=message.get('sequence'), reply_text=message.get('content'), chat_name=message.get('position'))
#     elif command == "at-send": #群管to机器人 发一条消息(带@)
#         config.wx.SendMsg(message.get('content'), who=message.get('position'), at=message.get('receiver'))
#     elif command == "reply-and-at":  # 群管to机器人 又要引用又要@
#         reply_with_quote(msg_id=message.get('sequence'), reply_text=message.get('content'), chat_name=message.get('position'), at=message.get('receiver'))
#     elif command == "sync-group-member":  # 群管端要求机器人提供群成员列表
#         search_groups_member(message.get('group_id'))
#     elif command == "send-private-message": # 群管端to机器人 回复私人会话
#         config.wx.SendMsg(message.get('content'), who=message.get('receiver'))
#     elif command == "msg-ack": # 确认消息群管已经接受到
#         # config.db.update_message_fields("msg_id", message.get('sequence'), {"status": 200})
#         config.db.update_send_message_fields("send_id",message.get('send_id'),{"status": "发送成功"})
#     # elif command == "at-all": # 群管to机器人 要求发送得所有群成员
#     #     config.wx.AtAll(message.get('content'), who=message.get('position'))



def collect_group_names():
    """收集所有微信群聊名称"""
    config.wx.SwitchToContact()
    config.groupName_list = config.wx.CollectAllGroupNames()
    config.wx.SwitchToChat()
    time.sleep(0.2)

def getHistoricalNews(nickname):
    config.wx.ChatWith(nickname)
    # config.firstCheckGroup[nickname] = True
    logger.info(f"数据库中暂无群：{nickname} 消息记录,直接记录不需要操作")
    messages = config.wx.GetAllMessage()
    history_msg = []
    for msg in messages:
        if is_record(msg):
            msg_type = getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("type", "")
            params =  MessageData(
                group_name= nickname,
                type= msg_type,
                content= getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", "").split("引用  的消息 :")[0].rstrip(),
                sender=getattr(msg, "sender", None),
                msg_id=get_msg_id(),
                quote_id= "",
                quote_content= "",
                recall_id= "",
                image_url= "",
                have_checked= "true",
                status= "200",
                img_md5= "",
                timestamp= get_now(),
            )

            if getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("attr", "") == 'self':
                continue
            
            # 如果是引用消息
            if msg_type == "other" and "引用  的消息 :" in getattr(msg, "content", ""):
                params.quote_content = getattr(msg, "content", "").split("引用  的消息 :")[1].lstrip()
                #先从当前数据查看 信息的id 如果是图片引用，默认个人最新一条图片信息 不做处理,如果是文字则是选上一条
                for m in history_msg:
                    if params.quote_content == m.content:
                        params.quote_id = m.msg_id
                        break  
            if msg_type == "base" and "撤回了一条消息" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", ""):
                params.recall_id = get_msg_id()
                params.type = 'text'
            if msg_type == "image" and msg.info.get('attr') == 'friend':
                path,filename  = msg.download()
                if path:
                    raw_bytes = open(path, 'rb').read()  
                    params.img_md5 =  img_key(base64.b64encode(raw_bytes))
                else:
                    logger.error("图片下载失败")
                    continue
            if msg.info.get('attr') == 'self':
                params.type = 'self'
                params.sender= config.my_wxName
            history_msg.append(params)
    # 数据入库
    for item in history_msg:
        update_db_messages(item)
    # 该群已经初始化聊天已经录入成功
    config.firstCheckGroup[nickname] = True
    logger.info(f"已初始化所有群聊天消息")

def getAllHistoricalNews():
    try:
        logger.info("获取监听所有群的历史消息")
        response = requests.get(config.get_listening_group_url + config.my_wxName).json()
        if response.get("code") == 200:
            config.groupName_list = [item['name'] for item in response['data']]            
            for nickname in config.groupName_list:
                getHistoricalNews(nickname)
    except Exception as e:
        print(e)

        
def deal_wx_msg(msg, nickname,type):
    print(f"处理群 {nickname}的消息：{msg}")
    return {}

def is_record(msg):
    msg_type = getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("type", "")
    if msg_type in ["text", "other", "image", "base"]:
        if msg_type == "other" and "base" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("attr", ""):
            # continue
            return False
        if msg_type == "base" and "time" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("attr", ""):
            # continue
            return False
        if msg_type == "base" and msg.info.get('attr') == 'system' and "下为新消息" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", ""):
            # continue
            return False
        return True
    return False

async def db_update_msg(msg, nickname):
    """
    处理当前窗口消息 新人加群 撤回信息 新消息
    Args:
        :param msg: 消息
        :param nickname: 群名
    """
    # print("db_update_msg")
    params = await deal_wx_msg(msg, nickname, "group")
    msg_type = getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("type", "")
    msg_data = MessageData(
        group_name= nickname,
        type= msg_type,
        content= getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", "").split("引用  的消息 :")[0].rstrip(),
        sender= getattr(msg, "sender", None),
        msg_id= params.sequence,
        quote_id= "",
        quote_content= "",
        recall_id= "",
        image_url= "",
        have_checked= "false",
        status= "",
        img_md5= "",
        timestamp= get_now(),
    )
    #
    # send_data = SendMessageData(
    #     sender= getattr(msg, "sender_remark", None),
    #     receiver= config.my_wxName,
    #     position= nickname,
    #     sequence= msg_data.msg_id,
    #     channel= config.my_wxName,
    #     type= "text",
    #     image= "",
    #     reply= "",
    #     content= msg_data.content
    # )
    #
    if msg_type == "image":
    #     send_data.type = "image"
    #     # 下载图片 默认WxParam.DEFAULT_SAVE_PATH
    #     path,filename  = msg.download()
    #     url = await obsClient.push(path,filename)
    #     # url = "https://tianxiadatong.obs.cn-south-1.myhuaweicloud.com/wxauto_image_20250708160435.png"
        msg_data.image_url = params.image
    #     send_data.image = url
        raw_bytes = open(WxParam.DEFAULT_SAVE_PATH +"\\" +params.image, 'rb').read()
        msg_data.img_md5 =  img_key(base64.b64encode(raw_bytes))
    elif msg_type == "other":
    #     # 微信引用不能发图片
    #     msg_data.quote_content = getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", "").split("引用  的消息 :")[1].lstrip() if "引用  的消息 :" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", "") else ""
    #     latest_msg_quote = []
    #     if msg_data.quote_content == '[图片]':
    #         img_md5 = get_img_md5(msg_data.content)
    #         latest_msg_quote = config.db.get_latest_messages(1, group_name=nickname, img_md5=img_md5)
    #     else:
    #         latest_msg_quote = config.db.get_latest_messages(1, group_name=nickname, content=msg_data.quote_content)
    #     # 查找引用的msg_id
    #     if latest_msg_quote:
    #         msg_data.quote_id = latest_msg_quote[0].get("msg_id")
    #         send_data.reply  = latest_msg_quote[0].get("msg_id")
        msg_data.quote_content = params.quote_content
        msg_data.quote_id = params.reply
    elif msg_type == "base" and "撤回了一条消息" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", ""):
        msg_data.recall_id = get_msg_id()
        # 撤回的消息 只入库 不发群管
        # update_db_messages(msg_data)
    #     return
    elif msg.info.get('attr') == 'self':
        msg_data.type = 'self'
        msg_data.sender= config.my_wxName
    #     # 机器人的话 只入库 不发群管
    #     update_db_messages(msg_data)
    #     return
    elif is_new_member_message(msg.info):
    #     new_member_name = extract_new_member_names(getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", ""))
        msg_data.have_checked = "true"
        update_db_messages(msg_data)
    #     robot_send_member_increase(new_member_name, nickname)
    #     return
    elif msg_type != "text":
        return
    update_db_messages(msg_data)
    # robot_send_group_msg(send_data)


# # 对比三条消息是否一致
# def match_and_slice(wx_list, db_list):
#     db_len = len(db_list)
#     print(wx_list)
#     print(db_list)
    
#     for start in range(len(wx_list) - db_len, -1, -1):
#         # 1. 逐字段完全匹配 额外触发条件撤回默认成立
#         matched = all(
#             (wx_list[start + i].info['type']   == db_list[i]['type'] and
#             wx_list[start + i].info['content'].split("引用  的消息")[0].rstrip() == db_list[i]['content'] and
#             wx_list[start + i].sender == db_list[i]['sender']) or (wx_list[start].info['type'] == 'base' and
#             '撤回了一条消息' in wx_list[start]['content'])
#             for i in range(db_len)
#         )
#         if matched:
#             return wx_list[start + db_len:]
#     return []

def match_and_slice(wx_list, db_list):
    db_len = len(db_list)
    # 避免打印过多冗余信息，只打印关键调试内容
    # print("待匹配的db_list：", db_list)
    
    # 从后往前遍历可能的起始位置（确保截取长度>=db_len）
    for start in range(len(wx_list) - db_len, -1, -1):
        # 检查当前start开始的db_len条消息是否与db_list完全匹配
        matched = all(
            # 条件1：正常消息匹配（type一致 + 内容处理后一致）
            (wx_list[start + i].info['type'] == db_list[i]['type'] and
             wx_list[start + i].info['content'].split("引用  的消息")[0].rstrip('\n').rstrip() == db_list[i]['content'])
            # 条件2：撤回消息匹配（当前消息type为base + 含撤回关键词）
            or (wx_list[start + i].info['type'] == 'base' and '撤回了一条消息' in wx_list[start + i].info['content'])
            for i in range(db_len)
        )
        if matched:
            # logger.info(f"匹配成功！匹配片段：{[msg.info['content'] for msg in wx_list[start:start+db_len]]}")
            # logger.info(f"匹配后的剩余消息:{wx_list[start + db_len:]}")
            if wx_list[start + db_len:]:
                return wx_list[start + db_len:]  # 返回匹配后的剩余消息
            return ["true"]
            
    # print("未匹配")
    return []

def check_more_message(db_message):
    db_message =list(reversed(db_message))
    logger.info("比对信息")
    wx_message = []
    count = 0
    while True:
        try:
            messages = config.wx.GetAllMessage()
        except Exception as e:
            logger.info(f"获取消息失败: {e}")
            return
        wx_message = []
        for msg in messages:
            if is_record(msg) and not "self" == msg.info.get("attr"):
                wx_message.append(msg)
        # 从后往前滑
        add_list = match_and_slice(wx_message,db_message)
        if add_list:
            if add_list[0] == "true":
                return []
            return add_list
        if count >=2:
            return []
        else:
            count+=1
            config.wx.LoadMoreMessage()
    

async def deal_msg(nickname):
    """
    处理当前窗口消息 新人加群 撤回信息 新消息
    Args:
        :param nickname: 群名
    """
    config.wx.ChatWith(nickname)
    # 检查是否是未检查的新群
    logger.info("检查新消息")
    if config.firstCheckGroup.get(nickname):
        latest_have_input_msg = config.db.get_latest_messages(3, group_name=nickname, type=["other", "text","image","base"])
        length = len(latest_have_input_msg)
        messages = config.wx.GetAllMessage()
        reversed_messages = list(reversed(messages))
        temp_list = []
        if latest_have_input_msg:
            if length <= 2:
                # 数据库少于2条，则单条做对比
                temp_list = []
                if latest_have_input_msg:
                    # 有消息录入
                    for index, msg in enumerate(reversed_messages):
                        msg_type = getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("type", "")
                        if "撤回了一条消息" in msg.info.get("content") and latest_have_input_msg[0].get("type") in ["text","other","image"]:
                            break
                        # 发送者和人相同 则说明相同
                        if latest_have_input_msg[0].get("content") == msg.info.get("content") and latest_have_input_msg[0].get("sender") ==  msg.sender:
                            # 图片比对的是md5
                            if msg.info.get("content") == '[图片]':
                                path,filename  = msg.download()
                                raw_bytes = open(path, 'rb').read()
                                img_md5 =  img_key(base64.b64encode(raw_bytes))
                                try:
                                    if os.path.isfile(path):
                                        os.remove(path)
                                except Exception as e:
                                    logger.info(e)
                                if latest_have_input_msg[0].get("img_md5") ==  img_md5:
                                    break
                            else:
                                break
                        # 系统消息相同
                        if msg_type == "base" and latest_have_input_msg[0].get("content") in msg.info.get("content"):
                            break
                        # 引用的消息 需要先处理一下 再比对
                        if  msg_type == "other":
                            text0 =  msg.info.get("content").split("引用  的消息")[0].rstrip()
                            if latest_have_input_msg[0].get("content") == text0:
                                break

                        if "self" == msg.info.get("attr"):
                            continue

                        if is_record(msg):
                            temp_list.insert(0,msg)
            else:
                # 判断三条消息的情况
                temp_list = check_more_message(latest_have_input_msg)
        else:
            for msg in messages:
                if is_record(msg):
                    temp_list.append(msg)
        if temp_list:
            logger.info("检查到需要处理的信息，处理新消息")
            for msg in temp_list:
                await db_update_msg(msg, nickname)
    elif nickname in config.groupName_list:
        getHistoricalNews(nickname)
    logger.info("检查撤回新人加入")
    # 数据库是否有消息
    group_msg_num_in_db = get_group_message_count(nickname)
    if group_msg_num_in_db > 0:
        # print("数据库中有此群消息记录,获取超过上次查询的2分钟的记录，进行对比")
        now_time = get_now()
        latest_no_check_msg = config.db.get_all_messages(group_name=nickname, have_checked="false", type=["other", "text","image"])
        length = len(latest_no_check_msg)
        count = 0
        chat_text_list = []
        if latest_no_check_msg:
            while True:
                temp_chat_text_list = []
                try:
                    messages = config.wx.GetAllMessage()
                    reversed_messages = list(reversed(messages))
                except Exception as e:
                    print(f"获取消息失败: {e}")
                    return
                for msg in reversed_messages:
                    msg_type = getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("type", "")
                    if msg_type in ["text", "other","image"]:
                        if msg_type == "other" and "base" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("attr", ""):
                            continue
                        if getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("attr", "") == "self":
                            continue
                        temp_chat_text_list.insert(0, getattr(msg, "info", {}))
                        if len(temp_chat_text_list) == length:
                            break
                    elif msg_type == 'base' and hasattr(msg, "info") and "撤回了一条消息" in getattr(getattr(msg, "info", {}), "get", lambda x, y=None: None)("content", ""):
                        temp_chat_text_list.insert(0, getattr(msg, "info", {}))
                        if len(temp_chat_text_list) == length:

                            break
                if len(temp_chat_text_list) == length:
                    chat_text_list = temp_chat_text_list
                    break
                elif count == 2:
                    return
                else:
                    count +=1
                    config.wx.LoadMoreMessage()
            # 检查处理撤回
            for index, msg in enumerate(chat_text_list):
                if hasattr(msg, "get") and "撤回了一条消息" in msg.get("content", "") and not latest_no_check_msg[index].get("recall_id"):
                    config.db.update_message_fields("id", latest_no_check_msg[index].get("id"), {"recall_id": get_msg_id()})
                    # robot_send_message_withdraw(latest_no_check_msg[index].get("msg_id"),nickname)
                    await deal_wx_msg(latest_no_check_msg[index],nickname,"withdraw")
                elif is_later_by_2_minutes(now_time, latest_no_check_msg[index].get("timestamp")):
                    config.db.update_message_fields("id", latest_no_check_msg[index].get("id"), {"have_checked": "true"})

async def check_group_member():
    """检查哪些群需要轮询"""
    import time
    global_start_time = getattr(config, "_start_time", None)
    if global_start_time is None:
        config._start_time = time.time()
    if not config.groupName_list:
        return
    elif len(config.groupName_list) == len(getattr(config, "have_check_groupName_list", [])):
        config.have_check_groupName_list = []
        config._end_time = time.time()
        logger.info(f"新一轮轮询，上一轮轮询用时{config._end_time - config._start_time}秒，涉及群{len(config.groupName_list)}个")
        config._start_time = time.time()
    else:
        prev_list = set(config.groupName_list)
        curr_list = set(getattr(config, "have_check_groupName_list", []))
        removed_list = prev_list - curr_list
        if removed_list:
            removed_name = removed_list.pop()
            config.have_check_groupName_list.append(removed_name)
            logger.info(f"轮询到群{removed_name}")
            await deal_msg(removed_name)
            logger.info(f"完成轮询群{removed_name}，等待时间")
            await asyncio.sleep(3)


# def collect_one_group_member(chatname):
#     config.wx.ChatWith(chatname)
#     group_list = []
#     rows = config.db.query("SELECT member FROM group_member WHERE group_name = ?", (chatname,))
#     if rows:
#         group_list = json.loads(rows[0][0])
#     members = config.wx.GetGroupMembers()
#     #转化成set可以相减
#     prev_members = set(group_list)
#     curr_members = set(members)
#     # 减少的
#     removed_members = prev_members - curr_members
#     if removed_members:
#         print(f"发现退群成员{list(removed_members)}")
#         for member in removed_members:
#             robot_send_member_decease(member,chatname)
#     print(f"群成员：{members}")
#     update_db_group_member(chatname, members)

# 从原文位置返回到引用的消息位置
def return_run_to_msg():
    # 1. 主窗口
    wechat = uia.WindowControl(searchDepth=1, Name='微信')
    # 2. 直接定位“回到引用位置”按钮
    btn = wechat.ButtonControl(Name='回到引用位置', foundIndex=1)
    if btn.Exists(1):
        btn.Click()
        print('已点击“回到引用位置”')
    else:
        print('按钮未找到，请确认窗口已打开且消息已加载')

# 右击引用内容，跳转至原文位置
def run_to_msg(content):
    # 1. 主窗口
    wechat = uia.WindowControl(searchDepth=1, Name='微信')
    # 2. 在聊天窗口里找消息列表
    msg_list = wechat.ListControl(Name='消息')
    if not msg_list.Exists(0.5):
        raise RuntimeError('未找到消息列表')
    # 3. 在消息列表里找包含“修改”的那条 ListItem
    modify_msg = None
    for item in msg_list.GetChildren():
        if content in item.Name:
            modify_msg = item
            break
    if modify_msg is None:
        raise RuntimeError('消息列表中未出现该信息')
    # 4. 找到按钮并右键
    btn = modify_msg.PaneControl(foundIndex=1) \
        .PaneControl(foundIndex=1) \
        .ButtonControl(foundIndex=1)
    if btn.Exists(0.5):
        btn.RightClick()
        print('已右键“修改”消息')
        # 等菜单渲染出来
        item = wechat.MenuItemControl(Name='定位到原文位置', foundIndex=1)
        if item.Exists(0.5):
            item.Click()
            print('已定位到原文位置')
        else:
            print('菜单未弹出或控件未渲染')
    else:
        print('按钮层级异常，请 inspect.exe 确认')

# CF_HDROP 原文件字节流 MD5 结果100% 一致
def clipboard_image_to_base64():
    clip.OpenClipboard()
    try:
        if clip.IsClipboardFormatAvailable(clip.CF_HDROP):
            files = clip.GetClipboardData(clip.CF_HDROP)
            img_path = files[0]
            with open(img_path, 'rb') as f:
                return base64.b64encode(f.read())
        else:
            raise ValueError("剪贴板无文件")
    finally:
        clip.CloseClipboard()

def copy_img(btn):
    # 4. 等待菜单出现，并点击“复制”
    time.sleep(0.3)                      # 菜单渲染
    btn.RightClick()
    copy_btn = uia.MenuItemControl(Name='复制')
    if copy_btn.Exists(0.5):
        copy_btn.Click()
        base = clipboard_image_to_base64()
        if imagewnd := WeChatImage():
            imagewnd.close()
        return img_key(base)
    else:
        print('未找到复制菜单项')
    return ''

def get_img_md5(content):
# 1. 主窗口
    wechat = uia.WindowControl(searchDepth=1, Name='微信')
    # 2. 在聊天窗口里找消息列表
    msg_list = wechat.ListControl(Name='消息')
    if not msg_list.Exists(0.5):
        raise RuntimeError('未找到消息列表')
    # 3. 在消息列表里找包含“修改”的那条 ListItem
    modify_msg = None
    for item in msg_list.GetChildren():
        if content in item.Name:
            modify_msg = item
            break
    if modify_msg is None:
        raise RuntimeError('消息列表中未出现该信息')
    # 4. 找到按钮并右键
    btn = modify_msg.PaneControl(foundIndex=1) \
        .PaneControl(foundIndex=1) \
        .ButtonControl(foundIndex=1)
    if btn.Exists(0.5):
        btn.Click()
        return copy_img(btn)
    else:
        print('按钮层级异常，请 inspect.exe 确认')
    return ""



def fetch_url(host, path):
    import http.client
    conn = http.client.HTTPSConnection(host)
    conn.request("GET", path)
    response = conn.getresponse()
    data = response.read().decode()
    conn.close()
    return data

# async def fetch_periodically(url, interval):

#     parsed = urllib.parse.urlparse(url)
#     host = parsed.hostname
#     # 编码 path
#     path = urllib.parse.quote(parsed.path)
#     # 编码 query
#     query = parsed.query
#     if query:
#         # 解析成字典再编码，防止重复编码
#         query_dict = urllib.parse.parse_qs(query)
#         query_encoded = urllib.parse.urlencode({k: v[0] for k, v in query_dict.items()}, doseq=True)
#         path += "?" + query_encoded
#     is_https = parsed.scheme == "https"
#     while True:
#         try:
#             send_robot_online()
#             def fetch():
#                 conn_class = http.client.HTTPSConnection if is_https else http.client.HTTPConnection
#                 conn = conn_class(host, parsed.port or (443 if is_https else 80))
#                 conn.request("GET", path)
#                 response = conn.getresponse()
#                 data = response.read().decode()
#                 conn.close()
#                 return data
#             result = await asyncio.to_thread(fetch)
#             result_obj = json.loads(result)
#             if result_obj.get("code") == 200:
#                 if result_obj["data"]:
#                     config.groupName_list = [item['name'] for item in result_obj['data']]
#                 else:
#                     config.groupName_list = []
#                 # config.groupName_list = ["我们的测试群2","我们的测试群"]
#                 # config.groupName_list = ["我们的测试群2"]
#             # print(f"接口返回: {config.groupName_list}")
#             for item in config.firstCheckGroup:
#                 if item in config.groupName_list:
#                     config.firstCheckGroup[item] = True
#                 else:
#                     config.firstCheckGroup[item] = False
#                 # if item in
#         except Exception as e:
#             print(f"请求出错: {e}")
#         await asyncio.sleep(interval)

# async def fetch_periodically(url: str, interval: int):
#     """
#     每 `interval` 秒异步 GET 拉取群列表，更新 config.groupName_list
#     使用原生 aiohttp，零线程阻塞。
#     """
#     # 解析 URL，提取 host / path / query
#     parsed = urllib.parse.urlparse(url)
#     host   = parsed.hostname
#     port   = parsed.port or (443 if parsed.scheme == "https" else 80)
#     path   = urllib.parse.quote(parsed.path)
#     query  = parsed.query
#     if query:
#         query_dict = urllib.parse.parse_qs(query, keep_blank_values=True)
#         query_encoded = urllib.parse.urlencode({k: v[0] for k, v in query_dict.items()}, doseq=True)
#         path += "?" + query_encoded

#     # 统一目标 URL（aiohttp 支持直接传 str，也可手动拼）
#     target_url = f"{parsed.scheme}://{host}:{port}{path}"

#     while True:
#         try:
#             await send_robot_online()          # 上报机器人存活（同步函数，很快）
#             async with aiohttp.ClientSession(
#                 timeout=aiohttp.ClientTimeout(total=10)
#             ) as session:
#                 async with session.get(target_url) as resp:
#                     if resp.status != 200:
#                         logger.warning(f"群列表接口返回 {resp.status}")
#                         continue
#                     result_obj = await resp.json()
#                     if result_obj.get("code") == 200:
#                         config.groupName_list = [item['name'] for item in result_obj.get("data", [])]
#                     else:
#                         config.groupName_list = []

#                     # firstCheckGroup 布尔映射
#                     for item in config.firstCheckGroup:
#                         config.firstCheckGroup[item] = item in config.groupName_list

#         except Exception as e:
#             logger.error(f"请求群列表出错: {e}")
#         await asyncio.sleep(interval)

# async def fetch_periodically(url: str, interval: int):
#     """严格每 `interval` 秒执行一次，不受任务耗时影响。"""
#     while True:
#         await asyncio.sleep(interval)      # ✅ 先等满周期
#         try:
#             await send_robot_online()      # 再发心跳
#             async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
#                 async with session.get(url) as resp:
#                     if resp.status != 200:
#                         logger.warning(f"群列表接口返回 {resp.status}")
#                         continue
#                     result_obj = await resp.json()
#                     if result_obj.get("code") == 200:
#                         config.groupName_list = [item['name'] for item in result_obj.get("data", [])]
#                     else:
#                         config.groupName_list = []
#                     # 布尔映射
#                     for item in config.firstCheckGroup:
#                         config.firstCheckGroup[item] = item in config.groupName_list
#         except Exception as e:
#             logger.error(f"请求群列表出错: {e}")

# async def fetch_periodically2(url, interval):
#     parsed = urllib.parse.urlparse(url)
#     host = parsed.hostname
#     # 编码 path
#     path = urllib.parse.quote(parsed.path)
#     # 编码 query
#     query = parsed.query
#     if query:
#         # 解析成字典再编码，防止重复编码
#         query_dict = urllib.parse.parse_qs(query)
#         query_encoded = urllib.parse.urlencode({k: v[0] for k, v in query_dict.items()}, doseq=True)
#         path += "?" + query_encoded
#     is_https = parsed.scheme == "https"
#     while True:
#         try:
#             def fetch():
#                 conn_class = http.client.HTTPSConnection if is_https else http.client.HTTPConnection
#                 conn = conn_class(host, parsed.port or (443 if is_https else 80))
#                 conn.request("GET", path)
#                 response = conn.getresponse()
#                 data = response.read().decode()
#                 conn.close()
#                 return data
#             result = await asyncio.to_thread(fetch)
#             result_obj = json.loads(result)
#             if result_obj.get('code') == 200:
#                 config.group_members_interval_time = result_obj.get("data").get("config_value")
#                 if config.group_members_interval_time == 0:
#                     logger.info("自动同步群成员未开启")
#                 else:
#                     logger.info(f"自动同步群成员已开启，间隔时间:{config.group_members_interval_time}分钟")
#             else:
#                 config.groupName_list = []
#                 logger.info("获取轮询群成员间隔时间失败")
#         except Exception as e:
#             print(f"请求出错: {e}")
#         await asyncio.sleep(interval)
#
# async def fetch_periodically2(url: str, interval: int):
#     """
#     每 `interval` 秒异步 GET 获取「群成员轮询间隔」配置，
#     更新 config.group_members_interval_time（分钟）。
#     使用原生 aiohttp，零线程阻塞。
#     """
#     parsed = urllib.parse.urlparse(url)
#     host   = parsed.hostname
#     port   = parsed.port or (443 if parsed.scheme == "https" else 80)
#     path   = urllib.parse.quote(parsed.path)
#     query  = parsed.query
#     if query:
#         query_dict = urllib.parse.parse_qs(query, keep_blank_values=True)
#         query_encoded = urllib.parse.urlencode({k: v[0] for k, v in query_dict.items()}, doseq=True)
#         path += "?" + query_encoded
#
#     target_url = f"{parsed.scheme}://{host}:{port}{path}"
#
#     while True:
#         try:
#             async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
#                 async with session.get(target_url) as resp:
#                     if resp.status != 200:
#                         logger.warning(f"轮询间隔接口返回 {resp.status}")
#                         continue
#
#                     result_obj = await resp.json()
#                     if result_obj.get('code') == 200:
#                         config.group_members_interval_time = result_obj.get("data", {}).get("config_value", 0)
#                         if config.group_members_interval_time == 0:
#                             logger.info("自动同步群成员未开启")
#                         else:
#                             logger.info(f"自动同步群成员已开启，间隔时间: {config.group_members_interval_time} 分钟")
#                     else:
#                         logger.info("获取轮询群成员间隔时间失败")
#
#         except Exception as e:
#             logger.error(f"请求轮询间隔出错: {e}")
#
#         await asyncio.sleep(interval)

async def fetch_periodically3(interval: int):
    """严格每 `interval` 秒执行一次，不受任务耗时影响。"""
    while True:
        await asyncio.sleep(interval)      # ✅ 先等满周期
        try:
            cleanup_sent_messages_hard()
        except Exception as e:
            logger.error(f"数据库操作出错: {e}")

# ServerWebSocket_URL = "ws://trade.dongxishi.com.cn/api/conn/wx/tunnel/"


def cleanup_sent_messages_hard():
    """每天 0 点硬删除所有 status='已发送' 的记录"""
    with config.db.lock:  # 复用原对象的锁
        cur = config.db.conn.cursor()
        cur.execute("DELETE FROM messages WHERE status = '发送成功'")
        rows = cur.rowcount
        config.db.conn.commit()
    # logging.info("[scheduler] 每日硬删除完成，删除 %d 条记录", rows)

# # 机器人在线消息
# async def send_robot_online():
#     # asyncio.create_task(send(command.online_payload()))
#     await send(command.online_payload())
#
# #机器人下线消息
# def send_robot_offline():
#     asyncio.create_task(send(command.offline_payload()))
#
# #机器人收到私人消息
# def robot_send_private_msg(info):
#     asyncio.create_task(send(command.private_conv_payload(info)))
#
# #机器人收到群消息
# def robot_send_group_msg(info):
#     asyncio.create_task(send(command.received_message_payload(info)))
#
# #机器人检查到新成员入群
# def robot_send_member_increase(new_member_name, group_name):
#     asyncio.create_task(send(command.group_member_increase_payload(new_member_name, group_name)))
#
# #机器人检查到成员退群
# def robot_send_member_decease(member_name, group_name):
#     asyncio.create_task(send(command.group_member_decease_payload(member_name, group_name)))
#
# #机器人检查到消息撤回
# def robot_send_message_withdraw(seq:str,group_name:str):
#     asyncio.create_task(send(command.message_withdraw_payload(seq, group_name)))
#
# #机器人发送群成员列表
# def robot_send_group_memberlist(members:List,group_name:str):
#     asyncio.create_task(send(command.group_memberlist_payload(format_group_member(members, group_name))))

# 投送壳：service.py 里直接调这些函数，无需改动
def wx_send_msg(content: str, who: str, at: str = None):
    _put_task("SendMsg", content=content, who=who, at=at)

def wx_reply_with_quote(msg_id: str, reply_text: str, chat_name: str, at: str = None):
    _put_task("reply_with_quote", msg_id=msg_id, reply_text=reply_text, chat_name=chat_name, at=at)

def wx_send_private_msg(content: str, who: str):
    _put_task("SendMsg", content=content, who=who)

# def wx_get_group_memberlist(chat_name: str):
#     _put_task("get_group_memberlist", chat_name=chat_name)

# 内部辅助：把任务扔进子线程队列
def _put_task(action: str, **kwargs):
    if not (config.wx_task_loop and config.wx_task_queue):
        logger.error("[robot] 子线程循环未就绪，丢弃任务")
        return
    asyncio.run_coroutine_threadsafe(
        config.wx_task_queue.put({"action": action, "kwargs": kwargs}),
        config.wx_task_loop
    )

# 真正执行函数：在子线程里运行
def _real_send_msg(content: str, who: str, at: str = None):
    config.wx.SendMsg(content, who=who, at=at)

def _real_reply_with_quote(msg_id: str, reply_text: str, chat_name: str, at: str = None):
    reply_with_quote(msg_id=msg_id, reply_text=reply_text, chat_name=chat_name, at=at)

def update_send_message_fields(send_id):
    config.db.update_send_message_fields("send_id", send_id, {"status": "发送成功"})

async def wx_get_group_memberlist(chat_name: str) -> list:
    task_id = uuid.uuid4().hex
    fut = asyncio.get_running_loop().create_future()
    config.task_futures[task_id] = fut          # 登记 Future
    _put_task("get_group_memberlist", chat_name=chat_name, task_id=task_id)
    return await fut                            # 等子线程把结果塞进来

async def wx_get_img_md5(content: str) -> str:
    task_id = uuid.uuid4().hex
    fut = asyncio.get_running_loop().create_future()
    config.task_futures[task_id] = fut
    _put_task("get_img_md5", content=content, task_id=task_id)
    return await fut                            # 等子线程把结果塞进来

def update_group_member_list():
    # 布尔映射
    for item in config.firstCheckGroup:
        config.firstCheckGroup[item] = item in config.groupName_list

async def get_latest_msg_quote(send_data):
    latest_msg_quote = []
    if send_data.quote_content == '[图片]':
        img_md5 = await wx_get_img_md5(send_data.content)
        latest_msg_quote = config.db.get_latest_messages(1, group_name=send_data.position, img_md5=img_md5)
    else:
        latest_msg_quote = config.db.get_latest_messages(1, group_name=send_data.position, content=send_data.quote_content)
    # 查找引用的msg_id
    if latest_msg_quote:
        return latest_msg_quote[0].get("msg_id")
    return ""