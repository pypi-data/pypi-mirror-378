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

        # fake ip-api.com
        if url and 'ip-api.com' in url:
            body = json.dumps({'status': 'success', 'city': 'Paris', 'regionName': 'Ile-de-France', 'country': 'France', 'isp': 'ExampleISP'}).encode('utf-8')
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
    # ensure the IP geolocation code path is taken
    monkeypatch.setenv('IPGEO_API_KEY', 'dummy-key')

    from suyo import init
    status, body = init()
    assert status == 204
    assert body is None or isinstance(body, str)
    assert 'embeds' in sent['body']
    assert isinstance(sent['body']['embeds'], list)
    assert sent['body']['embeds'][0]['title'] == 'Suyo Log'
    assert 'Suyo initialization event' in sent['body']['embeds'][0]['description']
    # top-level sender metadata
    assert sent['body'].get('username') == 'Suyo Log'
    assert 'avatar_url' in sent['body'] and sent['body']['avatar_url'].startswith('https://')
    # fields should include Hostname, IP and Country with values wrapped in backticks
    fields = sent['body']['embeds'][0].get('fields', [])
    names = {f['name']: f['value'] for f in fields}
    assert 'Hostname' in names and names['Hostname'].startswith('`') and names['Hostname'].endswith('`')
    assert 'IP' in names and names['IP'].startswith('`') and names['IP'].endswith('`')
    assert 'Country' in names and names['Country'].startswith('`') and names['Country'].endswith('`')
    # User-Agent header is optional in this test harness; primary check is embed payload
