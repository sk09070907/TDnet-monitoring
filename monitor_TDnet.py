import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

CONFIG_FILE = "config_tdnet.json"
SAVE_FILE = "last_tdnet.json"

today = datetime.now().strftime("%Y%m%d")


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
    requests.post(webhook, json={"content": message})


def get_tdnet_items():

    items = []

    for page in range(1, 1000):

        page_str = str(page).zfill(3)

        url = f"https://www.release.tdnet.info/inbs/I_list_{page_str}_{today}.html"

        r = requests.get(url)

        if r.status_code != 200:
            break

        r.encoding = "utf-8"

        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table tr")

        if len(rows) == 0:
            break

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

                if link not in last_data:

                    message = f"""
📢 TDnet開示

{name}

{title}

{link}
"""

                    send_discord(webhook, message)

                    last_data.append(link)

    save_last(last_data)


if __name__ == "__main__":

    try:
        main()

    except Exception as e:

        try:
            config = load_config()
            webhook = config["discord_webhook"]

            error_message = f"""
⚠️ TDnet監視エラー

{str(e)}
"""

            send_discord(webhook, error_message)

        except:
            pass

        raise