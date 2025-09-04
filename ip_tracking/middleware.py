from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
import requests

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Access denied")
        path = request.path
        country, city = self.get_geolocation(ip_address)
        RequestLog.objects.create(ip_address=ip_address, path=path, country=country, city=city)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_geolocation(self, ip_address):
        cache_key = f'geolocation_{ip_address}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data['country'], cached_data['city']

        try:
            response = requests.get(f'https://ipinfo.io/{ip_address}/json')
            data = response.json()
            country = data.get('country')
            city = data.get('city')
            cache.set(cache_key, {'country': country, 'city': city}, 86400)  # 24 hours
            return country, city
        except:
            return None, None