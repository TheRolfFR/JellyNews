from yarl import URL
import requests
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

class JellyfinQuickConnectAuth:
    """Good doc at https://api.jellyfin.org/#tag/User/operation/AuthenticateWithQuickConnect
    """

    server_url: URL
    device_id: str

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"MediaBrowser Client=\"{self.client}\", Device=Android, DeviceId={self.device_id}, Version=0.0.1"
        }

    @property
    def url(self):
        return str(self.server_url) + "/web/#/quickconnect"

    def __init__(self, server_url: str, device_id = "0123456", client="TheBot"):
        self.server_url = URL(server_url)
        self.device_id = device_id
        self.client = client

    def check(self):
        url = str(self.server_url / "QuickConnect/Enabled")
        response = requests.get(url)
        return response.status_code == 200 and response.text == "true"

    def connect(self, secret: str):
        url = str(self.server_url / "QuickConnect/Connect")
        response = requests.get(url, params= {
            "secret": secret,
        })
        return response.status_code == 200

    def initiate(self) -> tuple[str, str]:
        url = str(self.server_url / "QuickConnect/Initiate")
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError('Quick connect is not active on this server.')
        response_json = response.json()
        return response_json['Secret'], response_json['Code']

    def authenticate(self, secret: str) -> tuple[str, dict]:
        url = str(self.server_url / "Users/AuthenticateWithQuickConnect")
        response = requests.post(url, json={
            "Secret": secret,
        }, headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError('Missing token.')
        response_json = response.json()
        return response_json['AccessToken'], response_json['User']


# QuickConnect verification script
if __name__ == "__main__":
    jf_qcauth = JellyfinQuickConnectAuth(os.getenv('JELLYFIN_SERVER_URL'))

    qc_enabled = jf_qcauth.check()
    print(f"Jellyfin QuickConnect is{'' if qc_enabled else ' not'} enabled")

    if not qc_enabled:
        sys.exit(1)

    print("Intiated QuickConnect session:")
    secret, code = jf_qcauth.initiate()
    print(f"Secret={"*"*len(secret)}")

    jf_web_url = str(jf_qcauth.server_url) + "/web/#/quickconnect"
    print(f"Enter QuickConnect code into Jellyfin in app or at {jf_web_url}: {code}")

    print("Press enter when done:", end='')
    input("")

    qc_success = jf_qcauth.connect(secret)
    if not qc_success:
        print('QuickConnect failure!')
        sys.exit(1)
    print('QuickConnect success!')

    print('Logging in...')
    access_token, user = jf_qcauth.authenticate(secret)
    print(f"AccessToken={"*"*len(access_token)}")
    print(f"User={json.dumps(user, indent=4)}")
