from django.db.models import Sum, Max, Value, Avg
from django.db.models.functions import Coalesce
from .models import Item
from geopy.geocoders import Nominatim
from django.core.cache import cache


geolocator = Nominatim(user_agent="trending-map")


def calculate_cart_total(cart, movies_in_cart):
    total = 0
    for movie in movies_in_cart:
        quantity = cart[str(movie.id)]
        total += movie.price * int(quantity)
    return total

def building_trending_geojson():
    qs = (
        Item.objects
        .select_related('order__user__profile', 'movie')
        .exclude(order__user__profile__country='')
        .values(
            'order__user__profile__country',
            'order__user__profile__region',
            'movie_id', 'movie__name'
        )
        .annotate(total_qty=Coalesce(Sum('quantity'), Value(0)))
        .annotate(last_dt=Max('order__date'))
    )

    region_to_rows = {}
    for row in qs:
        key = (
            row['order__user__profile__country'],
            row['order__user__profile__region'],
        )
        region_to_rows.setdefault(key, []).append(row)
    
    from accounts.models import Profile
    features = []
    for (country, region), rows in region_to_rows.items():
        rows.sort(key=lambda r: (-r['total_qty'], -(r['last_dt'].timestamp() if r['last_dt'] else 0), r['movie__name']))
        top = rows[0]
        region_str = ", ".join([p for p in [region, country] if p])

        coords = get_coords(region_str)
        if not coords:
            continue

        lat, lon = coords
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "region": region_str,
                "topMovie": top['movie__name'],
                "count": int(top['total_qty']),
            },
        })
    
    return {"type": "FeatureCollection", "features": features}

def get_coords(region: str):
    if not region:
        return None
    
    cached = cache.get(region)
    if cached:
        return cached
    try:
        location = geolocator.geocode(region)
        if location:
            coords = (location.latitude, location.longitude)
            cache.set(region, coords, timeout=None)
            return coords
    except Exception:
        pass
    return None