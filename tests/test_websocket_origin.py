import base64
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

import effort_leveling_support_eel as app

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    ('origin', 'host', 'expected'),
    [
        # ブラウザ以外のクライアントは Origin を送らないので、そのまま通します。
        (None, 'localhost:8000', True),
        ('http://localhost:8000', 'localhost:8000', True),
        ('http://127.0.0.1:8000', '127.0.0.1:8000', True),
        ('http://LOCALHOST:8000', 'localhost:8000', True),
        ('http://evil.example', 'localhost:8000', False),
        ('http://localhost:8001', 'localhost:8000', False),
        ('null', 'localhost:8000', False),
    ],
)
def test_is_allowed_websocket_origin(origin, host, expected):
    assert app.is_allowed_websocket_origin(origin, host) is expected


def _call_via_websocket(origin):
    """/eel へ接続して計算関数を呼び、返ってきたデータを返します。"""

    key = base64.b64encode(os.urandom(16)).decode()
    request = (
        'GET /eel?page=test HTTP/1.1\r\n'
        'Host: localhost:8000\r\n'
        'Upgrade: websocket\r\n'
        'Connection: Upgrade\r\n'
        f'Sec-WebSocket-Key: {key}\r\n'
        'Sec-WebSocket-Version: 13\r\n'
        f'Origin: {origin}\r\n\r\n'
    )
    call = json.dumps(
        {'call': 1, 'name': 'get_calculation_result_text', 'args': [252, 1]}
    ).encode()
    mask = os.urandom(4)
    frame = bytes([0x81, 0x80 | len(call)]) + mask
    frame += bytes(b ^ mask[i % 4] for i, b in enumerate(call))

    received = b''
    with socket.create_connection(('127.0.0.1', 8000), timeout=3) as s:
        s.sendall(request.encode())
        try:
            while b'\r\n\r\n' not in received:
                received += s.recv(1024)
            s.sendall(frame)
            while b'"return"' not in received:
                chunk = s.recv(1024)
                if not chunk:
                    break
                received += chunk
        except OSError:
            pass
    return received


@pytest.fixture
def server():
    # 起動済みの別プロセスに繋いでしまわないよう、
    # ポートが空いていることを先に確かめます。
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', 8000)) == 0:
            pytest.fail(
                'ポート 8000 が使用中です。アプリを止めてから実行してください。'
            )

    env = {**os.environ, 'EEL_SERVER_MODE': '1'}
    script = ROOT / 'effort_leveling_support_eel.py'
    process = subprocess.Popen([sys.executable, script], cwd=ROOT, env=env)
    try:
        for _ in range(50):
            try:
                socket.create_connection(('127.0.0.1', 8000), timeout=1).close()
                break
            except OSError:
                time.sleep(0.1)
        yield
    finally:
        process.terminate()
        process.wait(timeout=5)


def test_server_rejects_cross_origin_websocket(server):
    assert b'"return": 1' not in _call_via_websocket('http://evil.example')
    assert b'"return": 1' in _call_via_websocket('http://localhost:8000')
