import logging
import shutil
import atexit
import zipfile
import io
from _pydatetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
import subprocess
import time
import uvicorn
import sys
import os
import threading
from QQ_Robot import processor
from QQ_Robot.db import db
import psutil
import uuid
import json
# # 配置日志流到自定义的local_logger
# from QQ_Robot.app.log import local_logger
logging.basicConfig(
    level=logging.INFO,
    format="-[%(asctime)s %(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]  # 控制台输出
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
arranger =  AsyncIOScheduler()

# 2️⃣ 读取
# with open("build.key", "rb") as f:
#     key = f.read()            # 现在 key 是合法的 32 字节 base64
key =  b'echYvO4vyQk91EzD5awPnRvuhFaI6_peeVUh3J4DPb8='
fernet = Fernet(key)          # ✅ 不会报错

_napcat_proc = None   # 全局句柄


# def decrypt_resources() -> Path:
#     """把 resources.encrypted → 临时目录/resources，返回路径"""
#     encrypted = Path(__file__).with_name("resources.encrypted").read_bytes()
#     decrypted_zip = fernet.decrypt(encrypted)
#     temp_dir = Path(tempfile.mkdtemp(prefix="res_"))
#     print(temp_dir)
#     with zipfile.ZipFile(io.BytesIO(decrypted_zip), 'r') as zf:
#         zf.extractall(temp_dir)
#     # 不自动删除（或忽略失败）'  C:\Users\Administrator\AppData\Local\Temp
#     atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
#     # atexit.register(lambda: shutil.rmtree(temp_dir))
#     return temp_dir

# def decrypt_resources() -> Path:
#     encrypted = Path(__file__).with_name("resources.encrypted").read_bytes()
#     fernet = Fernet(Path(__file__).with_name("build.key").read_bytes())
#     decrypted_zip = fernet.decrypt(encrypted)
#
#     # 1️⃣ 解压到 exe 同级目录（不建子目录）
#     exe_dir = Path(__file__).parent / "napcat"   # exe 所在目录
#     with zipfile.ZipFile(io.BytesIO(decrypted_zip), 'r') as zf:
#         for info in zf.infolist():
#             zf.extract(info, exe_dir)
#
#             # 跳过 exe 本身，只解压数据
#             # if not info.filename.lower().endswith(".exe"):
#             #     zf.extract(info, exe_dir)
#
#     # 2️⃣ 不自动删除（或忽略失败）
#     # atexit.register(lambda: shutil.rmtree(exe_dir, ignore_errors=True))
#     return exe_dir        # 返回 exe

def decrypt_resources() -> Path:
    """把 resources.encrypted → 临时目录/resources，返回路径"""
    # encrypted = Path(__file__).parent.with_name("resources.encrypted").read_bytes()
    encrypted = Path.cwd().joinpath("resources.encrypted").read_bytes()
    decrypted_zip = fernet.decrypt(encrypted)
    temp_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\Temp\napcat"))  # 固定路径 C:\Users\Administrator\AppData\Local\Temp\napcat
    # 🔥 强制清空旧目录（如果存在）
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    with zipfile.ZipFile(io.BytesIO(decrypted_zip), 'r') as zf:
        for info in zf.infolist():
            target = temp_dir / info.filename
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)  # ✅ 忽略已存在
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(target, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
    # 不自动删除（或忽略失败）清除的时候 先退出
    atexit.register(_cleanup_napcat)
    atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True) if temp_dir.exists() else None)
    return temp_dir
#
# import logging, shutil, atexit, zipfile, io, subprocess, time, os, threading, sys, psutil, uuid, json
# from pathlib import Path
# from cryptography.fernet import Fernet
# from importlib.resources import files  # ← 关键：读包资源
# import tempfile
#
# key = b'echYvO4vyQk91EzD5awPnRvuhFaI6_peeVUh3J4DPb8='
# fernet = Fernet(key)

# def decrypt_resources() -> Path:
#     """把包内 resources.encrypted → 临时目录，返回路径"""
#     # 1. 读包资源（wheel 安装后也能找到）
#     encrypted = files("QQ_Robot").joinpath("resources.encrypted").read_bytes()
#     decrypted_zip = fernet.decrypt(encrypted)
#
#     # 2. 固定临时目录
#     temp_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\Temp\napcat"))
#     if temp_dir.exists():
#         shutil.rmtree(temp_dir, ignore_errors=True)
#     temp_dir.mkdir(parents=True, exist_ok=True)
#
#     # 3. 解压
#     with zipfile.ZipFile(io.BytesIO(decrypted_zip)) as zf:
#         zf.extractall(temp_dir)
#     atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
#     return temp_dir

# 启动程序
def launch_concurrent(exes):
    procs = []
    for exe in exes:
        print(f'>>> 启动 {exe}')
        p = subprocess.Popen([exe])  # 不阻塞
        procs.append(p)
        time.sleep(1)  # 可选：错开启动，避免资源争抢

    print('>>> 全部启动完成，等待它们退出...')
    for p in procs:
        p.wait()
    print('<<< 所有进程已结束')

def _cleanup_napcat():
    """退出钩子：强制结束 NapCat 及其子进程"""
    global _napcat_proc
    if _napcat_proc and _napcat_proc.poll() is None:
        _napcat_proc.terminate()
        try:
            _napcat_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _napcat_proc.kill()
            _napcat_proc.wait()
        _napcat_proc = None  # 🔥 防止重复调用
        # 🔥 结束所有名为 QQ.exe 的进程
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() in ('qq.exe', 'qq'):
            try:
                p = psutil.Process(proc.info['pid'])
                p.terminate()
                p.wait(timeout=2)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass

def _run_napcat():
    # 1. 解密
    global _napcat_proc  # 🔥 声明使用全局变量
    # _KEY = Path(__file__).with_name("build.key").read_bytes()
    RESOURCES_ROOT = decrypt_resources()

    # # 2️⃣ 输出第一层（根目录）文件/文件夹
    # for item in sorted(RESOURCES_ROOT.iterdir()):
    #     # 只显示根级，不递归
    #     print(item.name)

    # 3️⃣ 启动 NapCat
    exe_path = RESOURCES_ROOT / "NapCatWinBootMain.exe"
    if not exe_path.exists():
        print(f"❌ 找不到启动文件：{exe_path}")
        return
    # 启动并保存句柄
    _napcat_proc = subprocess.Popen([str(exe_path)], cwd=str(RESOURCES_ROOT))
    try:
        _napcat_proc.wait()
    except KeyboardInterrupt:
        print("用户中断，正在清理..")


def start_fastapi(host,port):
    # 设置默认端口

    # 解析命令行参数（避免中文和空格路径）
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            print(f"使用自定义端口: {port}")
        except ValueError:
            print(f"无效端口参数: {sys.argv[1]}, 使用默认端口 {port}")

    # 获取当前目录（处理打包后路径）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # print(f"服务启动目录: {current_dir}")
    # logging.info(f"访问地址: http://localhost:{port}")

    # 启动Uvicorn服务
    uvicorn.run(
        "QQ_Robot.main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,
        log_level="info",
        # 添加日志配置
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(asctime)s - %(levelprefix)s %(message)s",
                    "use_colors": None,
                },
            },
        }
    )


class qqApp:
    # def init(self,host="0.0.0.0", port=int(os.getenv("PORT", 8099)),fun=None):
    #     # 启动 NapCat（子线程，不阻塞）
    #     threading.Thread(target=_run_napcat, name="NapCat").start()
    #     # 3. 主线程运行 FastAPI（阻塞）
    #     try:
    #         main.after_start_fun = fun
    #         # start_fastapi(host, port)
    #         threading.Thread(target=start_fastapi,args=(host, port),name="FastAPI").start()
    #         #3. 阻塞直到 FastAPI 启动完成
    #     except KeyboardInterrupt:
    #         print("\n>>> 用户中断，正在清理...")
    #     finally:
    #         _cleanup_napcat()
    #         # _safe_rmtree(TEMP_DIR)
    async def init(self, host="0.0.0.0", port=8099, fun=None):
        # 子线程 B：NapCat —— 完全不阻塞
        threading.Thread(target=_run_napcat, name="NapCat", daemon=True).start()

        # 子线程 A：FastAPI —— 自己跑自己的
        threading.Thread(target=start_fastapi, args=(host, port),
                         name="FastAPI", daemon=True).start()

        # 主线程只等 FastAPI 就绪
        from QQ_Robot.public import fastapi_started
        fastapi_started.wait()  # ✅ 仅阻塞主线程
        if fun:
            await fun()  # 启动完成回调

    def set_deal_qq_msg_fun(self,fun):
        processor.covertMessageAndSend = fun

def update_message_fields(where_field, where_value, update_dict):
    db.update_message_fields(where_field, where_value,update_dict)

# def insert_message( send_id: str, message: str, status: str = ""):
#     db.insert_message(send_id, message,status)
def wait_to_send(data):
    data['send_id'] = str(uuid.uuid4())
    db.insert_message(data['send_id'], json.dumps(data, ensure_ascii=False))

def resend_message(send_id):
    db.update_message_fields("send_id", send_id, {"status": ''})

def send_success(send_id):
    db.update_message_fields("send_id", send_id,{"status": '发送成功', "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

def had_send(send_id):
    db.update_message_fields("send_id", send_id,{"status": '已成功', "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})



def fetch_pending_send():
    return db.fetch_pending_send()

__all__ = ["qqApp", "arranger"]