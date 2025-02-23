from aiosmtpd.controller import Controller
import aiosmtpd.smtp
import asyncio
import os


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


def create_controller() -> Controller:
    handler = CustomSMTPHandler()
    controller_hostname = os.environ.get("SMTP_HOST", "127.0.0.1")
    controller_port = os.environ.get("STMP_PORT", 5021)
    controller = Controller(handler, hostname=controller_hostname, port=controller_port)
    return controller


async def run():
    controller = create_controller()
    await main(controller)

async def main(controller: Controller):
    controller.start()
    print(f"SMTP started on {controller.hostname}:{controller.port}")
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("SMTP task cancelled")
        controller.stop()


if __name__ == "__main__":
    asyncio.run(run())
