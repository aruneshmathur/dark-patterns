import datetime
from lxml import etree
import requests
from signer import RequestSigner


class Request(object):
    def __init__(self, access_key, secret_key):
        self.signer = RequestSigner(secret_key)
        self.access_key = access_key
        self.secret_key = secret_key

    def _request(self, **kwargs):
        kwargs['AWSAccessKeyId'] = self.access_key
        kwargs['Timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        kwargs['SignatureMethod'] = 'HmacSHA1'
        kwargs['SignatureVersion'] = 2
        kwargs['Signature'] = self.signer.sign(kwargs)
        query_str = self.signer.build_query_str(kwargs)
        request = requests.get('http://%s/?%s' % ('awis.amazonaws.com', query_str))
        return request.text

    def sites(self, query):
        text = self._request(**query)
        root = etree.fromstring(text)
        xpath = etree.XPathEvaluator(root)
        xpath.register_namespace('aws', 'http://awis.amazonaws.com/doc/2005-07-11')
        for site in xpath('//aws:Listing'):
            rv = []
            for child in site.iterchildren():
                rv.append(child.text)
            yield rv

    def rank(self, query):
        text = self._request(**query)
        root = etree.fromstring(text)
        xpath = etree.XPathEvaluator(root)
        xpath.register_namespace('aws', 'http://awis.amazonaws.com/doc/2005-07-11')

        res = xpath('//aws:Value')

        result = None
        try:
            result = res[6].text
        except:
            pass

        return result

    def categories(self, query):
        text = self._request(**query)
        root = etree.fromstring(text)
        xpath = etree.XPathEvaluator(root)
        xpath.register_namespace('aws', 'http://awis.amazonaws.com/doc/2005-07-11')

        res = xpath('//aws:AbsolutePath')

        result = []

        for r in res:
            result.append(r.text)

        return result
