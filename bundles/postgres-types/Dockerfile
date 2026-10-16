# Hook image for the postgres-types bundle: Python + pyarrow to open the Parquet
# output and assert schema + values. Nothing needed on the host beyond Docker.
FROM python:3.12-slim

RUN pip install --no-cache-dir pyarrow

COPY scripts/ /scripts/
RUN chmod +x /scripts/*
