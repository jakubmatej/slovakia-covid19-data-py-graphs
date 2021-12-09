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

  # Reverse order of rows in case of different source format (e.g. commit 2021-12-06)
  raw = raw.iloc[::-1]

  release_date = raw['Date'].values[-1]

  # --- Set Data range -> start from date
  # row_no = raw.loc[raw['Date'] == '2021-08-01'].first_valid_index()
  # raw = raw.drop(raw.index[:row_no-1])

  # --- Convert date to month no.
  raw['Date'] = raw['Date'].apply(pd.to_datetime)
  raw['Date'] = raw['Date'].dt.month

  # --- Create pivot table
  p = pd.pivot_table(raw, index=['Date', 'age_group'] , columns=['Vaccinated'], values='Admissions', aggfunc=np.sum, fill_value=0)

  # --- Split Data into categories

  # Remove rows with zero
  # When using the average function, if weights are given, they can not add up to 0 because that leads to division by 0
  wa_unvax = p.loc[~(p[False] == 0)]
  # Applay reset_index to avoid MultiIndex
  wa_unvax = wa_unvax.reset_index(1)
  wa_unvax = wa_unvax.rename(columns={False:'unvax', True:'vax'})
  wa_unvax['age_group'] = wa_unvax['age_group'].astype(np.int8) # Convert age_group values to intiger

  wa_vax = p.loc[~(p[True] == 0)]
  wa_vax = wa_vax.reset_index(1)
  wa_vax = wa_vax.rename(columns={False:'unvax', True:'vax'})
  wa_vax['age_group'] = wa_vax['age_group'].astype(np.int8)

  # --- Calculate Average by weights for each category
  # https://stackoverflow.com/questions/31521027/groupby-weighted-average-and-sum-in-pandas-dataframe
  wa_unvax = wa_unvax.groupby(wa_unvax.index).apply(lambda x: np.average(x.age_group, weights=x.unvax))
  wa_unvax = wa_unvax.rename('unvaccinated') # Renamed for proper graph legend
  wa_unvax = wa_unvax.to_frame()

  wa_vax = wa_vax.groupby(wa_vax.index).apply(lambda x: np.average(x.age_group, weights=x.vax))
  wa_vax = wa_vax.rename('vaccinated')
  wa_vax = wa_vax.to_frame()

  # --- Result Data as new DataFrame
  result = pd.DataFrame.join(wa_unvax, wa_vax, on='Date')
  # print(result)
  # print(type(result))

  # --- Plot Data
  fig = result.plot.line(title='Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average', figsize=(10,8), color = ['#ffa500', '#069af3'], marker='o')

  fig.set_xlabel("Months 2021")
  fig.set_ylabel("Age")

  fig.grid(visible=True, which='both')
  fig.minorticks_on()

  fig.grid(which='major', color='#a9a9a9', linewidth=1)
  fig.grid(which='minor', color='#e0e0e0', linewidth=0.6)
  fig.tick_params(which='minor', color='#e0e0e0')
  fig.xaxis.set_major_locator(MultipleLocator(1))
  fig.xaxis.set_minor_locator(MultipleLocator(1))
  fig.yaxis.set_major_locator(MultipleLocator(10))
  fig.yaxis.set_minor_locator(MultipleLocator(1))

  # Create marker labels
  for idx, row in result.iterrows():
    fig.annotate(row['unvaccinated'].round(2), xy=(idx, row['unvaccinated']*1.01), fontsize=8, ha='center')
    fig.annotate(row['vaccinated'].round(2), xy=(idx, row['vaccinated']*1.01), fontsize=8, ha='center')

  # Note inside plot area - foot note
  fig.annotate('Source: github.com/Institut-Zdravotnych-Analyz/covid19-data (' + str(release_date) + ')',
                xy = (1.0, -0.1),
                xycoords='axes fraction',
                ha='right',
                va='center',
                fontsize=8)

  # Set x, y Axis range
  # plt.xlim(datetime.datetime(2021,8,1), datetime.datetime(2021,12,31))
  plt.ylim(40, 80)
  plt.savefig('./res/Hospitalizations/' + str(release_date) + '_Ventilated_Admissions_Age_WAverage_by_Vaccine_Monthly.png')
  plt.show()