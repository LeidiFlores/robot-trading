import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import re
import datetime as dt
import yfinance as yf
import time

global df_bitcoin, actual_price, tendency, media_bitcoin, decision_algorithm

def import_base_bitcoin():
  period = '7d'
  interval = '5m'
  url = 'https://finance.yahoo.com/crypto'
  ua = {'User-Agente': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}
  r = requests.get(url, headers= ua)
  
  bitcoin = yf.Ticker("BTC-USD")
  historic = bitcoin.history(period=period, interval=interval)
  
  return historic
df_bitcoin = import_base_bitcoin()
df_bitcoin

def get_tendencys():
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}
  url = 'https://coinmarketcap.com/'
  data_response = requests.get(url, headers=headers)
  
  s=BeautifulSoup(data_response.content, features='lxml')
  prices = s.findAll('div',{'class':['sc-a0353bbc-0 gDrtaY rise','sc-a0353bbc-0 gDrtaY','sc-a0353bbc-0 gDrtaY fall']})
  price=[]
  
  for item in prices:
    price.append(item.text.split())
  actual_price = float((price[0][0]).replace("$", "").replace(",", ""))
  tendencys = s.findAll('span', {'class':['sc-d55c02b-0 gUnzUB','sc-d55c02b-0 iwhBxy']})
  tendency_bitcoin =  tendencys[0]
  icon = tendency_bitcoin.find('span', {'class': ['icon-Caret-down', 'icon-Caret-up']})
  if 'icon-Caret-down' in icon['class']:
      tendency = 'a la baja'
  else:
      tendency = 'es al alza'
      
  print(f'El price actual del bitcoin es: ${actual_price} dólares')
  print(f'La tendency actual es: {tendency} ')
  
  return actual_price, tendency

actual_price, tendency = get_tendencys()

df_bitcoin_copy = df_bitcoin.copy()
df_bitcoin_copy

def clean_data():
  duplicates = df_bitcoin_copy.index.duplicated()
  num_duplicates = duplicates.sum()
  
  if num_duplicates == 0:
    df_limpio = df_bitcoin_copy
  else:
    df_limpio = df_bitcoin_copy.index.drop_duplicates(inplace=True)
  values_nan = df_limpio['Close'].isna()
  
  if values_nan is False:
    df_clean_bitcoin = df_limpio
  else:
    df_clean_bitcoin = df_limpio.fillna(df_limpio['Close'].mean())
    
  df_bitcoin_clean = df_clean_bitcoin[df_clean_bitcoin['Volume'] > 0]
  
  Q1 = df_bitcoin_clean['Close'].quantile(0.25)
  Q3 = df_bitcoin_clean['Close'].quantile(0.75)
  IQR = Q3 - Q1
  
  df_bitcoin_filter =  df_bitcoin_clean[(df_bitcoin_clean['Close']>= Q1 ) & (df_bitcoin_clean ['Close']<= Q3)]

  media_bitcoin = df_bitcoin_filter['Close'].mean().round(3)
  print(f'El price promedio del bitcoin es: ${media_bitcoin} dólares')
  return df_bitcoin_filter, media_bitcoin, df_bitcoin_clean

df_bitcoin_filter, media_bitcoin, df_bitcoin_clean = clean_data()


plt.boxplot(df_bitcoin_copy['Close'], patch_artist=True, labels=['Close'])
plt.title("Box plot price de cierre, datos sin limpiar")
plt.show()

plt.boxplot(df_bitcoin_clean['Close'], patch_artist=True, labels=['Close'])
plt.title("Box plot price de cierre, datos limpios")
plt.show()

def make_decisions():
  decision = ''
  if actual_price >= media_bitcoin and tendency == 'a la baja':
    decision = 'Vender'
  elif actual_price <= media_bitcoin and tendency == 'es al alza':
    decision = 'Comprar'
  else:
    decision = 'Espera'
  return decision
decision_algorithm = make_decisions()

def visualizacion():
  df_bitcoin['Promedio'] = media_bitcoin
  plt.rc('figure',figsize = (16,5))
  plt.title('Bitcoin')
  y = df_bitcoin['Close']
  x = df_bitcoin.index
  z = df_bitcoin['Promedio']
  graph = plt.plot(x, y)
  graph_updated = plt.plot(x,z)
  x_text = x[-200] # índice indicado para x
  y_text = y[50]   # índice indicado para y
  plt.annotate(decision_algorithm, xy=(x_text, y_text))
  plt.show()
visualizacion()

while(True):
  import_base_bitcoin()
  get_tendencys()
  clean_data()
  make_decisions()
  visualizacion()
  time.sleep(300)