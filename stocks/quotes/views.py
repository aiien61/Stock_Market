import os
import asyncio

from .models import Stock
from .forms import StockForm

import aiohttp
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
    if request.method == "POST":
        form = StockForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, ("Stock Has Been Added."))
    
    return redirect(show_stocks)


def parse(api_data) -> dict:
    return api_data[0]

    
async def get_stock_data(session, ticker: str):
    url = os.path.join(ENDPOINT, ticker)
    async with session.get(url=url, params=parameters, ssl=False) as response:
        response.raise_for_status()
        return await response.json()

# by asyncio, 20 times api retrieve takes around 1 seconds much better than 20 seconds with scales in sequencing way     
async def show_stocks(request):
    tasks, output = [], []

    tickers = Stock.objects.values_list("ticker", flat=True)
    async with aiohttp.ClientSession() as session:
        async for ticker in tickers:
            tasks.append(asyncio.create_task(get_stock_data(session, ticker)))
        
        result = await asyncio.gather(*tasks)
        output = [parse(data) for data in result]

    return render(request, "add_stock.html", {'tickers': tickers, 'output': output, 'time': stop_time - start_time})


def delete(request, stock_id: int):
    item = Stock.objects.get(pk=stock_id)
    item.delete()
    messages.success(request, ("Stock Has Been Deleted!"))
    return redirect(delete_stock)


def delete_stock(request):
    ticker = Stock.objects.all()
    return render(request, "delete_stock.html", {'ticker': ticker})
