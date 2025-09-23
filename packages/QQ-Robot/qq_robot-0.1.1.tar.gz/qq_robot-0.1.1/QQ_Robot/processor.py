import logging
from urllib.parse import urlparse

import requests

# import QQ_Robot.client as client
from QQ_Robot import public
from QQ_Robot.db import db
import os
import time
import uuid

active_conversation = dict()

logger = logging.getLogger("uvicorn.access")
# 此函数发送一个带 @ 的消息，并且还要引用
async def send_reply_message_with_at(Msg:dict):
    try:
        # 现在群管能返回user_id，就不需要再请求获取一次
        # if str(Msg.get('reply','0')) == '1':
        #     builtPayload = {
        #         "message_id": Msg['sequence']
        #     }
        #     resp = requests.post(public.LocalRobotAddress + "/get_msg", json=builtPayload)
        #     resp.raise_for_status()
        #     Msg["receiver"] = resp.json().get('data').get('user_id','')

        payload = {
            "group_id": Msg["position"],
            "message": [
                {
                    "type": "at",
                    "data": {
                        "qq": Msg["receiver"],
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": Msg["content"]
                    }
                },
                {
                    "type": "reply",
                    "data": {
                        "id": Msg["sequence"],
                    }
                },
            ]
        }
        response = requests.post(public.LocalRobotAddress + "/send_group_msg", json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)



# 此函数发送一个带 @ 的消息
async def send_message_with_at(Msg:dict):
    try:

        if str(Msg.get('reply','0')) == '1':
            builtPayload = {
                "message_id": Msg['sequence']
            }
            resp = requests.post(public.LocalRobotAddress + "/get_msg", json=builtPayload)
            resp.raise_for_status()
            Msg["receiver"] = resp.json().get('data').get('user_id','')



        payload = {
            "group_id": Msg["position"],
            "message": [
                {
                    "type": "at",
                    "data": {
                        "qq": Msg["receiver"],
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": Msg["content"]
                    }
                }
            ]
        }
        response = requests.post(public.LocalRobotAddress + "/send_group_msg", json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)

# 此函数发送一条普通消息
async def send_message(Msg:dict):
    payload = {
        "group_id": Msg["position"],
        "message": Msg["content"]
    }
    response = requests.post(public.LocalRobotAddress + "/send_group_msg", json=payload)
    response.raise_for_status()
    return response.json()

# 此函数发送一条引用回复消息
async def reply_message(Msg:dict):
    try:
        payload = {
            "group_id": Msg["position"],
            "message": [
                {
                    "type": "reply",
                    "data": {
                        "id": Msg["sequence"],
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": Msg["content"]
                    }
                }
            ]
        }
        response = requests.post(public.LocalRobotAddress + "/send_group_msg", json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)

# 此函数获取当前登录账号信息
async def getOnlineAccountDetails():
    try:
        response = requests.get(public.LocalRobotAddress + "/get_login_info")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "@error"}

# 此函数获取当前登录账号登录状态
async def get_status():
    try:
        response = requests.get(public.LocalRobotAddress + "/get_status")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "@error"}

# 此函数为主处理函数，解析消息类型，然后发送对应指令消息到WS
async def covertMessageAndSend(data: dict):
    print("recv:", data)
    # try:
    #
    #     # 不在监听的群列表里
    #     if data.get('group_id') and not str(data['group_id']) in public.listening_group:
    #         return
    #     print("recv:", data)
    #     ### 处理通知类事件
    #     if "notice_type" in data:
    #         if data["notice_type"] == "group_increase" and data["sub_type"] in ['approve', 'invite']:#扫描进群approve和邀请进群invite
    #             payload = {"user_id": data["user_id"]}
    #             res = requests.post(public.LocalRobotAddress + "/get_stranger_info", json=payload)
    #             res.raise_for_status()
    #             await sender.instance.send(
    #                 command.packGroupMemberIncreasePayLoad(
    #                     data["user_id"],
    #                     res.json().get("data", {}).get("nick", "未知"),
    #                     data["group_id"]
    #                 )
    #             )
    #         elif data["notice_type"] == "group_decrease" and data["sub_type"] in ['kick', 'leave']: #群主踢人kick和自己退出leave
    #             payload = {"user_id": data["user_id"]}
    #             res = requests.post(public.LocalRobotAddress + "/get_stranger_info", json=payload)
    #             res.raise_for_status()
    #             await sender.instance.send(
    #                 command.packGroupMemberDeceasePayLoad(data["group_id"], res.json().get("data", {}).get("nick", "未知"), data["user_id"])
    #             )
    #         elif data["notice_type"] == "group_recall":
    #             print("消息被撤回了")
    #             await sender.instance.send(command.packMessageWithdrawPayLoad(data["message_id"], data["group_id"]))
    #         elif data["notice_type"] == "bot_offline":
    #             print("机器人下线")
    #             command.offline_msg = data["message"]
    #             await sender.instance.send(
    #                 command.offlinePayload()
    #             )
    #         return
    #
    #         ### 忽略自身消息
    #     if data['sender']['user_id'] == public.robot_id:
    #          return
    #
    #     if "message_type" in data and data["message_type"] == "private":
    #         packed = MessagePacket(
    #             sender=data['sender']['nickname'] or data['sender']['nickname'],
    #             sender_number=str(data['sender']['user_id']),
    #             receiver=public.robot_name,
    #             position=str(data['user_id']),
    #             sequence=data['message_id'],
    #             channel=public.robot_id,
    #             type="",
    #             content='',
    #             image="",
    #             reply="",
    #         )
    #         await sender.instance.send(command.privateConvPayload(MessagePack=packed))
    #         return
    #
    #
    #
    #     message = data.get('message', '')
    #     raw_message = data.get('raw_message', '')
    #
    #     # 构建并发送消息包
    #     packed = MessagePacket(
    #         sender= data['sender']['card'] or data['sender']['nickname'] ,# 发送者
    #         sender_number=str(data['sender']['user_id']),
    #         receiver= public.robot_name , # 接收者
    #         content= "" , # 文本内容
    #         image= "",  # 图片地址
    #         position= str(data['group_id']),  # 群
    #         type= "" , # 类型 text image text-image
    #         reply= "" , # 引用的消息id
    #         channel= public.robot_id,  # 机器人
    #         sequence= data['message_id'],  # 消息id
    #     )
    #
    #     # 多张图片的情况
    #     img_list = []
    #     ### 消息为结构化列表（推荐方式） 看napcat客户端配的是string还是array 上面array 下面string
    #     parts = []    #存储消息的类型text/image/text-image
    #     is_at_content = ''
    #     if isinstance(message, list):
    #         for segment in message:
    #             if segment['type'] == 'text':
    #                 if not 'text' in parts:
    #                     parts.append("text")
    #                 packed.content = packed.content + segment['data']['text']
    #             elif segment['type'] == 'at':
    #                 packed.content = packed.content+ '@'+ segment['data']['qq']
    #             elif segment['type'] == 'image':
    #                 if not 'image' in parts:
    #                     parts.append("image")
    #                 matches = re.findall(r'url=([^,\]]+)', raw_message)
    #                 decoded_results = [unquote(match.replace("&amp;", "&")) for match in matches]
    #                 if decoded_results and not img_list:
    #                     for url in decoded_results:
    #                         pic_url, pic_name = download_qq_image(url)
    #                         img_list.append(await client.push(pic_url, pic_name))
    #             elif segment['type'] == 'reply':
    #                 packed.reply = (segment['data']['id'])
    #
    #
    #     ### 消息为纯字符串（旧格式）
    #     elif isinstance(message, str):
    #         packed.content = re.sub(r'\[.*?\]', '', raw_message).strip()
    #         if packed.content:
    #             parts.append("text")
    #         if '[CQ:' in message:
    #             if '[CQ:image' in message:
    #                 parts.append("image")
    #                 match = re.search(r'url=([^,\]]+)', raw_message)
    #                 if match:
    #                     url = unquote(match.group(1).replace("&amp;", "&"))
    #                 else:
    #                     url = raw_message
    #                 pic_url,pic_name = download_qq_image(url)
    #                 packed.image  = await client.push(pic_url,pic_name)
    #             if '[CQ:reply' in message:
    #                 packed.reply = re.search(r"\[CQ:reply,id=(\d+)]", raw_message).group(1)
    #
    #             if '[CQ:at' in message:
    #                 packed.content = packed.content + '@'+ re.search(r"\[CQ:at,qq=(\d+)]", raw_message).group(1)
    #     # 消息类型 text/image/text-image
    #     if len(parts) == 1:
    #         packed.type = parts[0]
    #     elif len(parts) == 2:
    #         packed.type = "text-image"
    #     else:
    #         logger.info("不是回复类型")
    #         return
    #     # 如果有@ 文本内容修改成@的形式
    #     # if is_at_content:
    #     #     packed.content = packed.content+ is_at_content
    #     if img_list:
    #         if len(img_list) == 1:
    #             for img in img_list:
    #                 packed.image = img
    #                 await sender.instance.send(command.packReceivedMessagePayLoad(packed))
    #         else:
    #             await sendReplyMessageWithAt({
    #                 "position": packed.position,
    #                 "receiver": data['user_id'],
    #                 "sequence": packed.sequence,
    #                 "content": "对不起，暂不支持多张图片。",
    #             })
    #             return
    #     else:
    #         await sender.instance.send(command.packReceivedMessagePayLoad(packed))
    #
    # except KeyError as e:
    #     print(e)
    #     logger.error(f"[KeyError In Received Message] - {e}")
    # except Exception as e:
    #     print(e)
    #     logger.error(f"[Exception In Received Message] - {e}")

#
# async def synGroupMembers(data: dict):
#     payload = {
#         "group_id": data["group_id"],
#         "no_cache": True
#     }
#     response = requests.post(public.LocalRobotAddress + "/get_group_member_list", json=payload)
#     response.raise_for_status()
#     json_resp = response.json()
#     members = [
#         {
#             "number": str(item["user_id"]),
#             "name": str(item["card"]) or str(item["nickname"]),
#             "group_id": str(item["group_id"])
#         }
#         for item in json_resp.get("data", [])
#     ]
#     await sender.instance.send(command.packGroupMemberListPayload(members))


async def send_dm_essage(Msg: dict):
    print("私聊信息回复")
    payload = {
        "user_id": Msg["receiver"],
        "message": [
            {
                "type":"text",
                "data": {
                    "text": Msg["content"]
                }
            }
        ]
    }
    response = requests.post(public.LocalRobotAddress + "/send_private_msg", json=payload)
    response.raise_for_status()

async def undate_msg_status(Msg: dict):
    db.update_message_fields("send_id",Msg["send_id"],{"status": "发送成功"})



def download_qq_image(url: str, save_dir: str = 'QQ_Robot/images') -> tuple[str, str] | tuple[None, None]:
    """
    支持两种 QQ 图片 URL：
      1) https://gchat.qpic.cn/gchatpic_new/...            # 直链
      2) https://multimedia.nt.qq.com.cn/download?...     # 带查询串
    统一 GET 下载即可，无需再解析 appid/fileid/rkey。
    下载腾讯多媒体图片并保存为 PNG，文件名唯一。
    """
    os.makedirs(save_dir, exist_ok=True)

    # 默认文件名：URL 最后一段 + .png
    parsed   = urlparse(url)
    base     = os.path.basename(parsed.path) or 'qq_image'
    unique_name = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}_{base}.png"
    save_path   = os.path.join(save_dir, unique_name)

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.qq.com/'
    }

    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()

            # 如果服务器给出文件名，照样加前缀保存为 png
            cd = r.headers.get('Content-Disposition', '')
            if 'filename=' in cd:
                server_name = cd.split('filename=')[-1].strip('"')
                server_base = os.path.splitext(server_name)[0]
                unique_name = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}_{server_base}.png"
                save_path   = os.path.join(save_dir, unique_name)

            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return save_path, unique_name
    except Exception as e:
        print('下载失败:', e)
        return None, None


async def get_stranger_info_by_id(user_id: int) -> dict:
    """
    通过 user_id 获取陌生人资料（异步封装）
    :param user_id: QQ 号
    :return: 成功返回 data 字段（dict），失败返回空 dict
    """
    try:
        payload = {"user_id": user_id}
        resp = requests.post(
            f"{public.LocalRobotAddress}/get_stranger_info",
            json=payload,
            timeout=10
        )
        resp.raise_for_status()  # 仅检查状态
        return resp.json().get("data", {})  # ✅ 返回 data 字段
    except requests.RequestException as e:
        logger.error(f"[get_stranger_info_by_id] 请求失败: {e}")
        return {}

async def get_group_member_list(group_id: str) -> list[dict]:
    """
    获取指定群的成员列表
    :param group_id: 群号
    :return: 成员列表，每个元素含 number/name/group_id
    """
    payload = {"group_id": group_id, "no_cache": True}
    try:
        resp = requests.post(
            f"{public.LocalRobotAddress}/get_group_member_list",
            json=payload,
            timeout=15
        )
        resp.raise_for_status()
        return resp.json().get("data", {})  # ✅ 返回 data 字段
    except requests.RequestException as e:
        logger.error(f"[get_group_member_list] 请求失败: {e}")
        return []