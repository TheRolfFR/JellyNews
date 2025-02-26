import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

s = smtplib.SMTP(
    os.environ.get("SMTP_HOST", "127.0.0.1"),
    os.environ.get("SMTP_PORT", "8587")
)

if __name__ == "__main__":
    # s.login('user','password')

    r = s.sendmail('a@example.com', ['b@example.com'], """\
    From: Anne Person <anne@example.com>
    To: Bart Person <bart@example.com>
    Subject: A test
    Message-ID: <ant>

    Hi Bart, this is Anne.
    """)