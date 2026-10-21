import eel


# JavaScript から関数を呼び出すデコレータです。
@eel.expose
def get_calculation_result_text(ev: int, pokemon_num: int) -> str:
    """計算を行い、結果のテキストを返します。"""

    try:
        x, y = calculate(ev, pokemon_num)
        return ' '.join(
            [
                f'Give power-item each of them <span class="emphasize">{x} times</span> in flock battle.',  # noqa: E501
                f'Then kick <span class="emphasize">{y} pokemons\'</span> ass.',
            ]
        )
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
    x, y = divmod(ev, ev_per_round)
    return (x, y)


def main() -> None:
    """アプリを起動します。"""

    # ウェブコンテンツの含まれるディレクトリを指定します。
    eel.init('web')

    # 最初に表示する html です。
    eel.start('index.html', size=(650, 500))


if __name__ == '__main__':
    main()
