#!/usr/bin/env python3
"""
PhoneBook Extended Console Application (simplified version)
All functionality preserved (TSIS 1)
"""

import csv
import json
import os
import sys
from datetime import datetime, date

import psycopg2
import psycopg2.extras

from connect import get_connection
from config import PAGE_SIZE


# ─────────────────────────────────────────────
# DB helper
# ─────────────────────────────────────────────
def query(conn, sql, params=None, fetch=False):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()


# ─────────────────────────────────────────────
# Utils
# ─────────────────────────────────────────────
def d(row): return dict(row)


def print_contacts(rows):
    if not rows:
        print(" (no contacts)")
        return

    print("─" * 70)
    for r in rows:
        r = d(r)
        bd = r.get("birthday")
        bd = bd.strftime("%Y-%m-%d") if isinstance(bd, date) else bd or "—"

        print(
            f"Name: {r.get('name')}\n"
            f"Username: {r.get('username')}\n"
            f"Email: {r.get('email') or '—'}\n"
            f"Birthday: {bd}\n"
            f"Group: {r.get('group_name') or '—'}\n"
            f"Phones: {r.get('phones') or '—'}\n"
            f"Created: {r.get('created_at')}\n"
            "─" * 70
        )


def inp(text, default=None):
    v = input(f"{text} [{default}]: " if default else f"{text}: ").strip()
    return v or default


def choose(options, title="Choice"):
    for i, o in enumerate(options, 1):
        print(i, o)
    while True:
        v = input(f"{title}: ")
        if v.isdigit() and 1 <= int(v) <= len(options):
            return options[int(v) - 1]


# ─────────────────────────────────────────────
# Groups
# ─────────────────────────────────────────────
def groups(conn):
    return query(conn, "SELECT id, name FROM groups ORDER BY name", fetch=True)


def group_id(conn, name):
    r = query(conn, "SELECT id FROM groups WHERE name=%s", (name,))
    if r:
        return r[0]["id"]
    r = query(conn,
              "INSERT INTO groups(name) VALUES(%s) RETURNING id",
              (name,), fetch=True)
    conn.commit()
    return r[0]["id"]


# ─────────────────────────────────────────────
# Contacts
# ─────────────────────────────────────────────
def add_contact(conn):
    name = inp("Name")
    username = inp("Username")
    email = inp("Email", "")
    b = inp("Birthday YYYY-MM-DD", "")

    birthday = None
    if b:
        try:
            birthday = datetime.strptime(b, "%Y-%m-%d").date()
        except:
            pass

    g = groups(conn)
    gnames = [x["name"] for x in g] + ["skip"]
    chosen = choose(gnames, "Group")

    gid = None
    if chosen != "skip":
        gid = next(x["id"] for x in g if x["name"] == chosen)

    try:
        r = query(conn,
            """INSERT INTO contacts(name, username, email, birthday, group_id)
               VALUES (%s,%s,%s,%s,%s) RETURNING id""",
            (name, username, email or None, birthday, gid),
            fetch=True
        )
        cid = r[0]["id"]

        while True:
            phone = inp("Phone (empty stop)", "")
            if not phone:
                break
            ptype = choose(["mobile", "home", "work"])
            query(conn,
                  "INSERT INTO phones(contact_id, phone, type) VALUES (%s,%s,%s)",
                  (cid, phone, ptype))
        conn.commit()
        print("✓ Added")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("Username exists")


# ─────────────────────────────────────────────
# Search / filters
# ─────────────────────────────────────────────
def filter_group(conn):
    g = groups(conn)
    chosen = choose([x["name"] for x in g])

    rows = query(conn, """
        SELECT c.*, g.name group_name,
        STRING_AGG(p.phone, ', ') phones
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        WHERE g.name=%s
        GROUP BY c.id, g.name
    """, (chosen,), fetch=True)

    print_contacts(rows)


def search_email(conn):
    q = inp("Email fragment")

    rows = query(conn, """
        SELECT c.*, g.name group_name,
        STRING_AGG(p.phone, ', ') phones
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        WHERE c.email ILIKE %s
        GROUP BY c.id, g.name
    """, (f"%{q}%",), fetch=True)

    print_contacts(rows)


def list_sorted(conn):
    sort = choose(["name", "birthday", "created_at"])

    rows = query(conn, f"""
        SELECT c.*, g.name group_name,
        STRING_AGG(p.phone, ', ') phones
        FROM contacts c
        LEFT JOIN groups g ON g.id=c.group_id
        LEFT JOIN phones p ON p.contact_id=c.id
        GROUP BY c.id, g.name
        ORDER BY c.{sort} NULLS LAST
    """, fetch=True)

    print_contacts(rows)


# ─────────────────────────────────────────────
# Pagination
# ─────────────────────────────────────────────
def paginate(conn):
    page = 0
    total = query(conn, "SELECT COUNT(*) FROM contacts")[0]["count"]
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    while True:
        rows = query(conn,
            "SELECT * FROM get_contacts_page(%s,%s)",
            (PAGE_SIZE, page * PAGE_SIZE),
            fetch=True
        )

        print(f"\nPage {page+1}/{pages}")
        print_contacts(rows)

        action = choose(
            ["next", "prev", "quit"] if page else ["next", "quit"]
        )

        if action == "next":
            page += 1
        elif action == "prev":
            page -= 1
        else:
            break


# ─────────────────────────────────────────────
# JSON / CSV
# ─────────────────────────────────────────────
def export_json(conn):
    path = inp("File", "export.json")

    contacts = query(conn, "SELECT * FROM contacts", fetch=True)
    phones = query(conn, "SELECT * FROM phones", fetch=True)

    by_id = {}
    for p in phones:
        by_id.setdefault(p["contact_id"], []).append(p)

    out = []
    for c in contacts:
        c = d(c)
        c["phones"] = by_id.get(c["id"], [])
        out.append(c)

    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)

    print("Exported")


def import_csv(conn):
    path = inp("CSV", "contacts.csv")
    if not os.path.exists(path):
        return

    data = {}

    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            u = row["username"]
            data.setdefault(u, {
                "name": row["name"],
                "email": row.get("email"),
                "group": row.get("group"),
                "phones": []
            })
            if row.get("phone"):
                data[u]["phones"].append((row["phone"], row.get("phone_type")))

    for u, v in data.items():
        if query(conn, "SELECT 1 FROM contacts WHERE username=%s", (u,)):
            continue

        gid = group_id(conn, v["group"]) if v["group"] else None

        cid = query(conn,
            """INSERT INTO contacts(name, username, email, group_id)
               VALUES (%s,%s,%s,%s) RETURNING id""",
            (v["name"], u, v["email"], gid),
            fetch=True
        )[0]["id"]

        for ph, t in v["phones"]:
            query(conn,
                  "INSERT INTO phones(contact_id, phone, type) VALUES (%s,%s,%s)",
                  (cid, ph, t or "mobile"))

    conn.commit()
    print("CSV imported")


# ─────────────────────────────────────────────
# Stored procedures
# ─────────────────────────────────────────────
def call_proc(conn, name):
    c = inp("Contact")
    v = inp("Value")
    try:
        query(conn, f"CALL {name}(%s,%s)", (c, v))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)


# ─────────────────────────────────────────────
# Menu
# ─────────────────────────────────────────────
def main():
    conn = get_connection()

    menu = {
        "1": add_contact,
        "2": filter_group,
        "3": search_email,
        "4": list_sorted,
        "5": paginate,
        "6": export_json,
        "7": import_csv,
        "8": lambda c: call_proc(c, "add_phone"),
        "9": lambda c: call_proc(c, "move_to_group"),
        "0": lambda c: sys.exit()
    }

    while True:
        print("""
1 Add contact
2 Filter group
3 Search email
4 Sorted list
5 Pagination
6 Export JSON
7 Import CSV
8 Add phone (proc)
9 Move group (proc)
0 Exit
""")

        ch = input(">> ")
        if ch in menu:
            menu[ch](conn)


if __name__ == "__main__":
    main()