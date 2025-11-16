# Made by xlbr
import os
import requests
import json

VK_APP_TOKEN = "6f88b1ea6f88b1ea6f88b1eabb6cb47ca566f886f88b1ea069c167500499bc64fe294f9"
GROUP_DOMAIN = "gimnasia32kurgan"
TRIGGER_WORD = "Расписание"
TMP_PATH = "tmp"
LAST_ID_FILE = "last_id.json"

def clear_old_photos():
    if not os.path.exists(TMP_PATH):
        return
    for file in os.listdir(TMP_PATH):
        if file.lower().endswith(".jpg"):
            os.remove(os.path.join(TMP_PATH, file))
    print("tmp directory is been cleared.")

def get_images(update=False):
    response = requests.get("https://api.vk.com/method/wall.get", params={
        "access_token": VK_APP_TOKEN,
        "domain": GROUP_DOMAIN,
        "count": 15,
        "v": "5.199"
    }).json()

    photos = []

    items = response.get("response", {}).get("items", [])
    if not items:
        print("VK API request is empty.")
        return

    for item in items:
        text = item.get("text", "")
        if TRIGGER_WORD in text:
            for file in os.listdir(TMP_PATH):
                os.remove(os.path.join(TMP_PATH, file))

            attachments = item.get("attachments", [])
            for att in attachments:
                if att["type"] == "photo":
                    photo = att["photo"]
                    # берем лучшую версию фото по качеству
                    if "orig_photo" in photo:
                        url = photo["orig_photo"]["url"]
                    else:
                        url = sorted(photo["sizes"], key=lambda s: s["width"], reverse=True)[0]["url"]
                    photos.append(url)

            for i,photo in enumerate(photos):
                response = requests.get(photo)
                if response.status_code == 200:
                    with open(f"{TMP_PATH}/photo_{i}.jpg", "wb") as f:
                        f.write(response.content)
                    print(f"Фото сохранено как photo_{i}.jpg")
                else:
                    print("Ошибка при скачивании:", response.status_code)
            photos = []
            return True
        
    return False