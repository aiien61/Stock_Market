import os
import json

import requests
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()


def home(request):
    parameters = {
        'token': os.environ.get("API_KEY")
    }
    response = requests.get(url='https://api.iex.cloud/v1/data/core/quote/aapl', params=parameters)
    try:
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        data = "Error..."
    
    return render(request, 'index.html', {'data': data})


def about(request):
    return render(request, "about.html", {})