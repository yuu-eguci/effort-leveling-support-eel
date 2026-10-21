FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY effort_leveling_support_eel.py ./
COPY web ./web

ENV EEL_SERVER_MODE=1
ENV EEL_HOST=0.0.0.0
EXPOSE 8000

RUN useradd --create-home app
USER app

CMD ["python", "effort_leveling_support_eel.py"]
