import asyncio
import signal
from jellynews import bot, smtp

async def async_main():
    # Create an event to handle shutdown
    shutdown_event = asyncio.Event()

    # Signal handler function
    def shutdown():
        print("Shutdown signal received!")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, shutdown)
    loop.add_signal_handler(signal.SIGINT, shutdown)

    tasks = []
    tasks.append(asyncio.create_task(bot.run_task()))
    tasks.append(asyncio.create_task(smtp.run()))


    try:
        await shutdown_event.wait()
    except asyncio.CancelledError:
        print("Main task received cancellation request.")

    print("Cancelling tasks...")
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    print("All tasks cancelled. Shutting down.")

def main():
    asyncio.run(async_main())

# Run event loop
if __name__ == "__main__":
    main()