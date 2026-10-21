import importlib
import sys

import eel
import pytest


@pytest.fixture
def app(monkeypatch):
    """eel の起動処理を記録用の関数に差し替えてからモジュールを読み込みます。"""

    calls = []
    monkeypatch.setattr(eel, 'expose', lambda function: function)
    monkeypatch.setattr(eel, 'init', lambda *args, **kwargs: calls.append('init'))
    monkeypatch.setattr(eel, 'start', lambda *args, **kwargs: calls.append('start'))
    sys.modules.pop('effort_leveling_support_eel', None)
    module = importlib.import_module('effort_leveling_support_eel')
    module.calls = calls
    return module


def test_import_does_not_start_app(app):
    assert app.calls == []


def test_main_starts_app(app):
    app.main()
    assert app.calls == ['init', 'start']


@pytest.mark.parametrize(
    ('ev', 'num', 'expected'),
    [
        (252, 1, (10, 2)),
        (25, 1, (1, 0)),
        (24, 1, (0, 24)),
        (252, 3, (7, 7)),
        (252, 6, (5, 2)),
    ],
)
def test_calculate(app, ev, num, expected):
    assert app.calculate(ev, num) == expected


@pytest.mark.parametrize(('ev', 'num'), [(0, 1), (252, 0), (-1, 1)])
def test_calculate_rejects_non_positive_values(app, ev, num):
    with pytest.raises(ValueError):
        app.calculate(ev, num)


def test_get_calculation_result_text(app):
    text = app.get_calculation_result_text(252, 1)
    assert '<span class="emphasize">10 times</span>' in text
    assert '<span class="emphasize">2 pokemons\'</span>' in text


def test_get_calculation_result_text_with_invalid_values(app):
    assert app.get_calculation_result_text(0, 1) == 'Invalid values were input.'
