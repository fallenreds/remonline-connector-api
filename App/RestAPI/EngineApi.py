import requests


def ttn_tracking(documents: list):
    request = {
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "Documents": documents

        }
    }
    url = 'https://api.novaposhta.ua/v2.0/json/'
    return requests.post(url, json=request).json()
