FROM python:3.11.5-slim-bookworm as base
FROM base as builder

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY pymdp.py /app/

FROM base

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/python", "pymdp.py"]
CMD ["$VAR"]
