from pathlib import Path
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, Event
from nonebot.matcher import Matcher
from nonebot.typing import T_State


async def send_by_image(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    image_path, exe_time = matcher.state["output_image_abspath", "exe_time"]
    image_msg = MessageSegment.image(f"file:///{Path(image_path).as_posix()}")
    at_user = MessageSegment.at(event.get_user_id())

    msg = Message(at_user) + f"超分完成！用时{exe_time:.2f}秒\n" + image_msg
    await matcher.finish(msg)

async def send_by_file(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    image_path, exe_time = matcher.state["output_image_abspath", "exe_time"]
    file_msg = MessageSegment("file", {"file": f"file:///{image_path}"})
    at_user = MessageSegment.at(event.get_user_id())
    msg = Message(at_user) + f"超分完成！用时{exe_time:.2f}秒\n因为图片过大，即将转为文件发送..."
    await matcher.send(msg)
    await matcher.finish(file_msg)