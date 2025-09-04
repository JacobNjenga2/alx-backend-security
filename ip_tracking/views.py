from django.shortcuts import render
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required

@ratelimit(key='ip', rate='5/m', method='GET')
def login_view(request):
    if request.method == 'POST':
        # Simulate login logic
        return HttpResponse("Login successful")
    return render(request, 'login.html')

@login_required
@ratelimit(key='user', rate='10/m', method='GET')
def dashboard_view(request):
    return HttpResponse("Dashboard")
