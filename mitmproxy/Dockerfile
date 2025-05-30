FROM python:3.9

RUN apt-get update && apt-get install -y mitmproxy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY mitm.py .

CMD ["mitmdump", "-s", "mitm.py", "-p", "8080", "--set", "keep_host_header=true"]

EXPOSE 8080

# mitmdump -s mitm.py -p 8080 --set keep_host_header=true