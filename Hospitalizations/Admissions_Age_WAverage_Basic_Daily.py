import datetime
import requests
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

  # --- Daily Admissions - Axis 1
  df = pd.DataFrame()
  df['Admissions'] = raw['Admissions'].groupby(raw['Date']).sum()
  df['Admissions_ma7'] = df['Admissions'].rolling(7, closed='left').mean()

  # --- Daily weighten average age_group - Axis 0
  raw = raw.dropna(subset=['age_group']) # Additional cleansing before weighten average --> Remove NaN for proper calculation
  df['age_group_WAverage'] = raw.groupby(raw['Date']).apply(lambda x: np.average(x.age_group, weights=x.Admissions))
  df['age_group_WAverage_ma7'] = df['age_group_WAverage'].rolling(7, closed='left').mean()


  # --- Plot figure
  fig, axs = plt.subplots(2, 1, figsize=(10, 8))
  plt.subplots_adjust(left=0.06, right=0.99, bottom= 0.065, top=0.99, hspace=0.06)

  # Common axis settings:
  for ax in axs:
    ax.set_prop_cycle(color=['#FFC1C2','#dc0002'])
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
  
  # 0. Axis - Daily weighten average age
  ax = axs[0]
  ax.plot(df['age_group_WAverage'], label='Daily')
  ax.plot(df['age_group_WAverage_ma7'], label='Daily_ma7')
  ax.set_title('Slovakia Covid Hospital Admission Daily - age_group Weighted Average & ma7', loc='left', y=0.9, x=0.02, fontsize='medium', backgroundcolor='white')
  ax.set_xticklabels([])
  ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(2))
  # ax.legend(loc='upper right')
  ax.set_xlabel(None)
  ax.set_ylabel("Age")
  ax.set_ylim(40, 90)

  # 1. Axis - Daily admissions
  ax = axs[1]
  ax.plot(df['Admissions'], label='Admissions')
  ax.plot(df['Admissions_ma7'], label='Admissions_ma7')
  ax.fill_between(x=df['Admissions'].index, y1=df['Admissions'].values)
  ax.set_title('Slovakia Covid Hospital Admission Daily & ma7', loc='left', y=0.9, x=0.02, fontsize='medium', backgroundcolor='white')
  ax.yaxis.set_major_locator(mticker.MultipleLocator(100))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(20))
  ax.set_xlabel(None)
  ax.set_ylabel("Admissions", labelpad=0)
  ax.set_ylim(0, 500)

  # Note inside plot
  ax.annotate('Source: github.com/Institut-Zdravotnych-Analyz/covid19-data (' + str(release_date) + ')',
                xy = (1.0, -0.12),
                xycoords='axes fraction',
                ha='right',
                va="center",
                fontsize=8)

  plt.savefig('./res/Hospitalizations/Admissions_Age_WAverage_Basic_Daily.png')