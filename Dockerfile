# Pipfile.lock から requirements.txt を書き出すためだけのステージです。
FROM python:3.14-slim AS requirements

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv requirements --hash > requirements.txt

FROM python:3.14-slim

WORKDIR /app

COPY --from=requirements requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY effort_leveling_support_eel.py ./
COPY web ./web

ENV EEL_SERVER_MODE=1
ENV EEL_HOST=0.0.0.0
EXPOSE 8000

RUN useradd --create-home app
USER app

CMD ["python", "effort_leveling_support_eel.py"]
