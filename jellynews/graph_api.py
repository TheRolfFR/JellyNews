import requests
from dotenv import load_dotenv
import copy
import os

load_dotenv()

# This is API key for facebook messenger.
API = "https://graph.facebook.com/v22.0/me/messages"


class GraphAPI:
    """Real docs at https://developers.facebook.com/docs/messenger-platform/reference/send-api/"""

    page_access_token: str

    def __init__(self, access_token: str):
        self.page_access_token = access_token

    @property
    def params(self):
        return {"access_token": self.page_access_token}

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def create_postback_button(self, title: str, payload: str):
        return {"type": "postback", "title": title, "payload": str(payload)}

    def create_url_button(self, title: str, url: str, webview_height_ratio=None):
        url_button = {"type": "web_url", "url": url, "title": title}
        if webview_height_ratio is not None:
            url_button["webview_height_ratio"] = webview_height_ratio
        return url_button

    def create_default_action(self, button):
        action = copy.deepcopy(button)
        if "title" in action:
            del action["title"]
        return action

    def create_single_generic(
        self,
        title: str,
        subtitle=None,
        image_url=None,
        default_action=None,
        buttons=None,
    ):
        attachment = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [{"title": title}],
            },
        }
        if subtitle is not None:
            attachment["payload"]["elements"][0]["subtitle"] = subtitle
        if image_url is not None:
            attachment["payload"]["elements"][0]["image_url"] = image_url
        if default_action is not None:
            attachment["payload"]["elements"][0]["default_action"] = default_action
        if buttons is not None:
            attachment["payload"]["elements"][0]["buttons"] = buttons
        return attachment

    def quick_reply(self, title, payload, image=None):
        qr = {
            "content_type": "text",
            "title": title,
            "payload": str(payload),
        }
        if image is not None:
            qr["image"] = image
        return qr

    def send_quick_replies(self, recipient: str, text: str, quick_replies: list[dict], notification_type="REGULAR"):
        payload = {
            "recipient": {"id": recipient},
            "notification_type": notification_type,
            "message": {
                "text": text,
                "quick_replies": quick_replies
            }
        }

        response = requests.post(
            API, headers=self.headers, json=payload, params=self.params
        )
        print(response, response.status_code, response.text)
        return response.status_code == 200


    def send_template(self, recipient, template, **kwargs):
        payload = {
            "recipient": {"id": recipient},
            "notification_type": kwargs.get("notification_type", "REGULAR"),
            "message": {"attachment": {"type": "template", "payload": template}},
        }

        response = requests.post(
            API, headers=self.headers, json=payload, params=self.params
        )
        return response.status_code == 200

    def send_text(self, recipient, text, notification_type="REGULAR"):
        total_payload = {
            "recipient": {"id": recipient},
            "notification_type": notification_type,
            "message": {"text": text},
            "messaging_type": "RESPONSE",
        }

        response = requests.post(
            API, headers=self.headers, json=total_payload, params=self.params
        )
        return response.status_code == 200

    def send_attachment(self, recipient, attachment, notification_type="REGULAR"):
        payload = {
            "recipient": {"id": recipient},
            "notification_type": notification_type,
            "message": {"attachment": attachment},
        }

        response = requests.post(
            API, headers=self.headers, json=payload, params=self.params
        )
        return response.status_code == 200


if __name__ == "__main__":
    api = GraphAPI(os.environ["FB_GRAPH_API_TOKEN"])
    notification_type = "NO_PUSH"

    api.send_text(
        recipient=os.environ["FB_TEST_RECIPIENT"],
        text=os.environ["FB_TEST_TEXT"],
        notification_type=notification_type,
    )

    button = api.create_url_button(
        title=os.environ["FB_TEST_BTN_TITLE"], url=os.environ["FB_TEST_BTN_URL"]
    )
    action = api.create_default_action(button)
    attachment = api.create_single_generic(
        title=os.environ["FB_TEST_GEN_TITLE"],
        subtitle=os.environ["FB_TEST_GEN_SUBTITLE"],
        image_url=os.environ["FB_TEST_GEN_IMAGE_URL"],
        default_action=action,
        buttons=[button],
    )
    api.send_attachment(
        recipient=os.environ["FB_TEST_RECIPIENT"],
        attachment=attachment,
        notification_type=notification_type,
    )
