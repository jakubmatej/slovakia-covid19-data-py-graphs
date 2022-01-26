import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

def is_uri_ok(uri_string, print_error=True):
  try:
    r = requests.head(uri_string)
    r.raise_for_status()
    return True
  except requests.exceptions.RequestException as error:
    if print_error:
      print(error)
    pass
  return False

uri = 'https://raw.githubusercontent.com/Institut-Zdravotnych-Analyz/covid19-data/main/Hospitals/OpenData_Slovakia_Covid_Hospital_UPV_AdmissionDischarge.csv'

if is_uri_ok(uri):
  raw = pd.read_csv(uri, sep=';', index_col=0)

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
  result['unvaccinated_7ma'] = result['unvaccinated'].rolling(7, closed='left').mean()
  result['vaccinated_7ma'] = result['vaccinated'].rolling(7, closed='left').mean()

  # --- Plot Data
  ax = result.plot.line(title='Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average & 7ma', figsize=(10,8), color = ['#FFDFA4', '#A4DBFD', '#ffa500', '#069af3'])
  plt.subplots_adjust(left=0.06, right=0.99, bottom= 0.065, top=0.96)

  ax.grid(visible=True, which='both')
  ax.minorticks_on()

  ax.grid(which='major', color='#a9a9a9', linewidth=1)
  ax.grid(which='minor', color='#e0e0e0', linewidth=0.6)
  ax.tick_params(which='minor', color='#e0e0e0')
  ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
  ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(2.5))
  # Format x tick labels
  for label in ax.get_xticklabels(which='major'):
    label.set(rotation=0, horizontalalignment='center')
  ax.set_xlabel(None)
  ax.set_ylabel("Age")
  # Set x and y axis range
  xlimoOffset = datetime.timedelta(days=7)
  ax.set_xlim(datetime.datetime(2021, 8, 1) - xlimoOffset, datetime.datetime(2022, 5, 1) + xlimoOffset)
  ax.set_ylim(0, 100)

  # Note inside plot area - foot note
  ax.annotate('Source: github.com/Institut-Zdravotnych-Analyz/covid19-data (' + str(release_date) + ')',
                xy = (1.0, -0.06),
                xycoords='axes fraction',
                ha='right',
                va='center',
                fontsize=8)

  plt.savefig('./res/Hospitalizations/Ventilated_Admissions_Age_WAverage_by_Vaccine_Daily.png')