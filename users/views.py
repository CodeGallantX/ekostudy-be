from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def profile(request):
    return HttpResponse('<h1>Hello, welcome to my profile!</h1>')