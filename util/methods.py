import requests


class Method(object):
    r = requests.Session()

    def __init__(self, base_url):
        self.base_url = base_url

    def mail(self, guid: str, stand: str):
        return self.r.get(f'{self.base_url}/support/api/{stand}/getProductEmail/{guid}').json()

    def publish_info(self, guid: str, stand: str):
        return self.r.post(f'{self.base_url}/support/api/{stand}/publishProductInfo/{guid}').json()

    def reset_request_status(self, request_guid: str, stand: str):
        return self.r.post(f'{self.base_url}/support/api/{stand}/resetRequestStatus/{request_guid}').json()

    def update_request_status(self, request_guid: str, stand: str):
        return self.r.post(f'{self.base_url}/support/api/{stand}/updateRequest/{request_guid}').json()

    def update_abonents(self, guid: str, stand: str):
        data = {'products': [f"{guid}"]}
        return self.r.put(f'{self.base_url}/support/api/{stand}/updateAbonents', json=data).json()