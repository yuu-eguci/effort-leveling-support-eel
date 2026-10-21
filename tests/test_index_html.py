from html.parser import HTMLParser
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent / 'web'


class _Collector(HTMLParser):
    """index.html から参照しているファイルと、id 付き要素を集めます。"""

    def __init__(self):
        super().__init__()
        self.assets = []
        self.elements = {}
        self._form_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self._form_depth += 1
        if tag == 'script' and 'src' in attrs:
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.assets.append(attrs['href'])
        if 'id' in attrs:
            attrs['in_form'] = self._form_depth > 0
            self.elements[attrs['id']] = attrs

    def handle_endtag(self, tag):
        if tag == 'form':
            self._form_depth -= 1


def _collect():
    collector = _Collector()
    collector.feed((WEB_DIR / 'index.html').read_text(encoding='utf-8'))
    return collector


def test_assets_are_bundled_locally():
    # eel.js は eel が配信するので、それ以外は web 配下に同梱されている必要があります。
    assets = [a for a in _collect().assets if a != '/eel.js']
    assert assets
    for asset in assets:
        assert '//' not in asset, asset
        assert (WEB_DIR / asset).is_file(), asset


def test_enter_key_submits_calculation():
    elements = _collect().elements
    for element_id in ('input_ev', 'input_pokemon_num', 'b'):
        assert elements[element_id]['in_form'], element_id
    assert elements['b']['type'] == 'submit'


def test_inputs_accept_only_positive_integers():
    elements = _collect().elements
    for element_id in ('input_ev', 'input_pokemon_num'):
        assert elements[element_id]['min'] == '1', element_id
        assert elements[element_id]['step'] == '1', element_id
