import os
import json
import time
import requests
import smtplib

from email.message import EmailMessage
from concurrent.futures import ThreadPoolExecutor


# =====================================
# Feature 1 & 9
# Load servers from ENV or config file
# =====================================
def load_servers():

    # First check environment variable
    env_servers = os.getenv("SERVERS")

    if env_servers:
        servers = [url.strip() for url in env_servers.split(",")]
        print(f"Loaded {len(servers)} servers from ENV")
        return servers

    # Otherwise use config file
    if os.path.exists("config.json"):

        with open("config.json", "r") as file:
            data = json.load(file)

        servers = data.get("servers", [])

        print(f"Loaded {len(servers)} servers from config file")
        return servers

    raise Exception(
        "No servers found. Use SERVERS env variable or config.json"
    )


# =====================================
# Feature 2,3,4,5,6,12
# Check one server
# =====================================
def check_server(url, retries=2):

    for attempt in range(retries + 1):

        try:

            start_time = time.time()

            response = requests.get(
                url,
                timeout=5
            )

            end_time = time.time()

            response_time = round(
                (end_time - start_time) * 1000
            )

            status = "OK"

            # Status code check
            if response.status_code >= 400:
                status = "DOWN"

            # JSON validation
            json_ok = False

            try:
                data = response.json()

                if data.get("status") == "ok":
                    json_ok = True

            except:
                pass

            return {
                "url": url,
                "status_code": response.status_code,
                "response_time": response_time,
                "status": status,
                "json_ok": json_ok,
                "slow": response_time > 500
            }

        except requests.exceptions.Timeout:

            if attempt < retries:
                continue

            return {
                "url": url,
                "status": "TIMEOUT"
            }

        except Exception:

            if attempt < retries:
                continue

            return {
                "url": url,
                "status": "FAILED"
            }


# =====================================
# Feature 7
# Format output
# =====================================
def format_result(result):

    url = result["url"]

    if result["status"] == "TIMEOUT":
        return f"{url} — TIMEOUT"

    if result["status"] == "FAILED":
        return f"{url} — FAILED"

    output = (
        f"{url} "
        f"— {result['status']} "
        f"({result['status_code']}) "
        f"— {result['response_time']}ms"
    )

    if result["slow"]:
        output += " [slow]"

    if result["json_ok"]:
        output += " [json status=ok]"

    return output


# =====================================
# Feature 13
# Send email alert
# =====================================
def send_email_alert(failed_services):

    if not failed_services:
        return

    try:

        sender = "abiturijee@gmail.com"
        password = "aiyh jwie ovbr uvjz"


        receiver = "abiturije1alicade@gmail.com"

        message = EmailMessage()

        message["Subject"] = "Server Health Alert"
        message["From"] = sender
        message["To"] = receiver

        message.set_content(
            "Failed services:\n\n"
            + "\n".join(failed_services)
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(sender, password)
            smtp.send_message(message)

        print("\nAlert email sent")

    except Exception as error:
        print("\nCould not send email:", error)


# =====================================
# Feature 10 & 11
# Check all servers in parallel
# =====================================
def check_all_servers():

    servers = load_servers()

    failed_services = []

    print("\nChecking servers...\n")

    with ThreadPoolExecutor(max_workers=5) as executor:

        results = list(
            executor.map(check_server, servers)
        )

    for result in results:

        print(format_result(result))

        if result["status"] != "OK":
            failed_services.append(
                result["url"]
            )

    return failed_services


# =====================================
# Main Program
# =====================================
def main():

    failed_services = check_all_servers()

    print("\n" + "=" * 50)

    if failed_services:

        print(
            "\nFailed services:"
        )

        for service in failed_services:
            print("-", service)

        # Save to file
        with open(
            "failed_services.txt",
            "w"
        ) as file:

            for service in failed_services:
                file.write(service + "\n")

        send_email_alert(
            failed_services
        )

    else:
        print(
            "\nAll services are healthy"
        )


if __name__ == "__main__":
    main()