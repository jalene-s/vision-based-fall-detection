import requests

BOT_TOKEN = "8513395582:AAEL4mmRoxcHW274a7JCDsoM3lvLw1ZLmhw"
CHAT_ID = "8208889681"


def send_alert_message():

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": "⚠️ Fall Detected. Please check immediately. Sending snapshot and video."
        }
    )


def send_alert_image(image_path):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    with open(image_path, "rb") as image:

        requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"photo": image}
        )


def send_alert_video(video_path):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

    with open(video_path, "rb") as video:

        requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"video": video}
        )