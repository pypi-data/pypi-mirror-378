#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import json
import time
import requests
import yaml
import re
import threading
import whispers
import tldextract

POSTMAN_HOST = "https://www.postman.com"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_INFO_INTERESTING_DATA = [
    "id", "url", "method", "auth", "queryParams",
    "description", "name", "events", "data", "headerData"
]
ORANGE = '\033[0;35m'
GREEN = '\033[92m'
BLUE = '\033[94m'
BOLD = '\033[1m'
NOCOLOR = '\033[0m'

CONFIG_FILE = os.path.expanduser("~/.postalert_config.json")
CONFIG_YML = os.path.join(os.path.dirname(__file__), 'config.yml')

DISCORD_MSG_INTERVAL = 1.1
_last_msg_time = 0
_lock = threading.Lock()
_last_request_time = 0

def print_banner():
    banner = f"""
{BOLD}{BLUE}██████╗  ██████╗ ███████╗████████╗     █████╗ ██╗     ███████╗██████╗ ████████╗
██╔══██╗██╔═══██╗██╔════╝╚══██╔══╝    ██╔══██╗██║     ██╔════╝██╔══██╗╚══██╔══╝
██████╔╝██║   ██║███████╗   ██║       ███████║██║     █████╗  ██████╔╝   ██║   
██╔═══╝ ██║   ██║╚════██║   ██║       ██╔══██║██║     ██╔══╝  ██╔══██╗   ██║   
██║     ╚██████╔╝███████║   ██║       ██║  ██║███████╗███████╗██║  ██║   ██║   
╚═╝      ╚═════╝ ╚══════╝   ╚═╝       ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝{NOCOLOR}
By Muthu D.
LinkedIn: https://www.linkedin.com/in/anonysm
Email: talktomuthud@gmail.com
"""
    print(banner)

def load_discord_webhook(args):
    config = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
        except Exception:
            pass
    webhook = args.discord_webhook or config.get("discord_webhook")
    if args.discord_webhook and args.discord_webhook != config.get("discord_webhook"):
        config["discord_webhook"] = args.discord_webhook
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            print(f"{GREEN}[+] Discord webhook saved to config file{NOCOLOR}")
        except Exception as e:
            print(f"{ORANGE}[-] Failed to save webhook to config file: {e}{NOCOLOR}")
    if not webhook:
        print(f"{ORANGE}[-] Discord webhook URL must be provided via --discord-webhook or config file{NOCOLOR}")
        sys.exit(1)
    return webhook

def send_discord_alert(webhook_url, message):
    global _last_msg_time
    with _lock:
        elapsed = time.time() - _last_msg_time
        if elapsed < DISCORD_MSG_INTERVAL:
            time.sleep(DISCORD_MSG_INTERVAL - elapsed)
        payload = {"content": message}
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 429:
                retry_after = response.json().get("retry_after", 1)
                print(f"{ORANGE}[-] Discord rate limited, retrying after {retry_after}s...{NOCOLOR}")
                time.sleep(retry_after)
                response = requests.post(webhook_url, json=payload)
            if response.status_code != 204:
                print(f"{ORANGE}[-] Discord alert failed: {response.status_code} {response.text}{NOCOLOR}")
            else:
                _last_msg_time = time.time()
        except Exception as e:
            print(f"{ORANGE}[-] Exception sending Discord alert: {e}{NOCOLOR}")

def safe_request(session, method, url, **kwargs):
    global _last_request_time
    REQUEST_INTERVAL = 0.2
    with _lock:
        elapsed = time.time() - _last_request_time
        if elapsed < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed)
        response = session.request(method, url, **kwargs)
        _last_request_time = time.time()
        if response.status_code == 429:
            print(f"{ORANGE}[-] Rate limit hit, sleeping 60 seconds...{NOCOLOR}")
            time.sleep(60)
            response = session.request(method, url, **kwargs)
            _last_request_time = time.time()
        response.raise_for_status()
        return response

def load_old_alerts(alerts_file):
    if os.path.exists(alerts_file):
        try:
            with open(alerts_file) as f:
                data = json.load(f)
            return set((d['id'], d['key'], d['value']) for d in data)
        except Exception:
            return set()
    return set()

def save_alerts(alerts_file, all_alerts_set):
    alerts_list = [{"id": i, "key": k, "value": v} for (i, k, v) in all_alerts_set]
    with open(alerts_file, "w") as f:
        json.dump(alerts_list, f, indent=2)

def format_alert_message(domain_title, leak_id, request_id, url, method, secrets):
    msg = f"*New Alert for [{domain_title}](http://{domain_title})*\n"
    msg += f"New request ID found: {request_id}\n"
    msg += f"Postman API url: [https://www.postman.com/_api/request/{request_id}](https://www.postman.com/_api/request/{request_id})\n"
    if leak_id and leak_id != request_id:
        msg += f"Leak ID: {leak_id}\n"
    msg += f"URL: [{url}]({url})\n"
    msg += f"Method: {method}\n"
    msg += "Secrets:\n"
    for s in secrets:
        msg += f"Potential secret found: `{s['key']} = {s['value']}`\n"
    return msg

def detect_secrets_for_file(file_path):
    if not file_path:
        return []
    secrets_raw = list(whispers.secrets(f"-c {CONFIG_YML} {file_path}"))
    if secrets_raw:
        seen = set()
        dedup_secrets = []
        for s in secrets_raw:
            if (s.key, s.value) not in seen:
                seen.add((s.key, s.value))
                dedup_secrets.append(s)
        return dedup_secrets
    return []

def process_and_alert_leaks(keyword, output_folder, request_infos, webhook_url, strict=False):
    new_leaks_count = 0
    domain_title = get_domain_title(request_infos, keyword)
    domain_folder = os.path.join(output_folder, domain_title)
    os.makedirs(domain_folder, exist_ok=True)
    alerts_file_path = os.path.join(domain_folder, "alerts.json")
    old_alerts = load_old_alerts(alerts_file_path)
    new_alerts_data = set()

    for info in request_infos:
        leak_id = info.get('id')
        full_request_id = info.get("full_request_id", leak_id)
        method = info.get('method') or "N/A"
        url = info.get('url') or "N/A"
        file_path = info.get("_file_path")

        if not full_request_id:
            continue

        secrets = detect_secrets_for_file(file_path) if file_path else []

        fresh_secrets = []
        for s in secrets:
            secret_tuple = (full_request_id, s.key, s.value)
            if secret_tuple not in old_alerts:
                fresh_secrets.append({"key": s.key, "value": s.value})
                new_alerts_data.add(secret_tuple)

        if fresh_secrets and webhook_url:
            msg = format_alert_message(domain_title, leak_id, full_request_id, url, method, fresh_secrets)
            send_discord_alert(webhook_url, msg)
            new_leaks_count += 1

        new_alerts_data.add((full_request_id, None, None))
    all_alerts = old_alerts.union(new_alerts_data)
    save_alerts(alerts_file_path, all_alerts)
    return new_leaks_count

def get_domain_title(requests, keyword):
    """Return domain from first request URL if it matches keyword, else use keyword as folder/alert name."""
    if requests and requests[0].get("url"):
        domain = extract_registered_domain(requests[0]["url"])
        if domain and domain.lower() in keyword.lower():
            return domain
    return keyword.replace(" ", "_").lower()

def extract_registered_domain(url):
    try:
        ext = tldextract.extract(url)
        if ext.domain and ext.suffix:
            return ext.domain + "." + ext.suffix
    except Exception:
        pass
    return None

def store_temp_json(info, output):
    temp_folder = os.path.join(output, "temp")
    os.makedirs(temp_folder, exist_ok=True)
    filepath = os.path.join(temp_folder, info["id"] + ".json")
    with open(filepath, "w") as f:
        json.dump(info, f, indent=2)
    return filepath

def search_request_info_collection_all_ids(keyword, include_match, exclude_match, extend_workspaces, raw, strict, output):
    print(BLUE + "[*] Looking for data in Postman.com" + NOCOLOR)
    ids = search_requests_ids(keyword)
    print(f"[DEBUG] Found {len(ids)} request IDs for keyword '{keyword}'")
    request_ids = set()
    workspaces_ids = set()
    for i in ids:
        full_request_id = next(iter(i.keys()))
        request_ids.add(full_request_id)
        if extend_workspaces:
            current_ws = i.get(full_request_id, [])
            for w in current_ws:
                workspaces_ids.add(w)
    if extend_workspaces and workspaces_ids:
        new_ids = search_request_ids_for_workspaces_id(workspaces_ids)
        request_ids = request_ids.union(new_ids)
    filtered_request_infos = []
    all_fetched_request_ids = list(request_ids)
    session = requests.Session()
    GET_REQUEST_ENDPOINT = "/_api/request/"
    for rid in request_ids:
        print(f"[DEBUG] Fetching request ID {rid}")
        response = safe_request(session, "GET", POSTMAN_HOST + GET_REQUEST_ENDPOINT + str(rid), headers=HEADERS)
        if response.status_code != 200 or "data" not in response.json():
            request_info = {
                "id": rid.split("-", 1)[1] if "-" in rid else rid,
                "full_request_id": rid,
                "url": None,
                "method": None,
                "_file_path": None
            }
            filtered_request_infos.append(request_info)
            continue
        data = response.json()["data"]
        try:
            request_info = {}
            for key, value in data.items():
                if key in REQUEST_INFO_INTERESTING_DATA:
                    if key == "url" and value:
                        if (include_match and include_match.lower() not in value.lower()) or (exclude_match and exclude_match.lower() in value.lower()):
                            raise StopIteration
                        if strict and keyword.lower() not in value.lower():
                            raise StopIteration
                    request_info[key] = value
            if "collectionId" in data:
                request_info["collectionId"] = data["collectionId"]
            request_info["full_request_id"] = rid
        except StopIteration:
            continue
        else:
            if "url" in request_info:
                file_path = store_temp_json(request_info, output)
                request_info["_file_path"] = file_path
            else:
                request_info["_file_path"] = None
            filtered_request_infos.append(request_info)
    return filtered_request_infos, all_fetched_request_ids

def safe_request(session, method, url, **kwargs):
    global _last_request_time
    REQUEST_INTERVAL = 0.2
    with _lock:
        elapsed = time.time() - _last_request_time
        if elapsed < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed)
        response = session.request(method, url, **kwargs)
        _last_request_time = time.time()
        if response.status_code == 429:
            print(f"{ORANGE}[-] Rate limit hit, sleeping 60 seconds...{NOCOLOR}")
            time.sleep(60)
            response = session.request(method, url, **kwargs)
            _last_request_time = time.time()
        response.raise_for_status()
        return response

def main():
    print_banner()
    parser = argparse.ArgumentParser(description=BOLD + "PostAlert 🚀💧" + NOCOLOR + " Search for sensitive data in Postman public library.")
    parser.add_argument('-k', type=str, required=False, dest='keyword', help="Keyword (Domain, company, etc.)")
    parser.add_argument('-kf', type=str, required=False, dest='keyword_file', help="File containing keywords (one per line)")
    parser.add_argument('--extend-workspaces', action="store_true", default=False, dest='extend_workspaces', help="Extend search on Postman workspaces linked to requests")
    parser.add_argument('--strict', action="store_true", default=False, dest='strict', help="Only include results where keywords are in the URL")
    parser.add_argument('--include', type=str, required=False, dest='include', help="URL must include this string")
    parser.add_argument('--exclude', type=str, required=False, dest='exclude', help="URL must exclude this string")
    parser.add_argument('--raw', action="store_true", default=False, dest='raw', help="Display raw JSON results")
    parser.add_argument('--output', type=str, required=False, dest='output', help="Base output folder (default: outputs)")
    parser.add_argument('--discord-webhook', type=str, required=True, dest='discord_webhook', help="Discord webhook URL for alerts")
    args = parser.parse_args()

    if not args.keyword and not args.keyword_file:
        parser.error("At least one of '-k' or '-kf' is required.")

    keywords = []
    if args.keyword:
        keywords.append(args.keyword)
    if args.keyword_file:
        with open(args.keyword_file, "r") as f:
            keywords.extend(line.strip() for line in f if line.strip())

    output_folder = args.output if args.output and args.output.strip() else "outputs"
    webhook_url = load_discord_webhook(args)

    for keyword in keywords:
        print(BLUE + f"[*] Searching for leaks related to keyword {keyword}" + NOCOLOR)
        request_infos, all_fetched_request_ids = search_request_info_collection_all_ids(keyword, args.include, args.exclude, args.extend_workspaces, args.raw, args.strict, output_folder)

        if not request_infos:
            print(f"{ORANGE}[-] No valid requests found for keyword {keyword}{NOCOLOR}")
            continue

        domain_title = get_domain_title(request_infos, keyword)
        print(BLUE + f"[*] Processing results under domain folder '{domain_title}'" + NOCOLOR)

        new_leaks_count = process_and_alert_leaks(keyword, output_folder, request_infos, webhook_url, strict=args.strict)
        print(BLUE + f"[*] Processed {new_leaks_count} new leaks (saved & alerted) for keyword '{keyword}'." + NOCOLOR)

if __name__ == "__main__":
    main()
