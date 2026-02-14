import requests
import os

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

# === Events to monitor ===
EVENTS = [
    {
        "event_id": "19253513",
        "name": "DEN-LAT",
        "ticket_url": "https://tickets.milanocortina2026.org/en/event/hockey-su-ghiaccio-milano-santa-giulia-ice-hockey-arena-19253513/?affiliate=26O&language=en#/generic/"
    },
    {
        "event_id": "19253536",
        "name": "CAN-Fra",
        "ticket_url": "https://tickets.milanocortina2026.org/en/event/hockey-su-ghiaccio-milano-santagiulia-ice-hockey-arena-19253536/?affiliate=26O"
    },
    {
        "event_id": "19253535",
        "name": "USA-DEN",
        "ticket_url": "https://tickets.milanocortina2026.org/en/event/hockey-su-ghiaccio-milano-santagiulia-ice-hockey-arena-19253535/?affiliate=26O"
    },{
        "event_id": "19253528",
        "name": "SUI-CZE",
        "ticket_url": "https://tickets.milanocortina2026.org/en/event/hockey-su-ghiaccio-milano-santagiulia-ice-hockey-arena-19253528/?affiliate=26O"
    },
    # Add more events here as needed
    # {
    #     "event_id": "XXXXXXXX",
    #     "name": "Event Name",
    #     "ticket_url": "https://tickets.milanocortina2026.org/..."
    # },
]

# === Ticket scraper setup ===
API_URL_TEMPLATE = "https://api-cloud.eventim.com/ecom/resale/offer-listing/prd/api/v2/platforms/38/events/{event_id}/offers"
MAX_PRICE_PER_TICKET = 100
MIN_TICKETS = 1

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

def check_event(event):
    """Check a single event for matching tickets."""
    api_url = API_URL_TEMPLATE.format(event_id=event["event_id"])
    matches = []
    
    try:
        r = requests.get(api_url, timeout=10, headers=headers)
        r.raise_for_status()
        offers = r.json()
        
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
                    f"Seats {offer['ticketSeats']}\n"
                    f"Link: {event['ticket_url']}"
                )
                matches.append(match_text)
        
        return matches
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error for {event['name']}: {e}")
        print(f"Status Code: {e.response.status_code}")
        print(f"Response: {e.response.text[:500]}")
        return []
    except Exception as e:
        print(f"Error checking {event['name']}: {e}")
        return []

def main():
    all_matches = []
    
    for event in EVENTS:
        print(f"Checking {event['name']}...")
        matches = check_event(event)
        
        if matches:
            event_section = f"🎟️ {event['name']}:\n" + "\n\n".join(matches)
            all_matches.append(event_section)
    
    if all_matches:
        message = "🎟️ Ticket matches found!\n\n" + "\n\n" + "="*40 + "\n\n".join(all_matches)
        print(message)
        send_telegram_message(message)
    else:
        print("No matching tickets found for any event.")

if __name__ == "__main__":
    main()
