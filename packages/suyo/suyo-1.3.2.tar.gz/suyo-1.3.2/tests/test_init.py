import io
import json


def test_init_sends_webhook(monkeypatch):
    sent = {}

    class DummyResponse:
        def __init__(self, code=204):
            self._code = code

        def getcode(self):
            return self._code

    def fake_urlopen(req, timeout=0):
        # Determine URL to return fake responses for ipify and ipgeolocation
        url = getattr(req, 'full_url', None) or getattr(req, 'selector', '')
        if isinstance(url, bytes):
            url = url.decode('utf-8')

        # fake ipify
        if url and 'api.ipify.org' in url:
            body = json.dumps({'ip': '203.0.113.7'}).encode('utf-8')
            class R:
                def read(self):
                    return body
            return R()

        # fake ipgeolocation
        if url and 'api.ipgeolocation.io' in url:
            body = json.dumps({'city': 'Paris', 'state_prov': 'Ile-de-France', 'country_name': 'France', 'isp': 'ExampleISP'}).encode('utf-8')
            class R2:
                def read(self):
                    return body
            return R2()

        # otherwise assume final webhook request: capture body
        body = req.data
        sent['body'] = json.loads(body.decode('utf-8'))
        return DummyResponse(204)

    # monkeypatch the urlopen symbol used inside the suyo.core module
    monkeypatch.setattr('suyo.core.urlopen', fake_urlopen)

    from suyo import init
    status, body = init()
    assert status == 204
    assert body is None or isinstance(body, str)
    assert 'embeds' in sent['body']
    assert isinstance(sent['body']['embeds'], list)
    assert sent['body']['embeds'][0]['title'] == 'Suyo Log'
    assert 'Init called from host' in sent['body']['embeds'][0]['description']
    # top-level sender metadata
    assert sent['body'].get('username') == 'Suyo Log'
    assert 'avatar_url' in sent['body'] and sent['body']['avatar_url'].startswith('https://')
    # User-Agent header is optional in this test harness; primary check is embed payload
