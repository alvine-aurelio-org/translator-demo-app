import requests
import time

# Replace with your actual values
endpoint = "https://ustranslate001.cognitiveservices.azure.com/translator/document/batches?api-version=2025-12-01-preview"
api_key = "7VPvds3ZrIh96lIkbqstwOuk6Awb6qjQqSxLktwi1BhPXzH9BDLQJQQJ99CAACHYHv6XJ3w3AAAbACOGc7Vi"
region = "eastus2"

# Use valid SAS URLs for your test files
source_url = "https://ussampleeastus2storev2.blob.core.windows.net/source-docs/mission.txt?se=2026-02-05T07%3A20%3A35Z&sp=racwdl&spr=https&sv=2022-11-02&sr=c&sig=E3yHf4LVA0Fspt2234qHoAonBuNBpXrh9Z9oF6v1xCY%3D"
target_url = "https://ussampleeastus2storev2.blob.core.windows.net/translated-docs/mission-ed.txt?se=2026-12-05T07%3A20%3A35Z&sp=racwdl&spr=https&sv=2022-11-02&sr=c&sig=ZPJIj67RHhuRzcNOICpe%2BvP4ZyKFmV4t6tp4eAsXXiQ%3D"

headers = {
    "Ocp-Apim-Subscription-Key": api_key,
    "Ocp-Apim-Subscription-Region": region,
    "Content-Type": "application/json"
}

body = {
    "inputs": [
        {
            "storageType": "File",
            "source": {
                "sourceUrl": source_url,
                # "language": "fr"  # Uncomment and set if you want to specify
            },
            "targets": [
                {
                    "targetUrl": target_url,
                    "language": "en"
                }
            ]
        }
    ]
}

print("Submitting translation job...")
response = requests.post(endpoint, headers=headers, json=body)
print("Status:", response.status_code)
print("Response:", response.text)

if response.status_code in (200, 202):
    op_url = response.headers.get("operation-location")
    print("Operation URL:", op_url)
    if op_url:
        print("Polling job status...")
        for _ in range(10):
            status_resp = requests.get(op_url, headers=headers)
            print("Status:", status_resp.status_code)
            print("Body:", status_resp.text)
            if status_resp.status_code == 200 and 'Succeeded' in status_resp.text:
                print("Job succeeded!")
                break
            time.sleep(5)
else:
    print("Job submission failed.")
