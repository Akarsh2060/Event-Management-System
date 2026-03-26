import requests

def send_otp_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": "kd0EVmFN5KfsRiQuSUMplCG6ZHcAT4xPOeDIYJt1XrW8a2gonvD6iHkzgyFXONhK4fuv9IGMYV8lA17a",
        "Content-Type": "application/json"
    }

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()