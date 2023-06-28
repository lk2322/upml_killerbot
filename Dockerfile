FROM python:3.10.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10.11-slim

WORKDIR /app
RUN apt-get update && \
    apt-get install cron -y --no-install-recommends

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

COPY src ./src
COPY .env .

RUN pip install --no-cache /wheels/*

CMD ["python", "-m", "src"]