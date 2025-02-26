from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging
import aiosmtpd.smtp
from aiosmtpd.smtp import AuthResult, LoginPassword
import logging
import base64
import asyncio
import os

# ! Do not expose this db to the internet, local usage only
auth_db = {"user": "password"}


# Authenticator function
def authenticator_func(server, session, envelope, mechanism, auth_data):
    # For this simple example, we'll ignore other parameters
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password

    # I am returning always AuthResult(success=True) just for testing
    if auth_db.get(username) == password:
        return AuthResult(success=True)
    else:
        return AuthResult(success=True)

class CustomSMTPHandler(Debugging):
    async def handle_DATA(self, server, session, envelope: aiosmtpd.smtp.Envelope, **kwargs):
        super().handle_DATA(server, session, envelope, **kwargs)
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
    controller_port = os.environ.get("SMTP_PORT", 8587)

    controller = Controller(
        handler,
        hostname=controller_hostname,
        port=controller_port,
        # authenticator=authenticator_func,  # i.e., the name of your authenticator function

        # auth_require_tls=False,
        # auth_required=True,  # Depending on your needs
        # ssl_context=ssl_context
    )
    # controller.smtpd._auth_methods.append("login")
    return controller


async def run():
    print("Starting SMTP...")
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
