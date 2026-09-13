#!/usr/bin/env python3

from datetime import datetime
import csv
import os
from netmiko import ConnectHandler

### ez a linux szerverünk címe, amin a TFTPD fut
TFTP_SERVER = "192.168.10.20"  

## Eszkozlista IP-kkel
CSV_FILE = "devices.csv"


def backup_device(ip, name, username, password, secret):
    print(f"\nKapcsolódás: {name} ({ip})")

    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
        "secret": secret,
        "port": 22,
        "verbose": False,
    }

    connection = None

    try:
        connection = ConnectHandler(**device)

        # Enable mód
        if secret:
            connection.enable()

        # Kimeneti fájlnév: eszköznév_dátum
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{name}_{date}"

        backup_command = f"copy running-config tftp://{TFTP_SERVER}/{filename}"

        print(f"Futó konfiguráció mentése: {filename}")

        output = connection.send_command_timing(backup_command)

        # Cisco kérdések kezelése
        if "Address or name of remote host" in output:
            output += connection.send_command_timing(TFTP_SERVER)

        if "Destination filename" in output:
            output += connection.send_command_timing(filename)

        # Egyes IOS verziók további megerősítést kérhetnek
        if "confirm" in output.lower():
            output += connection.send_command_timing("")

        print(output)
        print(f"Mentés kész: {name} ({ip})")

    except Exception as e:
        print(f"HIBA: {name} ({ip}): {e}")

    finally:
        if connection:
            connection.disconnect()


def main():
    # Cisco bejelentkezési adatok
    username = "backup"
    password = "5678"
    secret = ""

    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            ip = row["ip"].strip()
            name = row["name"].strip()

            if not ip or not name:
                print("Hibás vagy hiányos CSV sor, kihagyva.")
                continue

            backup_device(ip, name, username, password, secret)


if __name__ == "__main__":
    main()
