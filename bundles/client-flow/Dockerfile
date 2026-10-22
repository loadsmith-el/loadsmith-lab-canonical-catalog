# Hook image for the client-flow bundle: Python + pyarrow to open the Parquet objects
# delivered to the S3 simulator and assert keys, rows and types. Nothing needed on the host beyond Docker.
FROM python:3.12-slim

RUN pip install --no-cache-dir pyarrow

COPY scripts/ /scripts/
RUN chmod +x /scripts/*
