import datetime
import time
import os
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Dizin yolu ve URL bilgisi
Grundpfad = r'C:\Users\isaci\OneDrive\Masaüstü\Japan'
URL = 'https://www.inflation.eu/en/inflation-rates/LAND/historic-inflation/cpi-inflation-LAND-JAHR.aspx'

# Dizin mevcut değilse oluştur
try:
    os.makedirs(Grundpfad, exist_ok=True)
except OSError as e:
    print(f"Error creating directory: {e}")
    exit(1)

# Unix zamanını al ve bugünkü tarih olarak biçimlendir
UnixTime = int(time.time())
currentdate = datetime.datetime.fromtimestamp(UnixTime).strftime('%Y-%m-%d')

############ Değişkenler ##########
Countries = ['turkey']
Jahre = list(range(1956, 2024))

data_list = []  # Verileri liste halinde toplamak için boş bir liste

for Country in Countries:
    for Jahr in Jahre:
        neue_URL = URL.replace("JAHR", str(Jahr)).replace("LAND", Country)
        response = requests.get(neue_URL)
        if response.status_code != 200:
            print(f"Error fetching data for {Country} in {Jahr}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Tablonun bulunduğu bölümü ayır
        soup2 = str(soup)
        ind1 = soup2.find('<table cellpadding="2" cellspacing="0" style="width:100%;border:1px solid #CCCCCC;">')
        ind2 = soup2.find('<h2 style="margin:16px 0px 4px 0px;">Historic CPI inflation ')
        a = soup2[ind1:ind2]

        # Tabloyu parse et
        soup3 = BeautifulSoup(a, "html.parser")

        # Tablo içeriğini çıkarma
        Month = 1
        for tr in soup3.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) > 4:  # Geçerli bir veri kontrolü
                data_list.append({
                    'Year': Jahr,
                    'Month': Month,
                    'Day': 1,
                    'Country': Country,
                    'Inflation-Rate': tds[4].text.strip().replace('%', '')
                })
                Month += 1

# Listeyi DataFrame'e dönüştürme
df = pd.DataFrame(data_list)

# Verileri CSV dosyasına kaydetme
Datenpfad = os.path.join(Grundpfad, f"{currentdate}_Inflationsdaten.csv")
df.to_csv(Datenpfad, index=False)

# Veriyi tekrar okuma ve düzenleme
df = pd.read_csv(Datenpfad)

# Zaman serisi formatı oluşturma
df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
df.set_index('Date', inplace=True)

###### Ülkeye göre grafik çizme
Country = Countries[0]
fig, ax1 = plt.subplots(figsize=(20, 4.5))
ax1.grid(color='black', linestyle='--', linewidth=0.05)
ax1.set_title(f'Monthly Inflation-Rate in {Country}')
ax1.set_xlabel('Date')
ax1.set_ylabel('Inflation Rate')
ax1.plot(df[df["Country"] == Country]['Inflation-Rate'], label='Inflation Rate')
fig.tight_layout()
plt.savefig(os.path.join(Grundpfad, f"InflationRate-Month_{Country}.png"), bbox_inches='tight')

###### Yıllık veri toplama
df_year_list = []

for Country in Countries:
    for Jahr in Jahre:
        new_df = df.loc[(df['Year'] == Jahr) & (df['Country'] == Country)]
        if not new_df.empty:
            df_year_list.append({
                'Year': Jahr,
                'Country': Country,
                'InflationRateYear': new_df['Inflation-Rate'].astype(float).mean()
            })

df_year = pd.DataFrame(df_year_list)

# Yıllık verileri CSV'ye kaydetme
Datenpfad = os.path.join(Grundpfad, f"{currentdate}_Inflationsdaten_Year.csv")
df_year.to_csv(Datenpfad, index=False)

###### Yıllık veri grafiği çizme
fig, ax1 = plt.subplots(figsize=(20, 4.5))
ax1.grid(color='black', linestyle='--', linewidth=0.1)
ax1.set_title(f'Yearly Inflation-Rate in {Country}')
ax1.set_xlabel('Year')
ax1.set_ylabel('Inflation Rate')
ax1.plot(df_year[df_year["Country"] == Country]['Year'], df_year[df_year["Country"] == Country]['InflationRateYear'],
         label='Inflation Rate')
fig.tight_layout()
plt.savefig(os.path.join(Grundpfad, f"InflationRate-Year_{Country}.png"), bbox_inches='tight')

