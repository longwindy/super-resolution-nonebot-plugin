import asyncio
import re
import time
from datetime import timedelta
from nonebot.matcher import Matcher

progress_pattern = re.compile(r"(\d+(\.\d+)?)%")


async def run_exe(exePath: str, estimatedTotalTime: asyncio.Queue, *args):
    process = await asyncio.create_subprocess_exec(
        str(exePath), *args,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.STDOUT,
    )

    start_time = None
    progress_time = []

    assert process.stdout is not None

    async for raw_line in process.stdout:
        line = raw_line.decode("utf-8").strip()
        print(line)
        
        match = progress_pattern.search(line)
        if match:
            percent = float(match.group(1))
            current_time = time.time()

            if start_time == None:
                start_time = current_time
            
            progress_time.append((current_time, percent))

        if len(progress_time) >= 2:
            t0, p0 = progress_time[0]
            t1, p1 = progress_time[-1]
            elapsed = t1 - t0
            progress_made = p1 - p0

            if progress_made > 0:
                estimated_total_time = elapsed / progress_made * 100
                if len(progress_time) == 4:
                    await estimatedTotalTime.put(estimated_total_time)
                remaining = estimated_total_time - (t1 - start_time)
                print(f"估计总用时: {timedelta(seconds=int(estimated_total_time))}, 剩余约: {timedelta(seconds=int(remaining))}")


    await process.wait()

    if process.returncode == 0:
        print("exe 运行成功")
    else:
        print("exe 运行失败")
    
    await estimatedTotalTime.put(None)

    return process.returncode

async def sendEstimatedTime(matcher: Matcher, estimatedTotalTime: asyncio.Queue):
    while True:
        estimated_total_time = await estimatedTotalTime.get()
        if estimated_total_time is None:
            break
        else:
            await matcher.send(f"预计所需时间: {estimated_total_time:.2f}秒")
            print(f"------Watcher 收到时间: {estimated_total_time}------")
