import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

CONFIG_FILE = "config_tdnet.json"
SAVE_FILE = "last_tdnet.json"

# 今日の日付取得
today = datetime.now().strftime("%Y%m%d")

TDNET_URL = f"https://www.release.tdnet.info/inbs/I_list_001_{today}.html"


def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_last():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_last(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def send_discord(webhook, message):

    data = {
        "content": message
    }

    requests.post(webhook, json=data)


def get_tdnet_items():

    r = requests.get(TDNET_URL)

    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("table tr")

    items = []

    for row in rows:

        cols = row.find_all("td")

        if len(cols) > 3:

            title = cols[3].text.strip()

            link_tag = cols[3].find("a")

            if link_tag:

                link = "https://www.release.tdnet.info" + link_tag["href"]

                items.append({
                    "title": title,
                    "link": link
                })

    return items


def main():

    config = load_config()
    last_data = load_last()

    webhook = config["discord_webhook"]
    companies = config["companies"]

    items = get_tdnet_items()

    for item in items:

        title = item["title"]
        link = item["link"]

        for company in companies:

            name = company["name"]
            code = company["code"]

            if code in title:

                if title not in last_data:

                    message = f"""
📢 TDnet開示

{name}

{title}

{link}
"""

                    send_discord(webhook, message)

                    last_data.append(title)

    save_last(last_data)


if __name__ == "__main__":
    main()