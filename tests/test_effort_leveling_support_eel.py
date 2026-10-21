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
    monkeypatch.setattr(eel.chrome, 'find_path', lambda: '/path/to/chrome')
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


FLOCK_10 = 'Give power-item each of them <span class="emphasize">10 times</span> in flock battle.'  # noqa: E501
FLOCK_1 = 'Give power-item each of them <span class="emphasize">1 time</span> in flock battle.'  # noqa: E501


@pytest.mark.parametrize(
    ('ev', 'num', 'expected'),
    [
        (
            252,
            1,
            f'{FLOCK_10} Then kick <span class="emphasize">2 pokemons\'</span> ass.',
        ),
        (
            26,
            1,
            f'{FLOCK_1} Then kick <span class="emphasize">1 pokemon\'s</span> ass.',
        ),
        (25, 1, FLOCK_1),
        (24, 1, 'Kick <span class="emphasize">24 pokemons\'</span> ass.'),
    ],
)
def test_get_calculation_result_text(app, ev, num, expected):
    assert app.get_calculation_result_text(ev, num) == expected


@pytest.mark.parametrize(('ev', 'num'), [(0, 1), (2.5, 1), (None, 1)])
def test_get_calculation_result_text_with_invalid_values(app, ev, num):
    assert app.get_calculation_result_text(ev, num) == 'Invalid values were input.'


def test_main_uses_eel_host_in_server_mode(app, monkeypatch):
    monkeypatch.setenv('EEL_SERVER_MODE', '1')
    monkeypatch.setenv('EEL_HOST', '0.0.0.0')
    app.main()
    assert app.calls[-1][2]['host'] == '0.0.0.0'


def test_main_falls_back_to_default_browser_without_chrome(app, monkeypatch, capsys):
    monkeypatch.setattr(eel.chrome, 'find_path', lambda: None)
    app.main()
    assert app.calls[-1] == ('start', ('index.html',), {'mode': 'default'})
    # 既定のブラウザも開けない環境向けに、開く URL を表示します。
    assert 'http://localhost:8000/index.html' in capsys.readouterr().out
