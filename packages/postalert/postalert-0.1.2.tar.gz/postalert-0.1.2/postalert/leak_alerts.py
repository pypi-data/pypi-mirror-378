import os
import json
import requests
import platform
import whispers

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"  # Replace with your webhook

def save_leak_json(output_base_folder, domain, leak_data):
    domain_folder = os.path.join(output_base_folder, domain)
    os.makedirs(domain_folder, exist_ok=True)
    file_path = os.path.join(domain_folder, "secrets.json")
    # Load existing secrets if present
    existing = {}
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            existing = json.load(f)
    # Store leak data keyed by leak id
    existing[leak_data['id']] = leak_data
    with open(file_path, 'w') as f:
        json.dump(existing, f, indent=2)
    return file_path

def load_existing_leak_ids(output_base_folder, domain):
    domain_folder = os.path.join(output_base_folder, domain)
    file_path = os.path.join(domain_folder, "secrets.json")
    if not os.path.isfile(file_path):
        return set()
    with open(file_path, 'r') as f:
        data = json.load(f)
    return set(data.keys())

def extract_secrets_from_file(config_yml_path, file_path):
    # Use whispers to get secrets from JSON file
    config_path = config_yml_path
    if platform.system() == 'Windows':
        config_path = config_path.replace("\\", "\\\\")
    secrets_raw = list(whispers.secrets(f"-c {config_path} {file_path}"))
    secrets = list(set(f"Potential secret found: {s.key} = {s.value}" for s in secrets_raw))
    return secrets

def send_slack_alert(leak_info, secrets):
    url = leak_info.get('url', '')
    leak_id = leak_info.get('id', '')
    method = leak_info.get('method', '')
    # Format URL as clickable link in Slack <URL|text> format
    url_formatted = f"<{url}|{url}>"
    secrets_text = "\n".join(secrets) if secrets else "No secrets found"
    text = (
        f"*New Potential Secrets Found:*\n"
        f"Leak ID: {leak_id}\n"
        f"URL: {url_formatted}\n"
        f"Method: {method}\n"
        f"Secrets:\n{secrets_text}"
    )
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    return response.status_code == 200

def process_new_leaks(keyword, output_base_folder, found_leaks, config_yml_path, strict=False):
    domain = keyword.lower()
    existing_ids = load_existing_leak_ids(output_base_folder, domain)
    new_leaks = []

    for leak in found_leaks:
        url = leak.get('url', '').lower()
        leak_id = leak.get('id')
        if strict and keyword.lower() not in url:
            continue
        if leak_id not in existing_ids:
            new_leaks.append(leak)

    for leak in new_leaks:
        # Save leak JSON to outputs/domain/secrets.json
        file_path = save_leak_json(output_base_folder, domain, leak)
        # Extract secrets from JSON file (using config.yml path)
        secrets = extract_secrets_from_file(config_yml_path, file_path)
        # Send Slack alert with secrets
        send_slack_alert(leak, secrets)

    return len(new_leaks)
