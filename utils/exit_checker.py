from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Event

async def exitCheck(event: Event, matcher: Matcher, cancel_keywords={"0"}):
    text = event.get_plaintext().strip()
    if text in cancel_keywords:
        await matcher.finish("操作已取消")


