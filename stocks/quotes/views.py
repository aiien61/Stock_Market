import os
import json

import requests
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = 'https://api.iex.cloud/v1/data/core/quote'


def home(request):
    if request.method == "POST":
        try:
            symbol = request.POST["ticker"]
            parameters = {
                'token': os.environ.get("API_KEY")
            }
            target_url = os.path.join(ENDPOINT, symbol)
            response = requests.get(url=target_url, params=parameters)
            
            response.raise_for_status()
            
            # response structure often changes e.g. list or dict
            data = response.json()[0]
            
            return render(request, 'index.html', {'data': data})
        
        except KeyError as e:
            ticker_message = str(e)
    else:
        ticker_message = "Enter a Ticker Symbol Above..."
    
    return render(request, 'index.html', {'ticker': ticker_message})


def about(request):
    return render(request, "about.html", {})