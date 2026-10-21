effort-leveling-support-eel
===

This app supports pokemon effort leveling.

- Docker: 対応!
- Python: 3.14!
- Linter: Ruff!
- Test: pytest!
- Eel: 0.18!

## パッと実行してみたい

```bash
docker compose up --build
```

ブラウザで http://localhost:8000 を開く。

Docker なしで動かすならこっち。

```bash
pipenv install
pipenv run python effort_leveling_support_eel.py
```

Chrome または Chromium のウィンドウでアプリが開く。
どっちもなければ既定のブラウザで開く。

`EEL_SERVER_MODE=1` でブラウザを開かずにサーバだけ起動。
Docker はこのモードを使う。

## 開発

```bash
pipenv install --dev
pipenv run ruff check .
pipenv run ruff format --check .
pipenv run pytest
```

GitHub Actions は master への push と pull request ごとに lint と test を実行。

## About

Remake app of https://github.com/yuu-eguci/effort-leveling-support

![1](https://user-images.githubusercontent.com/28250432/83946778-de13a900-a84d-11ea-9869-4e699a34ee53.png)

![2](https://user-images.githubusercontent.com/28250432/83946780-df44d600-a84d-11ea-8056-4921fd46d834.png)

![3](https://user-images.githubusercontent.com/28250432/83946781-e10e9980-a84d-11ea-81f7-8f24cfb0c954.png)
