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
        # capture request body
        body = req.data
        sent['body'] = json.loads(body.decode('utf-8'))
        return DummyResponse(204)

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    from suyo import init
    status, body = init()
    assert status == 204
    assert body is None or isinstance(body, str)
    assert 'embeds' in sent['body']
    assert sent['body']['embeds'][0]['title'] == 'Test Embed - Suyo'
