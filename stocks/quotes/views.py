import os

from .models import Stock
from .forms import StockForm

import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = 'https://api.iex.cloud/v1/data/core/quote'
parameters = {'token': os.environ.get("API_KEY")}


def home(request):
    if request.method == "POST":
        try:
            symbol = request.POST["ticker"]
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


def add_stock(request):
    if request.method == "POST": # add to db
        form = StockForm(request.POST or None)

        if form.is_valid():
            form.save()
            messages.success(request, ("Stock Has Been Added."))
            return redirect(add_stock)

    else: # call db
        ticker = Stock.objects.all()

        output = []
        for symbol in ticker:
            target_url = os.path.join(ENDPOINT, str(symbol))
            response = requests.get(url=target_url, params=parameters)
            response.raise_for_status()
            output.append(response.json()[0])

        return render(request, "add_stock.html", {'ticker': ticker, 'output': output})


def delete(request, stock_id: int):
    item = Stock.objects.get(pk=stock_id)
    item.delete()
    messages.success(request, ("Stock Has Been Deleted!"))
    return redirect(delete_stock)


def delete_stock(request):
    ticker = Stock.objects.all()
    return render(request, "delete_stock.html", {'ticker': ticker})