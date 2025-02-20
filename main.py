import asyncio
from jellynews import bot, smtp

async def async_main():
    task1 = asyncio.create_task(bot.main())
    task2 = asyncio.create_task(smtp.main())

    await asyncio.gather(task1, task2)

def main():
    asyncio.run(async_main())

# Run event loop
if __name__ == "__main__":
    main()