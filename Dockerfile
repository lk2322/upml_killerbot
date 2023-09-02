FROM python:3.10.11-slim as builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir=/app/wheels -r ./requirements.txt


FROM python:3.10.11-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache --no-cache-dir /wheels/*

COPY /src ./src

CMD ["python", "-m", "src"]
