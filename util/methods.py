import requests


class Method(object):
    r = requests.Session()

    def mail(self, guid=None, stand=None):
        return self.r.get(f'http://util.ao5.in/support/api/{stand}/getProductEmail/{guid}').json()
