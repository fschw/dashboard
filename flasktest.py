from flask import Flask
from flask import request
import requests
import json

app = Flask(__name__)
@app.route("/")
def receive_code():
    code = request.args.get('code', '')
    if code is not "":
        print("Code received:" + code)
        url = "https://iam.viessmann.com/idp/v2/token"
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        data = "grant_type=authorization_code&client_id=9ceff2a5f57d345a580142626e3b4a7f&redirect_uri=http://localhost:4200/&code_verifier=2e21faa1-db2c-4d0b-a10f-575fd372bc8c-575fd372bc8c&code="+code
        response = requests.post(url=url, headers=header, data=data)
        if response.ok:
            access_token = json.loads(response.text).get('access_token')
            header = {"Authorization": "Bearer " + access_token}
            req1 = "https://api.viessmann.com/iot/v1/equipment/installations/952499/gateways/7637415022052208/devices/0/features/heating.sensors.temperature.outside"
            response = requests.get(url=req1, headers=header)

            return "Außentemperatur: " + str(response.json()["data"]["properties"]["value"]["value"])
        else:
            return response
    return "No code received"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4200)