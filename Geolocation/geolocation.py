from pathlib import Path

import geoip2.database
import geoip2.errors
MMDB_PATH = Path("data/GeoLite2-City.mmdb")
reader = geoip2.database.Reader(str(MMDB_PATH))


def lookup_ip(ip_address: str):
    try:
        response = reader.city(ip_address)
        return {
            "ip_address": ip_address,
            "country": response.country.name,
            "city": response.city.name,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude
        }
    except geoip2.errors.AddressNotFoundError:
        return None
