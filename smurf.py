#!/usr/bin/env python

import sqlite3
import requests
from pathlib import Path

DB_FILE = Path("database.sqlite3")

# Инициализация базы данных
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT UNIQUE NOT NULL
            );
        """)
        conn.commit()

def getip() -> str:
    try:
        response = requests.get('https://api.ipify.org', timeout=2).text
        return response
    except Exception as e:
        return f"Error retrieving IP: {e}"

def checkip(ip: str) -> bool:
    if ip.startswith("Error"):
        return False
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM known_ips WHERE ip = ?", (ip,))
        return cursor.fetchone() is not None

def addip(ip: str) -> None:
    if ip.startswith("Error"):
        return
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO known_ips (ip) VALUES (?)", (ip,))
            conn.commit()
        except sqlite3.IntegrityError:
            # IP уже есть
            pass

if __name__ == "__main__":
    init_db()
    ip = getip()
    print(f"Твой IP: {ip}")
    in_db = checkip(ip)
    print(f"Наличие в базе: {in_db}")
    if not in_db:
        answer = input("Добавить IP в базу? (Yes/No): ").strip().lower()
        if answer in ["yes", "y"]:
            addip(ip)
            print("IP добавлен в базу.")
        else:
            print("IP не был добавлен.")
