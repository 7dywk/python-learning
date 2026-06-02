import time
from scraper import get_listings
from storage import load_old, save, find_new
from notifier import send_message

while True:
    old_listings = load_old()
    new_listings = get_listings()
    new_ones = find_new(old_listings, new_listings)

    if new_ones:
        print(f"Знайдено {len(new_ones)} нових!")
        send_message(new_ones)
    else:
        print("Нових оголошень немає")

    save(new_listings)
    time.sleep(300)