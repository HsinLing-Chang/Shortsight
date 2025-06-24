FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl

COPY . .


ARG MAXMIND_LICENSE_KEY

RUN mkdir -p /data && \
    curl -L "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz" \
    -o /tmp/geo.tar.gz && \
    tar -xzf /tmp/geo.tar.gz -C /data --strip-components=1 --wildcards '*/GeoLite2-City.mmdb' && \
    rm /tmp/geo.tar.gz 

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
