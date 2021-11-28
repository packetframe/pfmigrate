#!/usr/bin/python3

import requests
from PyInquirer import style_from_dict, prompt, Token
from rich.console import Console
from rich.traceback import install

# Register rich traceback hook
install()

console = Console()

LEGACY_API = "https://packetframe.com/api"
V4_API = "https://v4.packetframe.com/api"

PYINQUIRER_STYLE = style_from_dict({
    Token.Separator: "#6C6C6C",
    Token.QuestionMark: "#FFF",
    Token.Selected: "#dd00ff",
    Token.Pointer: "#FFF",
    Token.Instruction: "",
    Token.Answer: "#dd00ff",
    Token.Question: "",
})

API_KEY = ""
V4_API_KEY = ""


def legacy_request(message, route, method, body=None):
    with console.status(f"[bold green]{message}..."):
        r = requests.request(method, LEGACY_API + route, json=body, headers={"X-API-Key": API_KEY})
        if r.status_code != 200:
            console.log(f"[bold red]ERROR (request)[reset] code {r.status_code} body {r.text}")
            exit(1)
        elif not r.json()["success"]:
            console.log(f"[bold red]ERROR (api)[reset] {r.json()['message']}")
            exit(1)
        return r.json()["message"]


def legacy_login():
    console.print("[underline]Packetframe (Legacy) Login")
    account = prompt([
        {
            "type": "input",
            "name": "username",
            "message": "Email:",
        },
        {
            "type": "password",
            "message": "Password:",
            "name": "password"
        }
    ], style=PYINQUIRER_STYLE)

    if account:
        r = legacy_request(f"Logging in as {account['username']}", "/auth/login", "POST", account)
        console.print("[bold green]Login successful")
        global API_KEY
        API_KEY = r


def v4_login():
    console.print("[underline]Packetframe (v4) Login")
    account = prompt([
        {
            "type": "input",
            "name": "username",
            "message": "Email:",
        },
        {
            "type": "password",
            "message": "Password:",
            "name": "password"
        }
    ], style=PYINQUIRER_STYLE)

    if account:
        r = requests.request("POST", "https://v4.packetframe.com/api/user/login", json={
            "email": account["username"],
            "password": account["password"]
        })
        if r.status_code != 200:
            print("Invalid username or password")
            exit(1)

        global V4_API_KEY
        V4_API_KEY = r.json()["data"]["token"]


def select_zone():
    zones = legacy_request("Getting zones", "/zones/list", "GET")
    answer = prompt([
        {
            "type": "list",
            "name": "Zone",
            "message": "Which zone do you want to migrate?",
            "choices": map(lambda z: z["zone"], zones),
        },
    ], style=PYINQUIRER_STYLE)["Zone"]

    for zone in zones:
        if zone["zone"] == answer:
            confirm = prompt(questions=[
                {
                    "type": "confirm",
                    "message": f"Are you sure you want to migrate {zone['zone']}?",
                    "name": "continue",
                    "default": False,
                },
            ], style=PYINQUIRER_STYLE)["continue"]
            if not confirm:
                print("Migration cancelled")
                exit()

            with console.status(f"[bold green]Adding zone..."):
                r = requests.request("POST", V4_API + "/dns/zones", json={"zone": zone["zone"]}, headers={"Authorization": "Token " + V4_API_KEY})
                if r.status_code != 200:
                    print(f"Error adding zone: {r.text}")

            zone_id = ""
            r = requests.request("GET", V4_API + "/dns/zones", json={}, headers={"Authorization": "Token " + V4_API_KEY})
            for z in r.json()["data"]["zones"]:
                if z["zone"] == zone["zone"] + ".":
                    zone_id = z["id"]

            with console.status(f"[bold green]Adding records..."):
                for record in zone["records"]:
                    r = requests.request("POST", V4_API + "/dns/records", json={
                        "zone": zone_id,
                        "label": record["label"],
                        "ttl": record["ttl"],
                        "type": record["type"],
                        "value": record["value"]
                    }, headers={"Authorization": "Token " + V4_API_KEY})
                    if r.status_code != 200:
                        print(f"Unable to add record ({record['label']} {record['type']} {record['ttl']} {record['value']}): {r.text}")

            print(f"Zone {zone['zone']} migrated successfully!")


legacy_login()
v4_login()
select_zone()
