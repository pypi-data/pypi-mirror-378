import asyncio
wx_task_queue = None   # asyncio.Queue
wx_task_loop  = None   # 子线程事件循环
task_futures: dict[str, asyncio.Future] = {}   # key=uuid, value=Future
id前缀 = "1"
my_wxName = ""  # 微信名
wx = None  #wx实例

# 获取监听群聊列表
# get_listening_group_url = "http://10.7.110.87:8111/api/group/wx/listening?robot_account="  #生产
# get_listening_group_url = "http://10.7.115.88/api/group/wx/listening?robot_account="  #测试
get_listening_group_url = "http://localhost:8081/group/wx/listening?robot_account="  #本地
groupName_list = []  # 所有的群名
# groupName_list = ["微信测试2"]  # 所有的群名
# groupName_list = ["wxauto十八群","踢人","微信测试","得闲饮茶","数字交易员对接","测试群001","天下大同伐木累","九顺小程序","我的野外生存游戏群","三个健忘鬼","奶茶群","一点半大咖到滘心"]                 #所有的群名
# groupName_list=[]
have_check_groupName_list =[]
offline_msg = ''
db = None  # 数据库实例
ServerWebSocket_URL = "ws://localhost:8081/ws/tunnel/"
# ServerWebSocket_URL = "ws://192.168.28.104:8001/ws/tunnel/"
# ServerWebSocket_URL = "ws://192.168.28.143:8000/wx/tunnel/"
# ServerWebSocket_URL = "ws://172.16.0.179:8081/wx/tunnel/"
# ServerWebSocket_URL = "ws://172.17.103.143:8081/wx/tunnel/"
# 线上
# ServerWebSocket_URL = "ws://trade.dongxishi.com.cn/api/conn/wx/tunnel/"
# 测试
# ServerWebSocket_URL = "ws://10.7.115.88/api/conn/ws/tunnel/"
# 生产
# ServerWebSocket_URL = "ws://10.7.110.87:8111/api/conn/ws/tunnel/"
_start_time = None
_end_time = None
ws_client = None
firstCheckGroup = dict()

# sentry_sdk配置 地址
sentry_sdk_url = "http://fe99b117e84044718514e7568bfaa0ca@10.7.115.88:9000/5" #测试
# sentry_sdk_url = "http://82aa30b246de4dedbca51095a6566d94@10.7.115.88:9000/7" #生产

# 向群管获取更新群成员的间隔
get_group_members_interval_time_url = "http://localhost:8081/system/config/robot-push-interval"
# get_group_members_interval_time_url = "http://10.7.115.88/api/system/config/robot-push-interval" #测试
# get_group_members_interval_time_url = "http://10.7.110.87:8111/api/system/config/robot-push-interval" #生产

group_members_interval_time = 0
check_group_members_time_start = None
check_group_members_time_end = None
import os
# 华为云 OBS 配置
class OBSConfig:
    # 线上
    ENDPOINT = "https://obs.cn-south-1.myhuaweicloud.com"
    ACCESS_KEY = "HPUAV1CU32FRVZKMVWZT"
    SECRET_KEY = "6icG48uD7KuVDBgnfjUNxIxthgXTSa78xhrmWrgV"
    BUCKET = "tianxiadatong"
    # 测试
    # ENDPOINT = os.getenv("OBS_ENDPOINT", "http://test.osstest.foticit.com.cn")
    # ACCESS_KEY = os.getenv("OBS_ACCESS_KEY", "YWlnY3VzZXI=")
    # SECRET_KEY = os.getenv("OBS_SECRET_KEY", "17ed831e7e0b002345b3a16703eb7d95")
    # BUCKET = os.getenv("OBS_BUCKET", "aigc")
    # 生产
    # ENDPOINT = os.getenv("OBS_ENDPOINT", "http://10.7.110.89")
    # ACCESS_KEY = os.getenv("OBS_ACCESS_KEY", "B2550CD83C2D567E8387")
    # SECRET_KEY = os.getenv("OBS_SECRET_KEY", "1TuoJqdSUKo1FeLXDHGpjIsYexQAAAGVPC1WfpYP")
    # BUCKET = os.getenv("OBS_BUCKET", "aigc")

# import json, os, sys
# from types import SimpleNamespace
#
# if getattr(sys, 'frozen', False):
#     base_dir = os.path.dirname(sys.executable)
# else:
#     base_dir = os.path.dirname(__file__)
# json_path = os.path.join(base_dir, 'config.json')
#
# # ---------- 只转一层，list/dict 保持原样 ----------
# with open(json_path, 'r', encoding='utf-8') as f:
#     raw = json.load(f)
#
# def to_namespace(obj):
#     if isinstance(obj, dict):
#         return SimpleNamespace(**{k: to_namespace(v) for k, v in obj.items()})
#     if isinstance(obj, list):
#         return [to_namespace(i) for i in obj]
#     return obj
#
# cfg = to_namespace(raw)
# # 重新摊平到模块级
# globals().update(vars(cfg))
#
# # OBSConfig 保持类形式（兼容旧代码）
# class OBSConfig:
#     ENDPOINT   = raw['OBSConfig']['ENDPOINT']
#     ACCESS_KEY = raw['OBSConfig']['ACCESS_KEY']
#     SECRET_KEY = raw['OBSConfig']['SECRET_KEY']
#     BUCKET     = raw['OBSConfig']['BUCKET']

#
# import json, os, sys
# from types import SimpleNamespace
#
# base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
# cfg_path = os.path.join(base, 'config.json')
#
# with open(cfg_path, 'r', encoding='utf-8') as f:
#     raw = json.load(f)          # 原生 dict / list / 值
#
# # ---------- 只转顶层 ----------
# cfg = SimpleNamespace(**raw)    # 仅顶层变成属性，内层 list/dict 不变
#
# # 摊平到模块级
# globals().update(vars(cfg))
#
# # OBSConfig 保持类形式（兼容旧代码）
# class OBSConfig:
#     ENDPOINT   = raw['OBSConfig']['ENDPOINT']
#     ACCESS_KEY = raw['OBSConfig']['ACCESS_KEY']
#     SECRET_KEY = raw['OBSConfig']['SECRET_KEY']
#     BUCKET     = raw['OBSConfig']['BUCKET']

import json, os, sys
from pathlib import Path
# 1. 运行时脚本所在目录（项目根）
# RUNTIME_ROOT = Path(__file__).parent.parent
#
# # 2. 找 config.json
# CONFIG_FILE = RUNTIME_ROOT / "config.json"
#
# if not CONFIG_FILE.exists():
#     raise FileNotFoundError(
#         f"找不到配置文件：{CONFIG_FILE.resolve()}，请把它放在项目根目录！"
#     )
#
#
# with CONFIG_FILE.open("r", encoding="utf-8") as f:
#     cfg = json.load(f)


# 1. 优先读用户运行目录
user_cfg = Path.cwd() / 'config.json'
# 2. 其次读包目录（打包时带默认配置才用）
pkg_cfg  = Path(__file__).with_name('config.json')

if user_cfg.exists():
    CONFIG_PATH = user_cfg
elif pkg_cfg.exists():
    CONFIG_PATH = pkg_cfg
else:
    raise FileNotFoundError(
        '找不到 config.json！\n'
        f'请将该文件放到以下任一路径：\n'
        f'  1. {user_cfg}\n'
        f'  2. {pkg_cfg}'
    )

with CONFIG_PATH.open(encoding='utf-8') as f:
    cfg = json.load(f)

# ---------- 底座 ----------
base_url = cfg['base_url']          # localhost:8081

# ---------- 拼接 ----------
ServerWebSocket_URL            = f"ws://{base_url}/ws/tunnel/"
get_listening_group_url        = f"http://{base_url}/group/wx/listening?robot_account="
get_group_members_interval_time_url = f"http://{base_url}/system/config/robot-push-interval"

sentry_sdk_url = cfg['sentry_sdk_url']

# OBSConfig 保持类形式
class OBSConfig:
    ENDPOINT   = cfg['OBSConfig']['ENDPOINT']
    ACCESS_KEY = cfg['OBSConfig']['ACCESS_KEY']
    SECRET_KEY = cfg['OBSConfig']['SECRET_KEY']
    BUCKET     = cfg['OBSConfig']['BUCKET']