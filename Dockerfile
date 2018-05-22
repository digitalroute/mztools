FROM python:3.6-alpine

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir .
RUN mkdir /data

WORKDIR /data
ENTRYPOINT ["/usr/local/bin/mztools"]
