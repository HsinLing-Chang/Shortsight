from pathlib import Path

import geoip2.database
import geoip2.errors
MMDB_PATH = Path("data/GeoLite2-City.mmdb")
reader = geoip2.database.Reader(str(MMDB_PATH))


def lookup_ip(ip_address: str):
    try:
        response = reader.city(ip_address)
        return {
            "ip": ip_address,
            "country": response.country.name if response.country.name else None,
            "city": response.city.name if response.city.name else None,
            "latitude": response.location.latitude if response.location.latitude else None,
            "longitude": response.location.longitude if response.location.longitude else None
        }
    except geoip2.errors.AddressNotFoundError:
        return None
