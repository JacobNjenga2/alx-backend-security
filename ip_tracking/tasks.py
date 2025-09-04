from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import models
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    # Check for IPs with more than 100 requests in the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    ip_counts = RequestLog.objects.filter(timestamp__gte=one_hour_ago).values('ip_address').annotate(count=models.Count('id')).filter(count__gt=100)

    for ip_count in ip_counts:
        ip = ip_count['ip_address']
        count = ip_count['count']
        SuspiciousIP.objects.get_or_create(ip_address=ip, defaults={'reason': f'Exceeded {count} requests in the last hour'})

    # Check for IPs accessing sensitive paths
    sensitive_paths = ['/admin', '/login']
    sensitive_logs = RequestLog.objects.filter(path__in=sensitive_paths, timestamp__gte=one_hour_ago)

    for log in sensitive_logs:
        SuspiciousIP.objects.get_or_create(ip_address=log.ip_address, defaults={'reason': f'Accessed sensitive path: {log.path}'})