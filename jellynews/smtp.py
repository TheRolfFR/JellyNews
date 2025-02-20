from aiosmtpd.controller import Controller
import aiosmtpd.smtp
import asyncio


async def main():
    handler = CustomSMTPHandler()
    controller = Controller(handler, hostname="0.0.0.0", port=5021)
    controller.start()
    print("SMTP server started on port 5021")
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        controller.stop()


class CooperativeSmtpController(aiosmtpd.controller.UnthreadedController):
    async def async_begin(self):
        self.loop = asyncio.get_running_loop()
        self.server_coro = self._create_server()
        self.server = await self.server_coro


class CustomSMTPHandler:
    async def handle_DATA(self, server, session, envelope: aiosmtpd.smtp.Envelope):
        msg = {
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos,
            "data": envelope.content.decode("utf8", errors="replace"),
        }
        print("handle_DATA", msg)
        return "250 OK"


if __name__ == "__main__":
    asyncio.run(main())
