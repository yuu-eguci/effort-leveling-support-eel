import eel


# JavaScript から関数を呼び出すデコレータです。
@eel.expose
def get_calculation_result_text(ev: int, pokemon_num: int) -> str:
    print(repr(ev), repr(pokemon_num))
    return 'test text!!'


# ウェブコンテンツの含まれるディレクトリを指定します。
eel.init('web')

# 最初に表示する html です。
eel.start('index.html')
