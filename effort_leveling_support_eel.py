import eel


# JavaScript から関数を呼び出すデコレータです。
@eel.expose
def calculate():
    print('hello eel')


# ウェブコンテンツの含まれるディレクトリを指定します。
eel.init('web')

# 最初に表示する html です。
eel.start('index.html')
