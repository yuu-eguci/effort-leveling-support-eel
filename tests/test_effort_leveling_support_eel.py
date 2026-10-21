import importlib
import sys

import eel
import pytest


@pytest.fixture
def app(monkeypatch):
    """eel の起動処理を記録用の関数に差し替えてからモジュールを読み込みます。"""

    calls = []
    monkeypatch.setattr(eel, 'expose', lambda function: function)
    monkeypatch.setattr(
        eel, 'init', lambda *args, **kwargs: calls.append(('init', args, kwargs))
    )
    monkeypatch.setattr(
        eel, 'start', lambda *args, **kwargs: calls.append(('start', args, kwargs))
    )
    monkeypatch.delenv('EEL_SERVER_MODE', raising=False)
    monkeypatch.delenv('EEL_HOST', raising=False)
    sys.modules.pop('effort_leveling_support_eel', None)
    module = importlib.import_module('effort_leveling_support_eel')
    module.calls = calls
    return module


def test_import_does_not_start_app(app):
    assert app.calls == []


def test_main_starts_app(app):
    app.main()
    assert app.calls == [
        ('init', ('web',), {}),
        ('start', ('index.html',), {'size': (650, 500)}),
    ]


def test_main_starts_server_only_in_server_mode(app, monkeypatch):
    monkeypatch.setenv('EEL_SERVER_MODE', '1')
    app.main()
    name, args, kwargs = app.calls[-1]
    assert (name, args) == ('start', ('index.html',))
    assert kwargs['mode'] is None
    # 明示しない限り、ほかのマシンからは繋がらないようにします。
    assert kwargs['host'] == 'localhost'
    assert 'all_interfaces' not in kwargs
    # タブを閉じてもサーバが終了しないよう、何もしない callback を渡します。
    assert kwargs['close_callback']('index.html', []) is None


@pytest.mark.parametrize(
    ('ev', 'num', 'expected'),
    [
        (252, 1, (10, 2)),
        (25, 1, (1, 0)),
        (24, 1, (0, 24)),
        (252, 3, (7, 7)),
        (252, 6, (5, 2)),
        (10000, 1, (400, 0)),
        (2520, 1, (100, 20)),
    ],
)
def test_calculate(app, ev, num, expected):
    assert app.calculate(ev, num) == expected


@pytest.mark.parametrize(
    ('ev', 'num'),
    [
        (0, 1),
        (252, 0),
        (-1, 1),
        (2.5, 1),
        (252, 1.5),
        (252.0, 1),
        (float('nan'), 1),
        (True, 1),
        ('252', 1),
        (None, 1),
    ],
)
def test_calculate_rejects_invalid_values(app, ev, num):
    with pytest.raises(ValueError):
        app.calculate(ev, num)


def test_get_calculation_result_text(app):
    text = app.get_calculation_result_text(252, 1)
    assert '<span class="emphasize">10 times</span>' in text
    assert '<span class="emphasize">2 pokemons\'</span>' in text


@pytest.mark.parametrize(('ev', 'num'), [(0, 1), (2.5, 1), (None, 1)])
def test_get_calculation_result_text_with_invalid_values(app, ev, num):
    assert app.get_calculation_result_text(ev, num) == 'Invalid values were input.'


def test_main_uses_eel_host_in_server_mode(app, monkeypatch):
    monkeypatch.setenv('EEL_SERVER_MODE', '1')
    monkeypatch.setenv('EEL_HOST', '0.0.0.0')
    app.main()
    assert app.calls[-1][2]['host'] == '0.0.0.0'
