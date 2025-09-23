import asyncio
import logging

from fastapi import FastAPI
from QQ_Robot import message, public, processor, local_logger
from QQ_Robot.handler import AsyncLogHandler
from QQ_Robot.db import db
from QQ_Robot.qqApp import arranger
from apscheduler.triggers.cron import CronTrigger
# 配置日志流到自定义的local_logger
log_writer = local_logger.instance
async_handler = AsyncLogHandler(log_writer)
formatter = logging.Formatter('-[%(asctime)s %(levelname)s] %(message)s')
async_handler.setFormatter(formatter)
logger = logging.getLogger("uvicorn.access")
logger.handlers = []
logger.addHandler(async_handler)
logger.setLevel(logging.INFO)

from QQ_Robot.public import fastapi_started
app = FastAPI()

app.include_router(message.router)




def after_start_fun():
    logging.info("启动干什么")


#启动时检查。QQ是否已登录 & WS 是否可成功连接
async def cleanup_sent_messages_hard():
    """每天 0 点硬删除所有 status='已发送' 的记录"""
    with db.lock:  # 复用原对象的锁
        cur = db.conn.cursor()
        cur.execute("DELETE FROM messages WHERE status = '发送成功'")
        rows = cur.rowcount
        db.conn.commit()
    logging.info("[scheduler] 每日硬删除完成，删除 %d 条记录", rows)

@app.on_event("startup")
async def startup_event():
    for i in range(99999999999999999999):
        res = await processor.getOnlineAccountDetails()
        if res.get("status") != "@error":
            break
        logging.info(("QQ未登录"))
        await asyncio.sleep(1)
    else:
        logger.error("QQ持续未登录，启动失败")
        # 可选：raise RuntimeError 退出程序
        return
    response = await processor.getOnlineAccountDetails()
    public.robot_name = response.get("data").get("nickname")
    public.robot_id = response.get("data").get("user_id")
    logger.info(f"Robot Now Operating QQ Account of <{public.robot_id},{public.robot_name}>")
    # import sender
    # import command
    # sender.instance = sender.connector(public.ServerWebSocket_URL + str(public.robot_id), command.resolveAndExecuteCommand)
    # asyncio.create_task(sender.instance.connect())
    # await sender.instance.connected_event.wait()
    # 每天 00:00 执行 删除已发生成功的消息
    arranger.add_job(
        cleanup_sent_messages_hard,
        CronTrigger(hour=0, minute=0, second=0),  # 凌晨 0 点
        id="cleanup_sent_messages_hard",  # 方便后续移除
        replace_existing=True,  # 重启时覆盖旧任务
    )
    if not arranger.running:
        arranger.start()
    fastapi_started.set()  # 🔓 告诉 qqApp：我启动完了


@app.on_event("shutdown")
def shutdown_scheduler():
    arranger.shutdown()

