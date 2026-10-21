import os
from urllib.parse import urlsplit

import bottle
import eel


# JavaScript から関数を呼び出すデコレータです。
@eel.expose
def get_calculation_result_text(ev: int, pokemon_num: int) -> str:
    """計算を行い、結果のテキストを返します。"""

    try:
        x, y = calculate(ev, pokemon_num)

        # 0 回の手順は省き、回数と体数は単数形と複数形を使い分けます。
        sentences = []
        if x > 0:
            times = 'time' if x == 1 else 'times'
            sentences.append(
                f'Give power-item each of them <span class="emphasize">{x} {times}</span> in flock battle.'  # noqa: E501
            )
        if y > 0:
            kick = 'Then kick' if x > 0 else 'Kick'
            pokemons = "pokemon's" if y == 1 else "pokemons'"
            sentences.append(
                f'{kick} <span class="emphasize">{y} {pokemons}</span> ass.'
            )
        return ' '.join(sentences)
    except ValueError as e:
        print(e)
        return 'Invalid values were input.'
    except Exception as e:
        print(e)
        return 'Sorry! Something went wrong!'


def calculate(ev: int, num: int) -> tuple:
    """
    振りたい努力値と、同時に処理したいポケモン数を指定すると、
    パワーアイテムを各ポケモンに順番に持たせてそれぞれ群れバトルを x 回させ
    その後パワーアイテムを持たせずに単体バトルを y 回すればいいと教えてくれます。

    Parameters
    ----------
    ev : int
        振りたい努力値数
    num : int
        同時に処理したいポケモン数

    Returns
    -------
    x : int
        上の説明参照
    y : int
        上の説明参照

    Raises
    ------
    ValueError
        ev または num が正の整数でないとき
    """

    if not all(type(v) is int and v > 0 for v in (ev, num)):
        raise ValueError(f'Invalid value, ev:{ev}, num:{num}')

    # 群れバトル 1 周 (全員が 1 回ずつパワーアイテムを持つ) で 1 体が得る努力値です。
    # 自分が持つ回で 25、ほかの num - 1 体が持つ回で 5 ずつ得ます。
    ev_per_round = 25 + 5 * (num - 1)
    return divmod(ev, ev_per_round)


def is_allowed_websocket_origin(origin: str | None, host: str) -> bool:
    """
    WebSocket の接続元が、このアプリ自身のページかどうかを返します。
    ほかのサイトのページから関数を呼ばれないよう、Origin と Host を突き合わせます。
    """

    # ブラウザ以外のクライアントは Origin を送らないので、そのまま通します。
    if origin is None:
        return True
    return urlsplit(origin).netloc.lower() == host.lower()


def is_allowed_websocket_host(host: str) -> bool:
    """
    WebSocket のリクエストの Host が、このマシン自身を指しているかどうかを返します。
    DNS rebinding では攻撃者のドメイン名が Host に入るので、ここで弾きます。
    EEL_HOST に具体的なアドレスを指定したときは、そのアドレスも許可します。
    """

    allowed = {'localhost', '127.0.0.1', '::1'}
    eel_host = os.environ.get('EEL_HOST', '').lower()
    if eel_host and eel_host != '0.0.0.0':
        allowed.add(eel_host)
    return urlsplit(f'//{host}').hostname in allowed


def reject_cross_origin_websocket() -> None:
    """/eel への別オリジンや、このマシン以外の Host 宛ての接続を切断します。"""

    request = bottle.request
    host = request.get_header('Host', '')
    if request.path == '/eel' and not (
        is_allowed_websocket_host(host)
        and is_allowed_websocket_origin(request.get_header('Origin'), host)
    ):
        # ハンドシェイクは gevent-websocket が先に済ませているので、ここで閉じます。
        websocket = request.environ.get('wsgi.websocket')
        if websocket is not None:
            websocket.close()
        bottle.abort(403, 'Cross-origin WebSocket is not allowed.')


def main() -> None:
    """アプリを起動します。"""

    # ウェブコンテンツの含まれるディレクトリを指定します。
    eel.init('web')

    # eel は bottle の既定アプリにルートを登録するので、そこへ Origin の検査を足します。
    bottle.default_app().add_hook('before_request', reject_cross_origin_websocket)

    # EEL_SERVER_MODE=1 のときはブラウザを開かず、サーバだけを起動します。
    # 待ち受けアドレスは EEL_HOST で変えられます (Docker では 0.0.0.0) 。
    # タブを閉じても終了しないよう、何もしない close_callback を渡します。
    if os.environ.get('EEL_SERVER_MODE') == '1':
        eel.start(
            'index.html',
            mode=None,
            host=os.environ.get('EEL_HOST', 'localhost'),
            close_callback=lambda page, sockets: None,
        )
        return

    # Chrome も Chromium も見つからないときは、既定のブラウザで開きます。
    if eel.chrome.find_path() is None:
        eel.start('index.html', mode='default')
        return

    # 最初に表示する html です。
    eel.start('index.html', size=(650, 500))


if __name__ == '__main__':
    main()
