FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

RUN mkdir "/app/.pytest_cache" \
    && chown 1000 "/app/.pytest_cache" \
    && touch "/app/test-report.md" \
    && chown 1000 "/app/test-report.md"

COPY pytest.ini pytest.ini
COPY tests tests

USER 1000
ENTRYPOINT ["/usr/bin/env", "pytest", "tests/tests.py"]
