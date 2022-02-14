import datetime
import requests
import array as arr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO
import matplotlib.ticker as mticker

uri = 'https://raw.githubusercontent.com/Institut-Zdravotnych-Analyz/covid19-data/main/Hospitals/OpenData_Slovakia_Covid_Hospital_AdmissionDischarge.csv'

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

if is_uri_ok(uri):
  raw = pd.read_csv(uri, sep=';', index_col=0) # error_bad_lines=False
  
  release_date = raw['Date'].values[0]
  
  # --- Set Data range -> start from date
  # row_no = raw.loc[raw['Date'] == '2021-08-01'].last_valid_index()
  # raw = raw.drop(raw.index[row_no:])

  # --- Convert date to datetime
  raw['Date'] = raw['Date'].apply(pd.to_datetime)

  # --- Cleansing raw
  raw['Vaccinated'] = raw['Vaccinated'].fillna(value='unknown') # Replace NaN with word unknown
  #raw['age_group'] = raw['age_group'].fillna(value=55) # Replace NaN with value 55 (average age of unvaccinated COVID-19 patient) - currently in use in Daily admissions axis only
  raw['age_group'] = raw['age_group']+5 # Middle value of age_group (e.g. age_group 0 = 0-10 age --> will be 5)
  raw = raw.loc[~(raw['Admissions'] == 0)] # Remove unnecessary zero admissions
  raw = raw.dropna(subset=['age_group']) # Additional cleansing before weighten average --> Remove NaN for proper calculation

  # --- Result - Axis 0
  p = pd.pivot_table(raw, index=['Date'] , columns=['age_group'], values='Admissions', aggfunc=np.sum, fill_value=0)
  p['total'] = p.sum(axis=1)

  df = p.apply(lambda x: (x / x.total)*100, axis=1)
  df = df.rolling(7, closed='left').mean()
  df = df.drop('total', axis=1)

  # --- Plot figure
  fig, ax = plt.subplots(figsize=(10, 8))
  plt.subplots_adjust(left=0.06, right=0.99, bottom= 0.065, top=0.96, hspace=0.06)

  # Common axis settings:
  ax.set_prop_cycle(color=['#EFE0FF', '#DDBEFF', '#C6DFF3', '#7EAED7', '#4F7794', '#FEE2A1', '#FDD472', '#FCB714', '#F79A7E', '#F15628', '#B5411E'])
  # Grid, major and minor ticks settings
  ax.grid(visible=True, which='both')
  ax.minorticks_on()
  ax.grid(which='major', color='#a9a9a9', linewidth=1)
  ax.grid(which='minor', color='#e0e0e0', linewidth=0.6)
  ax.tick_params(which='minor', color='#e0e0e0')
  ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=MO))
  # Format x tick labels
  for label in ax.get_xticklabels(which='major'):
    label.set(rotation=0, horizontalalignment='center')
  # Set x axis range
  xlimoOffset = datetime.timedelta(days=7)
  ax.set_xlim(datetime.datetime(2021, 8, 1) - xlimoOffset, datetime.datetime(2022, 5, 1) + xlimoOffset)
  
  # 0. Axis - Daily Admissions Stacked by age_group
  colLabels = []
  for column in df:
    # Custom column labels
    colLabels.append(str(round(column)-5)+'-'+str(round(column)+5))
  ax.stackplot(df.index, df[5.0], df[15.0], df[25.0], df[35.0], df[45.0], df[55.0], df[65.0], df[75.0], df[85.0], df[95.0], df[105.0], labels=colLabels)
  ax.set_title('Slovakia Covid Hospital Admission Daily ma7 - Stacked by age_group', loc='center', y=1.002, x=0.5, fontsize='large')
  ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(2))
  ax.legend(loc='upper right')
  ax.set_xlabel(None)
  ax.set_ylabel("Age groups [%]")
  ax.set_ylim(0, 100)

  # Note inside plot
  ax.annotate('Source: github.com/Institut-Zdravotnych-Analyz/covid19-data (' + str(release_date) + ')',
                xy = (1.0, -0.06),
                xycoords='axes fraction',
                ha='right',
                va="center",
                fontsize=8)

  plt.savefig('./res/Hospitalizations/Admissions_Stacked_by_Age_Daily.png')