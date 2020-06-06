import eel


# JavaScript から関数を呼び出すデコレータです。
@eel.expose
def get_calculation_result_text(ev: int, pokemon_num: int) -> str:
    """計算を行い、結果のテキストを返します。"""

    try:
        x, y = calculate(ev, pokemon_num)
        return ' '.join([
            f'Give power-item each of them <span class="emphasize">{x} times</span> in flock battle.',
            f'Then kick <span class="emphasize">{y} pokemons\'</span> ass.'
        ])
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
    """

    if ev <= 0 or num <= 0:
        raise ValueError(f'Invalid value, ev:{ev}, num:{num}')

    for x in range(100):
        _ = (25 * x) + (x * 5 * (num - 1))
        if _ > ev:
            x -= 1
            y = ev - ((25 * x) + (x * 5 * (num - 1)))
            return (x, y)


# ウェブコンテンツの含まれるディレクトリを指定します。
eel.init('web')

# 最初に表示する html です。
eel.start('index.html')
