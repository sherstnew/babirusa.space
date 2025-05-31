FROM python:3.9-slim

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ../backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mitm.py .

CMD ["mitmdump", "-s", "mitm.py", "-p", "8080", "--set", "keep_host_header=true"]

EXPOSE 8080

# mitmdump -s mitm.py -p 8080 --set keep_host_header=true