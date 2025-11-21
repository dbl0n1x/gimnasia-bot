# Made by xlbr
import os
import requests
from pathlib import Path

VK_APP_TOKEN = "6f88b1ea6f88b1ea6f88b1eabb6cb47ca566f886f88b1ea069c167500499bc64fe294f9"
GROUP_DOMAIN = "gimnasia32kurgan"
TRIGGER_WORD = "Расписание"
TMP_PATH = "tmp"

def clear_old_photos():
    if not os.path.exists(TMP_PATH):
        return
    for file in os.listdir(TMP_PATH):
        if file.lower().endswith(".jpg"):
            os.remove(os.path.join(TMP_PATH, file))
    print("tmp directory is been cleared.")

def get_images(update=False):
    Path(TMP_PATH).mkdir(parents=True, exist_ok=True)

    response = requests.get("https://api.vk.com/method/wall.get", params={
        "access_token": VK_APP_TOKEN,
        "domain": GROUP_DOMAIN,
        "count": 15,
        "v": "5.199"
    }).json()

    items = response.get("response", {}).get("items", [])
    if not items:
        return []

    # Полностью очищаем tmp если update=True
    if (update):
        for f in os.listdir(TMP_PATH):
            os.remove(os.path.join(TMP_PATH, f))

    result_posts = []  # список постов, каждый пост — список файлов картинок

    post_index = 0
    for item in items:
        text = item.get("text", "")
        if TRIGGER_WORD not in text:
            continue

        attachments = item.get("attachments", [])
        post_images = []

        for att in attachments:
            if att["type"] != "photo":
                continue

            photo = att["photo"]
            if "orig_photo" in photo:
                url = photo["orig_photo"]["url"]
            else:
                url = sorted(photo["sizes"], key=lambda s: s["width"], reverse=True)[0]["url"]

            resp = requests.get(url)
            if resp.status_code == 200:
                filename = f"{TMP_PATH}/post{post_index}_img{len(post_images)}.jpg"
                with open(filename, "wb") as f:
                    f.write(resp.content)
                post_images.append(filename)

        if post_images:
            result_posts.append(post_images)
            post_index += 1

    return result_posts
