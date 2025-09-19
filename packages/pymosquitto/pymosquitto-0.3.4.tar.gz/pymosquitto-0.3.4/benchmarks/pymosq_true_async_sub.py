import asyncio

from pymosquitto.aio import TrueAsyncClient as Client

from benchmarks import config as c

logger = None

if c.INTERVAL:
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()


async def main():
    count = 0
    async with Client(logger=logger) as client:
        await client.connect(c.HOST, c.PORT)
        await client.subscribe(c.TOPIC, c.QOS)
        async for _ in client.read_messages():
            count += 1
            if count == c.LIMIT:
                print("DONE")
                break


asyncio.run(main())
