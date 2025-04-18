FROM python:3.11-slim-bookworm AS builder

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY src/pymdp/pymdp.py /app/

FROM gcr.io/distroless/python3-debian12

LABEL description="get mdpr image urls"

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages/

WORKDIR /app

ENTRYPOINT ["python", "pymdp.py"]
CMD ["$VAR"]
