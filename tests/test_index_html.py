from html.parser import HTMLParser
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent / 'web'


class _Collector(HTMLParser):
    """index.html から参照しているファイルと、id 付き要素を集めます。"""

    def __init__(self):
        super().__init__()
        self.assets = []
        self.elements = {}
        self.labels = []
        self.html_attrs = {}
        self.meta_charsets = []
        self.tags = []
        self._form_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'form':
            self._form_depth += 1
        if tag == 'html':
            self.html_attrs = attrs
        if tag == 'meta' and 'charset' in attrs:
            self.meta_charsets.append(attrs['charset'])
        if tag == 'label':
            self.labels.append(attrs)
        if tag == 'script' and 'src' in attrs:
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.assets.append(attrs['href'])
        if 'id' in attrs:
            attrs['tag'] = tag
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


def test_labels_point_to_inputs():
    collector = _collect()
    assert collector.labels
    for label in collector.labels:
        assert collector.elements[label['for']]['type'] == 'number', label


def test_document_declares_language_and_charset():
    collector = _collect()
    assert collector.html_attrs.get('lang') == 'en'
    assert [c.lower() for c in collector.meta_charsets] == ['utf-8']


def test_tabs_are_owned_by_tablist():
    tags = _collect().tags
    nav = [a for t, a in tags if t == 'ul' and 'nav-tabs' in a.get('class', '')]
    assert [a.get('role') for a in nav] == ['tablist']
    items = [a for t, a in tags if t == 'li' and 'nav-item' in a.get('class', '')]
    assert items
    assert all(a.get('role') == 'presentation' for a in items)


def test_tabpanels_are_not_forms():
    elements = _collect().elements
    for panel_id in ('nav-1', 'nav-2'):
        assert elements[panel_id]['tag'] == 'div', panel_id


def test_page_has_main_landmark():
    assert [t for t, _ in _collect().tags].count('main') == 1
