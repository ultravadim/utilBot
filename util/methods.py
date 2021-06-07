import requests


class Method(object):
    r = requests.Session()

    def __init__(self):
        pass

    def mail(self, guid=None, stand=None):
        response_json = self.r.get(f'http://util.ao5.in/support/api/{stand}/getProductEmail/{guid}').json()
        return response_json