#!/usr/bin/env python3
"""
Перевірка компаній через OpenCorporates API: назва + активна + адреса.

Запуск:
    pip install requests rapidfuzz
    export OPENCORPORATES_TOKEN=твій_токен      # Windows: set OPENCORPORATES_TOKEN=...
    python oc_check.py names.txt --out results.csv
    python oc_check.py names.txt --check        # лише звіт по файлу, без API і токена

Формат names.txt: блоки, розділені рядком ===
Назва береться з "Title: ...", адреса з "Address: ...", штат (для юрисдикції us_xx) з "state: ..."
у Raw Data (запасний варіант — з Address). EIN / місто / сайт теж витягуються.
Увесь блок зберігається як є (колонка info).

Вердикти:
    OK                назва збіглась + компанія активна + адреса збіглась
    CHECK_ADDRESS     назва + активна, але в OC немає адреси (або лише штат) -> перевір руками
    ADDRESS_MISMATCH  назва + активна, але адреса інша (може бути адреса агента) -> перевір руками
    INACTIVE          назва збіглась, але компанія неактивна
    MULTIPLE          кілька однаково підходящих компаній -> руками
    REVIEW            назва схожа, але не 1 в 1 -> руками
    NOT_FOUND         нічого схожого в реєстрі штату
    SKIPPED_STATE     штат зі списку --skip-states (за замовчуванням MD), запитів немає
    SKIPPED_NO_STATE  американський штат не визначено, запитів немає

Скрипт можна зупиняти й запускати знову: вже перевірені назви пропускаються,
а лічильник запитів за добу зберігається в SQLite (щоб не вилетіти за free-ліміт).
"""
import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from rapidfuzz import fuzz

API_URL = "https://api.opencorporates.com/v0.4/companies/search"
DB_PATH = "oc_results.db"

DAILY_LIMIT = 50        # free-тариф; змінюй, якщо платний
REQUEST_DELAY = 1.5     # секунд між запитами
MATCH_THRESHOLD = 92    # >= вважаємо збігом назви (можна підняти до 97, якщо назви збігаються 1 в 1)
REVIEW_THRESHOLD = 75   # [REVIEW; MATCH) -> на ручну перевірку

# ----------------------------------------------------------------------------
# Нормалізація назв
# ----------------------------------------------------------------------------


def _clean(name: str) -> list[str]:
    """lowercase, без діакритики й пунктуації -> список токенів."""
    s = name.casefold().replace("ł", "l").replace("&", " and ")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[.'’`]", "", s)        # "sp. z o.o." -> "sp z oo"
    s = re.sub(r"[^\w]+", " ", s)
    return s.split()


_RAW_LEGAL_FORMS = [
    "sp z oo", "sp zoo", "sp k", "sp j",
    "spolka z ograniczona odpowiedzialnoscia", "spolka akcyjna",
    "limited liability company", "limited", "ltd", "llc", "inc", "incorporated",
    "corp", "corporation", "gmbh", "ag", "sa", "sarl", "bv", "nv", "plc", "llp", "co",
    "тов", "ооо", "пат", "прат", "зат", "ат", "фоп",
    "товариство з обмеженою відповідальністю",
]
# довші форми першими; самі форми проганяємо через ту саму нормалізацію
LEGAL_FORMS = sorted((tuple(_clean(f)) for f in _RAW_LEGAL_FORMS), key=len, reverse=True)


def normalize(name: str) -> str:
    """Токени без організаційно-правових форм на початку/в кінці."""
    tokens = _clean(name)
    changed = True
    while changed:
        changed = False
        for form in LEGAL_FORMS:
            n = len(form)
            if len(tokens) > n and tuple(tokens[-n:]) == form:
                tokens, changed = tokens[:-n], True
            elif len(tokens) > n and tuple(tokens[:n]) == form:
                tokens, changed = tokens[n:], True
    return " ".join(tokens)


# ----------------------------------------------------------------------------
# Адреси
# ----------------------------------------------------------------------------

_ABBR = {
    "st": "street", "str": "street", "ave": "avenue", "av": "avenue", "rd": "road", "dr": "drive",
    "blvd": "boulevard", "ln": "lane", "ct": "court", "pl": "place", "hwy": "highway",
    "pkwy": "parkway", "cir": "circle", "ter": "terrace", "sq": "square",
    "ste": "suite", "apt": "suite", "unit": "suite", "fl": "floor",
    "n": "north", "s": "south", "e": "east", "w": "west",
}
_STREET_TYPES = {"street", "avenue", "road", "drive", "boulevard", "lane", "court", "place",
                 "highway", "parkway", "circle", "terrace", "square"}
_COUNTRY_TAIL = re.compile(r"[\s,]*(usa|u\.s\.a\.?|us|u\.s\.|united states( of america)?)\.?\s*$", re.I)
_ZIP_TAIL = re.compile(r"\b(\d{5})(?:[-\s]?\d{4})?\s*$")


def parse_address(addr: str | None) -> dict:
    """-> {'zip': '01060', 'number': '64', 'street_name': 'gothic'}"""
    if not addr:
        return {"zip": None, "number": None, "street_name": ""}
    s = _COUNTRY_TAIL.sub("", addr.strip())
    m = _ZIP_TAIL.search(s)
    zip5 = m.group(1) if m else None
    if m:
        s = s[: m.start()]
    m = re.search(r"\d+", s)
    number = ((m.group(0).lstrip("0")) or "0") if m else None
    line = re.sub(r"\bp o box\b", "po box", " ".join(_clean(s)))
    tokens = [_ABBR.get(t, t) for t in line.split() if not t.isdigit()]
    # назва вулиці = токени до слова-типу (street/avenue/...); якщо типу нема — перші два токени
    idx = next((i for i, t in enumerate(tokens) if t in _STREET_TYPES), None)
    name_tokens = tokens[:idx] if idx else tokens[:2]
    return {"zip": zip5, "number": number, "street_name": " ".join(name_tokens)}


def address_status(block_addr: str | None, oc_addr: str | None) -> str:
    """MATCH / MISMATCH / UNKNOWN (UNKNOWN = замало даних, напр. в OC лише штат)."""
    b, o = parse_address(block_addr), parse_address(oc_addr)
    if not (b["number"] or b["zip"]) or not (o["number"] or o["zip"]):
        return "UNKNOWN"
    if b["number"] and o["number"] and b["number"] != o["number"]:
        return "MISMATCH"
    if b["zip"] and o["zip"] and b["zip"] != o["zip"]:
        return "MISMATCH"
    if b["number"] and o["number"]:
        if b["zip"] and o["zip"]:
            return "MATCH"
        # zip немає з одного боку — додатково звіряємо назву вулиці
        if b["street_name"] and o["street_name"] and fuzz.ratio(b["street_name"], o["street_name"]) >= 85:
            return "MATCH"
    return "UNKNOWN"


def get_oc_address(c: dict | None) -> str | None:
    """Адреса компанії з відповіді OC (рядок, або зібрана зі структурованого поля)."""
    if not c:
        return None
    full = c.get("registered_address_in_full")
    if full:
        return " ".join(str(full).split())
    ra = c.get("registered_address")
    if isinstance(ra, dict):
        parts = [ra.get(k) for k in ("street_address", "locality", "region", "postal_code")]
        s = ", ".join(str(p) for p in parts if p)
        return s or None
    return None


# ----------------------------------------------------------------------------
# Логіка рішення (чиста функція — легко тестувати без мережі)
# ----------------------------------------------------------------------------


def score(target: str, candidate_name: str) -> float:
    t, c = normalize(target), normalize(candidate_name)
    if t and t == c:
        return 100.0
    return float(fuzz.token_sort_ratio(t, c))


def evaluate(target: str, candidates: list[dict], block_addr: str | None = None):
    """Повертає (verdict, top_score, top_candidate, addr_status)."""
    if not candidates:
        return "NOT_FOUND", 0.0, None, None

    scored = sorted(((score(target, c.get("name", "")), c) for c in candidates), key=lambda x: x[0], reverse=True)
    top_score, top = scored[0]

    strong = [(s, c, address_status(block_addr, get_oc_address(c))) for s, c in scored if s >= MATCH_THRESHOLD]
    if not strong:
        if top_score >= REVIEW_THRESHOLD:
            return "REVIEW", top_score, top, address_status(block_addr, get_oc_address(top))
        return "NOT_FOUND", top_score, None, None

    # адреса допомагає обрати "ту саму" компанію серед однойменних, активні мають пріоритет
    pool = [x for x in strong if x[2] == "MATCH"] or strong
    pool = [x for x in pool if not x[1].get("inactive")] or pool
    s, c, addr = pool[0]

    if len(pool) > 1:
        return "MULTIPLE", s, c, addr
    if c.get("inactive"):
        return "INACTIVE", s, c, addr
    return {"MATCH": "OK", "UNKNOWN": "CHECK_ADDRESS", "MISMATCH": "ADDRESS_MISMATCH"}[addr], s, c, addr


# ----------------------------------------------------------------------------
# API
# ----------------------------------------------------------------------------


class QuotaExceeded(Exception):
    pass


class AuthError(Exception):
    pass


class ApiError(Exception):
    pass


def search(session: requests.Session, query: str, token: str, jurisdiction: str | None = None) -> list[dict]:
    params = {"q": query, "api_token": token, "per_page": 30}
    if jurisdiction:
        params["jurisdiction_code"] = jurisdiction

    for attempt in range(3):
        try:
            r = session.get(API_URL, params=params, timeout=30)
        except requests.RequestException as e:
            if attempt == 2:
                raise ApiError(f"мережа: {e}") from e
            time.sleep(2 ** attempt)
            continue

        if r.status_code == 200:
            data = r.json()
            return [item["company"] for item in data["results"]["companies"]]
        if r.status_code in (403, 429):  # за докою OC: 403 = rate limit exceeded
            raise QuotaExceeded(f"HTTP {r.status_code}: ліміт вичерпано")
        if r.status_code == 401:
            raise AuthError("HTTP 401: перевір OPENCORPORATES_TOKEN")
        if r.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        raise ApiError(f"HTTP {r.status_code}: {r.text[:200]}")
    raise ApiError("сервер відповідає помилками 5xx")


# ----------------------------------------------------------------------------
# Розбір блоків з блокнота
# ----------------------------------------------------------------------------

US_STATES = set(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM "
    "NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
)


def _field(text: str, label: str) -> str | None:
    """Перше входження 'label: значення' на початку рядка."""
    m = re.search(rf"^{re.escape(label)}:[ \t]*(.+?)[ \t]*$", text, re.M | re.I)
    return m.group(1) if m else None


def parse_block(block: str) -> dict | None:
    first_line = next((ln.strip() for ln in block.splitlines() if ln.strip()), None)
    name = _field(block, "Title") or first_line
    if not name:
        return None

    ein = re.sub(r"\D", "", _field(block, "EIN") or "") or None
    address = _field(block, "Address")

    state = (_field(block, "state") or "").strip().upper()
    if state not in US_STATES:  # запасний варіант: з рядка Address ("..., Marion, MA, 02738")
        m = re.search(r"^Address:.*?,\s*([A-Z]{2}),?\s*\d{5}", block, re.M)
        state = m.group(1) if m and m.group(1) in US_STATES else None

    site = None
    m = re.search(r"^Web-site:[ \t]*(.+)$", block, re.M | re.I)
    if m:
        u = re.search(r"\((https?://[^)\s]+)\)", m.group(1))
        site = u.group(1) if u else m.group(1).strip()

    return {
        "name": name.strip(),
        "has_title": bool(_field(block, "Title")),
        "ein": ein,
        "state": state,
        "city": _field(block, "city"),
        "address": address,
        "website": site,
        "info": block.strip(),
    }


def load_companies(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8-sig")
    blocks = [b.strip() for b in re.split(r"^={3,}[ \t]*$", text, flags=re.M)]
    return [c for c in (parse_block(b) for b in blocks if b) if c]


# ----------------------------------------------------------------------------
# SQLite: стан + добовий лічильник
# ----------------------------------------------------------------------------


def init_db(path: str = DB_PATH) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    cols = {r[1] for r in db.execute("PRAGMA table_info(companies)")}
    if cols and not {"key", "addr_status"} <= cols:
        sys.exit(f"Стара схема БД — видали {path} і запусти знову.")
    db.execute(
        """CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,      -- EIN, а якщо його нема: назва|штат
            name TEXT NOT NULL,
            ein TEXT,
            state TEXT,
            city TEXT,
            address TEXT,
            website TEXT,
            info TEXT,
            verdict TEXT NOT NULL DEFAULT 'PENDING',
            addr_status TEXT,
            score REAL,
            matched_name TEXT,
            oc_address TEXT,
            jurisdiction TEXT,
            company_number TEXT,
            current_status TEXT,
            inactive INTEGER,
            oc_url TEXT,
            checked_at TEXT,
            raw TEXT
        )"""
    )
    db.execute("CREATE TABLE IF NOT EXISTS api_calls (day TEXT PRIMARY KEY, count INTEGER NOT NULL)")
    db.commit()
    return db


def calls_today(db: sqlite3.Connection) -> int:
    row = db.execute("SELECT count FROM api_calls WHERE day = ?", (date.today().isoformat(),)).fetchone()
    return row[0] if row else 0


def register_call(db: sqlite3.Connection) -> None:
    db.execute(
        "INSERT INTO api_calls(day, count) VALUES(?, 1) "
        "ON CONFLICT(day) DO UPDATE SET count = count + 1",
        (date.today().isoformat(),),
    )
    db.commit()


def save_result(db, row_id, verdict, top_score, top, addr_status, raw_candidates):
    matched = top if verdict != "NOT_FOUND" else None
    db.execute(
        """UPDATE companies SET verdict=?, addr_status=?, score=?, matched_name=?, oc_address=?,
               jurisdiction=?, company_number=?, current_status=?, inactive=?, oc_url=?,
               checked_at=?, raw=?
           WHERE id=?""",
        (
            verdict,
            addr_status,
            round(top_score, 1),
            matched.get("name") if matched else None,
            get_oc_address(matched),
            matched.get("jurisdiction_code") if matched else None,
            matched.get("company_number") if matched else None,
            matched.get("current_status") if matched else None,
            int(bool(matched.get("inactive"))) if matched else None,
            matched.get("opencorporates_url") if matched else None,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            json.dumps(raw_candidates[:3], ensure_ascii=False),
            row_id,
        ),
    )
    db.commit()


def mark_skipped(db: sqlite3.Connection, row_id: int, verdict: str) -> None:
    db.execute(
        "UPDATE companies SET verdict=?, checked_at=? WHERE id=?",
        (verdict, datetime.now(timezone.utc).isoformat(timespec="seconds"), row_id),
    )
    db.commit()


def check_input(companies: list[dict], skip_states: set[str], has_override: bool) -> None:
    """Звіт по файлу без токена й без запитів до API."""
    from collections import Counter

    total = len(companies)
    no_title = [c for c in companies if not c["has_title"]]
    no_state = [c for c in companies if not c["state"]]
    no_addr = [c for c in companies if not c["address"]]
    skipped = [c for c in companies if c["state"] in skip_states]
    no_ein = [c for c in companies if not c["ein"]]
    ein_dups = [e for e, n in Counter(c["ein"] for c in companies if c["ein"]).items() if n > 1]
    name_dups = [n for n, k in Counter(c["name"].casefold() for c in companies).items() if k > 1]
    eligible = [c for c in companies if c["state"] not in skip_states and (c["state"] or has_override)]
    will_search = len({c["ein"] or f"{c['name']}|{c['state'] or ''}" for c in eligible})

    print(f"Блоків: {total}")
    print(f"  без 'Title:' (назва = перший рядок): {len(no_title)}")
    print(f"  без EIN: {len(no_ein)} | без Address: {len(no_addr)} (для них адреса буде UNKNOWN)")
    print(f"  штат не визначено: {len(no_state)}" + ("" if has_override else "  -> будуть SKIPPED_NO_STATE"))
    print(f"  штати {sorted(skip_states)} (пропуск): {len(skipped)}")
    print(f"  дублікати EIN: {len(ein_dups)} (беруться лише перший блок) | однакові назви: {len(name_dups)}")
    print(f"Піде в API: {will_search}")
    print("Топ штатів:", ", ".join(f"{k or '-'}:{v}" for k, v in Counter(c["state"] for c in companies).most_common(8)))
    for label, items in (("Без Title", no_title), ("Без штату", no_state)):
        if items:
            print(f"\n{label} (перші 10):")
            for c in items[:10]:
                print("  -", c["name"][:80])


def export_csv(db: sqlite3.Connection, out_path: str) -> None:
    cur = db.execute(
        """SELECT name, ein, state, city, address, verdict, addr_status, score, matched_name, oc_address,
                  jurisdiction, company_number, current_status, inactive, oc_url, checked_at, website, info
           FROM companies ORDER BY id"""
    )
    headers = [d[0] for d in cur.description]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: Excel читає без крякозябр
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(cur)


# ----------------------------------------------------------------------------
# Основний цикл
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Перевірка компаній через OpenCorporates")
    ap.add_argument("input", help="txt-файл з блоками, розділеними рядком ===")
    ap.add_argument("--jurisdiction", help="примусовий код юрисдикції (pl, gb, us_ma...); за замовчуванням береться зі штату блоку")
    ap.add_argument("--limit", type=int, default=DAILY_LIMIT, help="макс. запитів за добу")
    ap.add_argument("--out", default="results.csv")
    ap.add_argument("--skip-states", default="MD", help="штати, які пропускаємо (через кому), за замовчуванням MD")
    ap.add_argument("--check", action="store_true", help="лише звіт по файлу, без API й без токена")
    args = ap.parse_args()

    skip_states = {x.strip().upper() for x in args.skip_states.split(",") if x.strip()}
    companies = load_companies(args.input)
    if args.check:
        check_input(companies, skip_states, bool(args.jurisdiction))
        return

    token = os.environ.get("OPENCORPORATES_TOKEN")
    if not token:
        sys.exit("Задай змінну середовища OPENCORPORATES_TOKEN")

    db = init_db()
    for c in companies:
        key = c["ein"] or f"{c['name']}|{c['state'] or ''}"
        db.execute(
            "INSERT OR IGNORE INTO companies(key, name, ein, state, city, address, website, info) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (key, c["name"], c["ein"], c["state"], c["city"], c["address"], c["website"], c["info"]),
        )
    db.commit()

    pending = db.execute(
        "SELECT id, name, state, address FROM companies WHERE verdict='PENDING' ORDER BY id"
    ).fetchall()

    # 1) пропуски без API: штат у списку виключень / штат не визначено
    to_search, skipped = [], 0
    for row_id, name, state, address in pending:
        if state and state in skip_states:
            mark_skipped(db, row_id, "SKIPPED_STATE")
            skipped += 1
        elif not state and not args.jurisdiction:
            mark_skipped(db, row_id, "SKIPPED_NO_STATE")
            skipped += 1
        else:
            to_search.append((row_id, name, state, address))
    print(f"До пошуку: {len(to_search)} | пропущено без запитів: {skipped} | використано сьогодні: {calls_today(db)}/{args.limit}")

    with requests.Session() as session:
        for row_id, name, state, address in to_search:
            if calls_today(db) >= args.limit:
                print("Ліміт на сьогодні вичерпано — продовжиш завтра.")
                break
            # --jurisdiction має пріоритет; інакше зі штату блоку (MA -> us_ma)
            jurisdiction = args.jurisdiction or (f"us_{state.lower()}" if state else None)
            try:
                candidates = search(session, name, token, jurisdiction)
            except QuotaExceeded as e:
                print(f"Ліміт API: {e}. Зупиняюсь.")
                break
            except AuthError as e:
                print(f"Помилка авторизації: {e}. Зупиняюсь.")
                break
            except ApiError as e:
                print(f"[skip] {name}: {e} (залишиться в черзі)")
                continue

            register_call(db)
            verdict, top_score, top, addr_status = evaluate(name, candidates, address)
            save_result(db, row_id, verdict, top_score, top, addr_status, candidates)
            print(
                f"{verdict:16} {top_score:5.1f} addr={addr_status or '-':8} "
                f"{name} [{jurisdiction or '-'}]  ->  {top.get('name') if top else '-'}"
            )
            time.sleep(REQUEST_DELAY)

    export_csv(db, args.out)
    left = db.execute("SELECT COUNT(*) FROM companies WHERE verdict='PENDING'").fetchone()[0]
    print(f"Готово. Файл: {args.out} | залишилось у черзі: {left}")


if __name__ == "__main__":
    main()
