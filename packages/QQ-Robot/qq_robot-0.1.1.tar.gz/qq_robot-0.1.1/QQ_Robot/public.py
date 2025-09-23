import threading
fastapi_started = threading.Event()

# 自动获取
robot_id = -1
# 自动获取
robot_name = ""

# 日志名称 base
Log_File_Name = "logger.txt"

# NC SERVER地址 Base
LocalRobotAddress = "http://localhost:11451"
# LocalRobotAddress = "http://localhost:3001"  #Linux配置

#
ServerRobotAddress = "http://localhost:8000/"
# ServerRobotAddress = "http://localhost:6199/"   #Linux配置

# 群管WS地址 Base
# 本地
ServerWebSocket_URL = "ws://localhost:8081/ws/tunnel/"
# 局域网
# ServerWebSocket_URL = "ws://192.168.28.104:8001/ws/tunnel/"
# 测试环境
# ServerWebSocket_URL = "ws://10.7.115.88/api/conn/ws/tunnel/"
# 线上
# ServerWebSocket_URL = "ws://trade.dongxishi.com.cn/api/conn/qq/tunnel/"
# 生产
# ServerWebSocket_URL = "ws://10.7.110.87:8111/api/conn/ws/tunnel/"

# sentry_sdk配置 测试环境地址
sentry_sdk_url = "http://af018d0bf71f4ab091aab4181d10a49d@10.7.115.88:9000/4" #测试
# sentry_sdk_url = "http://a73326eabb8e4bbc92ef7d4159227cdb@10.7.115.88:9000/6"  #生产

# 向群管获取需要监听的群列表地址
get_listening_group_url = "http://localhost:8081/group/qq/listening?robot_account="  #本地
# get_listening_group_url = "http://192.168.28.104:8001/group/qq/listening?robot_account=" #局域网
# get_listening_group_url = "http://10.7.115.88/api/group/qq/listening?robot_account="   #测试
# get_listening_group_url = "http://10.7.110.87:8111/api/group/qq/listening?robot_account=" #生产
# 向群管获取更新群成员的间隔
get_group_members_interval_time_url = "http://localhost:8081/system/config/robot-push-interval"  #本地
# get_group_members_interval_time_url = "http://192.168.28.104:8001/system/config/robot-push-interval"  #局域网
# get_group_members_interval_time_url = "http://10.7.115.88/api/system/config/robot-push-interval"  #测试
# get_group_members_interval_time_url = "http://10.7.110.87:8111/api/system/config/robot-push-interval" #生产
listening_group = []

group_members_interval_time = 0

import os
# 华为云 OBS 配置
class OBSConfig:
    # 测试
    ENDPOINT = os.getenv("OBS_ENDPOINT", "http://test.osstest.foticit.com.cn")
    ACCESS_KEY = os.getenv("OBS_ACCESS_KEY", "YWlnY3VzZXI=")
    SECRET_KEY = os.getenv("OBS_SECRET_KEY", "17ed831e7e0b002345b3a16703eb7d95")
    BUCKET = os.getenv("OBS_BUCKET", "aigc")
    # 生产
    # ENDPOINT = os.getenv("OBS_ENDPOINT", "http://10.7.110.89")
    # ACCESS_KEY = os.getenv("OBS_ACCESS_KEY", "B2550CD83C2D567E8387")
    # SECRET_KEY = os.getenv("OBS_SECRET_KEY", "1TuoJqdSUKo1FeLXDHGpjIsYexQAAAGVPC1WfpYP")
    # BUCKET = os.getenv("OBS_BUCKET", "aigc")
    # 线上
    # ENDPOINT = "https://obs.cn-south-1.myhuaweicloud.com"
    # ACCESS_KEY = "HPUAV1CU32FRVZKMVWZT"
    # SECRET_KEY = "6icG48uD7KuVDBgnfjUNxIxthgXTSa78xhrmWrgV"
    # BUCKET = "tianxiadatong"
#
import json, os, sys
from pathlib import Path

# # 1. 运行时脚本所在目录（项目根）
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
get_listening_group_url        = f"http://{base_url}/group/qq/listening?robot_account="
get_group_members_interval_time_url = f"http://{base_url}/system/config/robot-push-interval"

sentry_sdk_url = cfg['sentry_sdk_url']

# OBSConfig 保持类形式
class OBSConfig:
    ENDPOINT   = cfg['OBSConfig']['ENDPOINT']
    ACCESS_KEY = cfg['OBSConfig']['ACCESS_KEY']
    SECRET_KEY = cfg['OBSConfig']['SECRET_KEY']
    BUCKET     = cfg['OBSConfig']['BUCKET']