from scraper import get_listings
from storage import load_old, save, find_new


old_listings = load_old()
new_listings = get_listings()
new_ones = find_new(old_listings, new_listings)

if new_ones:
    print(f"Знайдено {len(new_ones)} нових оголошень!")
    for item in new_ones:
        print(item)

save(new_listings)