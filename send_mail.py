import smtplib
import ssl

s = smtplib.SMTP_SSL('192.168.1.16', 587)
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
s.starttls(context=ssl_context)

if __name__ == "__main__":
    s.login('user','password')

    r = s.sendmail('a@example.com', ['b@example.com'], """\
    From: Anne Person <anne@example.com>
    To: Bart Person <bart@example.com>
    Subject: A test
    Message-ID: <ant>

    Hi Bart, this is Anne.
    """)