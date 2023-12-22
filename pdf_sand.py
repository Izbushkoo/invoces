import json

import requests


url = "https://api.baselinker.com/connector.php"
headers = {"X-BLToken": "4013330-4028709-C9WA9JJT65GUBW355J9LO5F1H6Y490JJ9JP8KDH1WGQDU952HW78LFI8YMFT68BB"}

body_get_order = {
    "method": "getOrders",
    "parameters": json.dumps({"order_id": 31269796})
}
body_set_field = {
    "method": "setOrderFields",
    "parameters": json.dumps({
        "order_id": 31269796,
        "invoice_nip": 1234
    })
}
params = {
    "order_id": 31269796
}

result = requests.post(
    url=url, headers=headers, data=body_set_field
)
# print(len(result.json()['orders']))
with open('response.json', 'w') as file:
    json.dump(result.json(), file, indent=2)
