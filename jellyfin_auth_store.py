from jellyfin import JellyfinQuickConnectAuth
from pathlib import Path


class JellyfinAuthStore():

    __jf_auth: JellyfinQuickConnectAuth

    store_filepath: Path

    auth_recipient_list: list[str] = list()

    auth_in_progress_list: dict[str, str] = {}

    def __init__(self, jf_raw_auth: JellyfinQuickConnectAuth, load_file_path = "recipient_list.txt"):
        self.__jf_auth = jf_raw_auth
        self.store_filepath = Path(load_file_path)

    def load_store(self):
        if not self.store_filepath.exists():
            self.auth_recipient_list = []
            return self

        lines = []
        with open(self.store_filepath, 'r') as f:
            lines = f.readlines()
        lines = map(lambda line: line.strip(), filter(lambda line: len(line) > 0, lines))
        self.auth_recipient_list = list(lines)
        return self

    def add_to_store(self, recipient: str):
        self.auth_recipient_list.append(recipient)
        with open(self.store_filepath, "a") as f:
            f.write("\n" + recipient)

    def remove_from_store(self, recipient: str):
        if self.is_connected(recipient):
            self.auth_recipient_list.remove(recipient)
            with open(self.store_filepath, "w") as f:
                f.writelines(list(self.auth_recipient_list))

    def is_connected(self, recipient: str):
        return recipient in self.auth_recipient_list

    def auth_in_progress(self, recipient: str):
        return recipient in self.auth_in_progress_list

    def request_code(self, recipient: str):
        secret, code = self.__jf_auth.initiate()
        self.auth_in_progress_list[recipient] = secret
        return code

    def check_code(self, recipient: str):
        secret = self.auth_in_progress_list[recipient]
        auth_successful = self.__jf_auth.connect(secret)
        if auth_successful:
            self.add_to_store(recipient)
        return auth_successful

    def get_name(self, recipient: str):
        if recipient not in self.auth_in_progress_list:
            return None
        _, user = self.__jf_auth.authenticate(self.auth_in_progress_list[recipient])
        name = user["Name"]
        return name

    def remove_secret(self, recipient: str):
        if recipient in self.auth_in_progress_list:
            del self.auth_in_progress_list[recipient]
