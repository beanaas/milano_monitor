import requests

# === Telegram setup ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# === Ticket scraper setup ===
API_URL = "https://api-cloud.eventim.com/ecom/resale/offer-listing/prd/api/v2/platforms/38/events/19253531/offers"
MAX_PRICE_PER_TICKET = 300
MIN_TICKETS = 2

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://tickets.milanocortina2026.org",
    "Referer": "https://tickets.milanocortina2026.org/",
    "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=1, i"
}

def main():
    try:
        r = requests.get(API_URL, timeout=10, headers=headers)
        r.raise_for_status()
        offers = r.json()

        matches = []

        for offer in offers:
            tickets = offer["numberOfTickets"]
            total_price = offer["totalPrice"]
            price_per_ticket = total_price / tickets

            if tickets >= MIN_TICKETS and price_per_ticket <= MAX_PRICE_PER_TICKET:
                match_text = (
                    f"{tickets} tickets | "
                    f"{price_per_ticket:.2f}€ per ticket | "
                    f"{offer['tdlPriceLevelName']} | "
                    f"Area {offer['ticketAreas']} | "
                    f"Row {offer['ticketRows']} | "
                    f"Seats {offer['ticketSeats']}"
                    f"link https://tickets.milanocortina2026.org/en/event/hockey-su-ghiaccio-milano-santa-giulia-ice-hockey-arena-19253531/?affiliate=26O&language=en#/generic/"
                )
                matches.append(match_text)

        if matches:
            message = "🎟️ Ticket match found!\n\n" + "\n".join(matches)
            print(message)
            send_telegram_message(message)
        else:
            print("No matching tickets found.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Status Code: {e.response.status_code}")
        print(f"Response: {e.response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
