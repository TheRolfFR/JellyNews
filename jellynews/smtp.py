from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging
import ssl
import aiosmtpd.smtp
from aiosmtpd.smtp import AuthResult, LoginPassword, SMTP
import subprocess
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

# Create cert and key if they don't exist
if not os.path.exists('cert.pem') and not os.path.exists('key.pem'):
    subprocess.call('openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem ' +
                    '-days 365 -nodes -subj "/CN=localhost"', shell=True)

# Load SSL context
def create_ssl_context(certfile="cert.pem", keyfile="key.pem"):
    """Create an SSL context for STARTTLS"""
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return ssl_context

# Pass SSL context to aiosmtpd
class ControllerStarttls(Controller):
    def factory(self):
        return SMTP(self.handler, require_starttls=True, tls_context=context)

# Load SSL context
context = create_ssl_context()

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
    ssl_context = create_ssl_context()  # Load SSL

    controller_hostname = os.environ.get("SMTP_HOST", "127.0.0.1")
    controller_port = os.environ.get("SMTP_PORT", 587)

    controller = ControllerStarttls(
        handler,
        hostname=controller_hostname,
        port=controller_port,
        authenticator=authenticator_func,  # i.e., the name of your authenticator function
        auth_required=True,  # Depending on your needs
        # ssl_context=ssl_context,
    )
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
