from catt.api import CattDevice
from flask import Flask
from flask import request
import json
import time
import threading

app = Flask(__name__)

def send_you_got_mail():
    cast = CattDevice(name="Family Room Google")
    cast.play_url("https://osberg-mailbox.s3.us-east-2.amazonaws.com/youve-got-mail.ogg", resolve=False, block=True)
    time.sleep(10)
    cast.stop()
    print("You've Got Mail")

@app.route('/you-got-mail', methods=['POST'])
def hello_world():
    print('>>>REQUEST')
    print(request.get_json())
    if request.method == 'POST':
        json_body = request.get_json()
        if 'lifecycle' in json_body:
            if json_body['lifecycle'] == 'PING':
                return ping_handle(json_body)
            if json_body['lifecycle'] == 'CONFIGURATION':
                return config_handle(json_body)
            if json_body['lifecycle'] == 'INSTALL':
                return install_handle(json_body)
            if json_body['lifecycle'] == 'UPDATE':
                return update_handle(json_body)
            if json_body['lifecycle'] == 'EVENT':
                return handle_event(json_body)
        else:
            print('ERROR')

def handle_event(json_body):
    if json_body['eventData']['events'][0]['deviceEvent']['value'] == 'open':
        mail_thread = threading.Thread(target=send_you_got_mail)
        mail_thread.start()
    response_val = {
        "eventData": {}
    }
    return json.dumps(response_val)

def config_handle(json_body):
    if json_body['configurationData']['phase'] == 'INITIALIZE':
        print('INSTALL BODY')
        return install_body()
    else:
        print('PAGE ONE BODY')
        return page_one_body()

def install_handle(json_body):
    device_id = json_body['installData']['installedApp']['config']['contactSensor']['deviceConfig']['deviceId']
    response_val = {
        "installData": {}
    }
    return json.dumps(response_val)

def update_handle(json_body):
    response_val = {
        "updateData": {}
    }
    return json.dumps(response_val)

def ping_handle(json_body):
    challenge_value = json_body['pingData']['challenge']
    print(challenge_value)
    return_value = {
        "pingData": {
            "challenge": challenge_value
        }
    }
    return json.dumps(return_value)

def install_body():
    response_val = {
        "configurationData": {
            "initialize": {
                "name": "You've got mail when mailbox opens",
                "description": "When mailbox opens say you've got mail",
                "id": "app",
                "permissions": ["r:devices:*"],
                "firstPageId": "1"
            }
        }
    }
    return json.dumps(response_val)

def page_one_body():
    response_val = {
        "configurationData": {
            "page": {
                "pageId": "1",
                "name": "You've got mail when mailbox opens",
                "complete": "true",
                "sections": [
                    {
                        "name": "When this opens or closes...",
                        "settings": [
                            {
                                "id": "contactSensor",
                                "name": "Which contact sensor?",
                                "description": "Tap to set",
                                "type": "DEVICE",
                                "required": "true",
                                "multiple": "false",
                                "capabilities": [
                                    "contactSensor"
                                ],
                                "permissions": [
                                    "r"
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }
    return json.dumps(response_val)
