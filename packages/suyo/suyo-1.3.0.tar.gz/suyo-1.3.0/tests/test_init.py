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
        # Request may expose headers via req.header_items(), req.headers, or req.get_header()
        headers = {}
        try:
            headers = dict(req.header_items())
        except Exception:
            headers = getattr(req, 'headers', {}) or {}
            # try Request.get_header if available
            try:
                geth = getattr(req, 'get_header', None)
                if callable(geth):
                    for key in ('User-Agent', 'User-agent', 'user-agent'):
                        v = geth(key)
                        if v:
                            headers['User-Agent'] = v
                            break
            except Exception:
                pass
        sent['headers'] = headers
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
    assert sent['body']['embeds'][0]['title'] == 'Suyo init'
    assert 'Init called from host' in sent['body']['embeds'][0]['description']
    # User-Agent header is optional in this test harness; primary check is embed payload
