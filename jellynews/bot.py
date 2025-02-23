from typing import Optional
import os

import asyncio
from quart import Quart
from quart import request
from dotenv import load_dotenv

from jellynews.graph_api import GraphAPI
from jellynews.jellyfin_auth_store import JellyfinAuthStore, JellyfinQuickConnectAuth

load_dotenv()


app = Quart(__name__)
api = GraphAPI(os.environ["FB_GRAPH_API_TOKEN"])
notification_type = os.environ.get("NO_PUSH")

jf_qc_auth = JellyfinQuickConnectAuth(os.getenv('JELLYFIN_SERVER_URL'))
jf_auth = JellyfinAuthStore(jf_qc_auth).load_store()

@app.get("/kaboom")
async def kaboom():
    return "Yes Rico, kaboom"

@app.post("/")
async def receive_endpoint():
    try:
        data = await request.get_json()
        recipient = data["entry"][0]["messaging"][0]["sender"]["id"]

        message: dict = data["entry"][0]["messaging"][0]["message"]
        print(message)
        message_text: Optional[str] = message.get("text")
        quick_reply = message.get("quick_reply", None)
        if quick_reply is not None:
            quick_reply = quick_reply["payload"]

        if jf_auth.is_connected(recipient):
            api.send_text(recipient, "Tu es déjà connecté")
            return ""

        # send an qc code to connect
        if message_text.lower() == "jellyfin":
            code = jf_auth.request_code(recipient)
            api.send_text(recipient, f"Rentrer le code de connexion rapide dans l'appli Jellyfin ou sur {jf_qc_auth.url}")
            api.send_text(recipient, code)
            qr = api.quick_reply("J'ai rentré le code", "CODE_ENTERED")
            api.send_quick_replies(recipient, "Clique sur le bouton après avoir rentré le code", [qr])

        # finish auth process
        elif quick_reply == "CODE_ENTERED":
            success = jf_auth.check_code(recipient)
            if success:
                api.send_text(recipient, "Authentification réussie")
            name = jf_auth.get_name(recipient)
            api.send_text(recipient, f"Connecté en tant que {name}")
            jf_auth.remove_secret(recipient)
    except Exception as e:
        print(e)
        api.send_text(recipient, f"Erreur: {str(e)}")

    return ""

@app.after_serving
async def shutdown():
    tasks = asyncio.all_tasks()
	# cancel all tasks
    for task in tasks:
	    # request the task cancel
	    task.cancel()

async def run_task():
    await app.run_task(host="0.0.0.0", port=os.environ.get("FB_BOT_PORT", 8080), debug=True)

if __name__ == "__main__":
    asyncio.run(run_task())
