import os
import json


def load_old(filename="listings.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save(data, filename="listings.json"):
    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_new(old, new):
    old_links = {item["link"] for item in old}
    return [item for item in new if item["link"] not in old_links]