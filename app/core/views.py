"""
View for home page.
"""

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
