from math import asin, cos, radians, sin, sqrt


def validate_geofence(site_lat: float, site_lng: float, staff_lat: float, staff_lng: float, radius_m: float = 100.0) -> tuple[bool, float]:
    """Return (within_radius, distance_meters) using the Haversine formula."""
    earth_radius_m = 6371000.0
    phi1, phi2 = radians(site_lat), radians(staff_lat)
    dphi = radians(staff_lat - site_lat)
    dlambda = radians(staff_lng - site_lng)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    distance = 2 * earth_radius_m * asin(sqrt(min(1.0, a)))
    return distance <= radius_m, round(distance, 2)
