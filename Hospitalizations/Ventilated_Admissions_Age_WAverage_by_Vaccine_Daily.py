import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

def is_url_ok(url_string, print_error=True):
  try:
    r = requests.head(url_string)
    r.raise_for_status()
    return True
  except requests.exceptions.RequestException as error:
    if print_error:
      print(error)
    pass
  return False

url = 'https://raw.githubusercontent.com/Institut-Zdravotnych-Analyz/covid19-data/main/Hospitals/OpenData_Slovakia_Covid_Hospital_UPV_AdmissionDischarge.csv'

if is_url_ok(url):
  raw = pd.read_csv(url, sep=';', index_col=0)

  release_date = raw['Date'].values[0]

  # --- Set Data range -> start from date
  # row_no = raw.loc[raw['Date'] == '2021-08-01'].first_valid_index()
  # raw = raw.drop(raw.index[:row_no-1])

  # --- Convert date to datetime
  raw['Date'] = raw['Date'].apply(pd.to_datetime)

  # --- Create pivot table
  p = pd.pivot_table(raw, index=['Date', 'age_group'] , columns=['Vaccinated'], values='Admissions', aggfunc=np.sum, fill_value=0)
  p = p.rename(columns={False:'unvax', True:'vax'})

  # --- Split Data into categories

  # Remove rows with zero
  # When using the average function, if weights are given, they can not add up to 0 because that leads to division by 0
  wa_unvax = p.loc[~(p['unvax'] == 0)]
  # Applay reset_index to avoid MultiIndex
  wa_unvax = wa_unvax.reset_index(1)

  wa_vax = p.loc[~(p['vax'] == 0)]
  wa_vax = wa_vax.reset_index(1)

  # --- Calculate Average by weights for each category
  # https://stackoverflow.com/questions/31521027/groupby-weighted-average-and-sum-in-pandas-dataframe
  wa_unvax = wa_unvax.groupby(wa_unvax.index).apply(lambda x: np.average(x.age_group.astype(np.int8), weights=x.unvax))
  wa_unvax = wa_unvax.rename('unvaccinated') # Renamed for proper graph legend
  wa_unvax = wa_unvax.to_frame()

  wa_vax = wa_vax.groupby(wa_vax.index).apply(lambda x: np.average(x.age_group.astype(np.int8), weights=x.vax))
  wa_vax = wa_vax.rename('vaccinated')
  wa_vax = wa_vax.to_frame()

  # --- Result Data as new DataFrame
  result = pd.DataFrame.join(wa_unvax, wa_vax, on='Date')
  # print(result)
  # print(type(result))

  # --- Add moving average
  result['unvaccinated_7ma'] = result['unvaccinated'].rolling(7).mean()
  result['vaccinated_7ma'] = result['vaccinated'].rolling(7).mean()

  # --- Plot Data
  fig = result.plot.line(title='Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average & 7ma', figsize=(10,8), color = ['#FFDFA4', '#A4DBFD', '#ffa500', '#069af3'])

  fig.set_xlabel("Date")
  fig.set_ylabel("Age")

  fig.grid(visible=True, which='both')
  fig.minorticks_on()

  fig.grid(which='major', color='#a9a9a9', linewidth=1)
  fig.grid(which='minor', color='#e0e0e0', linewidth=0.6)
  fig.tick_params(which='minor', color='#e0e0e0')
  # fig.xaxis.set_major_locator(MultipleLocator(10)) --> Custom X axis major ticks. See below
  fig.xaxis.set_minor_locator(MultipleLocator(1))
  fig.yaxis.set_major_locator(MultipleLocator(10))
  fig.yaxis.set_minor_locator(MultipleLocator(2.5))

  # Custom X axis ticks - week interval
  xticks_start = datetime.datetime(2021,8,2) # Monday
  xticks_end = datetime.datetime(2021,12,31)
  xticks_interval = 7
  xticks_range = ((xticks_end - xticks_start) / datetime.timedelta(days=xticks_interval))
  xticks_list=[]
  xticks_list.append(xticks_start)
  for i in range(0, int(xticks_range)):
      xticks_list.append(xticks_list[i] + datetime.timedelta(days=xticks_interval))
  plt.xticks(xticks_list)

  # Note inside plot area - foot note
  fig.annotate('Source: github.com/Institut-Zdravotnych-Analyz/covid19-data (' + str(release_date) + ')',
                xy = (1.0, -0.2),
                xycoords='axes fraction',
                ha='right',
                va='center',
                fontsize=8)

  # Set x, y Axis range
  plt.xlim(left=xticks_start - datetime.timedelta(days=4))
  plt.ylim(0, 100)
  plt.savefig('./res/Hospitalizations/' + str(release_date) + '_Ventilated_Admissions_Age_WAverage_by_Vaccine_Daily.png')
  plt.show()