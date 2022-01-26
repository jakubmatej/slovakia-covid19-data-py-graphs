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

  # Replace NA vaccinated status with unknown
  raw['Vaccinated'] = raw['Vaccinated'].fillna(value='unknown')

  # --- Sum Vaccine status (True/False) on Admissions - Axis 0
  p = pd.pivot_table(raw, index=['Date', 'age_group'] , columns=['Vaccinated'], values='Admissions', aggfunc=np.sum, fill_value=0, dropna=False)
  p = p.rename(columns={False:'unvaccinated', True:'vaccinated'})
  p = p.reset_index(1)
  p['age_group'] = p['age_group'].astype(np.int8)
  
  # - Split Data into categories
  wa_unvaccinated = p.loc[~(p['unvaccinated'] == 0)]

  wa_vaccinated = p.loc[~(p['vaccinated'] == 0)]

  unk = p.loc[~(p['unknown'] == 0)]

  # - Calculate Average by weights for each Age category
  wa_unvaccinated = wa_unvaccinated.groupby(wa_unvaccinated.index).apply(lambda x: np.average(x.age_group, weights=x.unvaccinated))
  wa_unvaccinated = wa_unvaccinated.rename('unvaccinated')

  wa_vaccinated = wa_vaccinated.groupby(wa_vaccinated.index).apply(lambda x: np.average(x.age_group, weights=x.vaccinated))
  wa_vaccinated = wa_vaccinated.rename('vaccinated')

  unk = unk.groupby(unk.index).apply(lambda x: np.average(x.age_group, weights=x.unknown))
  unk = unk.rename('unknown')

  # - Result weighten average age
  result = pd.DataFrame.join(wa_unvaccinated.to_frame(), wa_vaccinated.to_frame(), on='Date')
  result = result.join(unk.to_frame(), on='Date')

  # - Moving average
  result['unvaccinated_7ma'] = result['unvaccinated'].rolling(7, closed='left').mean()
  result['vaccinated_7ma'] = result['vaccinated'].rolling(7, closed='left').mean()
  result['unknown_7ma'] = result['unknown'].rolling(7, closed='left').mean()

  # --- Sum admissions Daily - Axis 1
  resultAD = pd.DataFrame()
  resultAD['unvaccinated_adm'] = p['unvaccinated'].groupby(level=['Date']).sum()
  resultAD['vaccinated_adm'] = p['vaccinated'].groupby(level=['Date']).sum()
  resultAD['unknown_adm'] = p['unknown'].groupby(level=['Date']).sum()

  # - Moving average
  resultAD['unvaccinated_adm_7ma'] = resultAD['unvaccinated_adm'].rolling(7, closed='left').mean()
  resultAD['vaccinated_adm_7ma'] = resultAD['vaccinated_adm'].rolling(7, closed='left').mean()
  resultAD['unknown_adm_7ma'] = resultAD['unknown_adm'].rolling(7, closed='left').mean()

  # print(result)
  # print(resultAD)

  # --- Plot figure
  fig, axs = plt.subplots(2, 1, figsize=(10, 8))
  plt.subplots_adjust(left=0.06, right=0.99, bottom= 0.065, top=0.99, hspace=0.06)

  # Common axis settings:
  for ax in axs:
    ax.set_prop_cycle(color=['#D9D9D9','#A4DBFD','#FFDFA4','#898989','#069af3','#ffa500'])
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
  ax.plot(result['unknown'], label='unknown')
  ax.plot(result['vaccinated'], label='vaccinated')
  ax.plot(result['unvaccinated'], label='unvaccinated')
  ax.plot(result['unknown_7ma'], label='unknown_7ma')
  ax.plot(result['vaccinated_7ma'], label='vaccinated_7ma')
  ax.plot(result['unvaccinated_7ma'], label='unvaccinated_7ma')
  ax.set_title('Slovakia Covid Hospital Admission Daily - age_group Weighted Average & 7ma', loc='left', y=0.9, x=0.02, fontsize='medium', backgroundcolor='white')
  ax.set_xticklabels([])
  ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(2.5))
  ax.legend(loc='upper right')
  ax.set_xlabel(None)
  ax.set_ylabel("Age")
  ax.set_ylim(35, 85)

  # 1. Axis - Daily admissions
  ax = axs[1]
  ax.bar(resultAD.index, resultAD['unknown_adm'].values, width=1, align='edge')
  ax.bar(resultAD.index, resultAD['vaccinated_adm'].values, bottom=resultAD['unknown_adm'].values, width=1, align='edge')
  ax.bar(resultAD.index, resultAD['unvaccinated_adm'].values, bottom=resultAD['unknown_adm'].values+resultAD['vaccinated_adm'].values, width=1, align='edge')
  ax.set_prop_cycle(color=['#898989','#069af3','#ffa500'])
  ax.plot(resultAD['unknown_adm_7ma'], label='unknown_7ma')
  ax.plot(resultAD['vaccinated_adm_7ma']+resultAD['unknown_adm_7ma'].values, label='vaccinated_7ma')
  ax.plot(resultAD['unvaccinated_adm_7ma']+resultAD['unknown_adm_7ma'].values+resultAD['vaccinated_adm_7ma'].values, label='unvaccinated_7ma')
  ax.set_title('Slovakia Covid Hospital Admission Daily', loc='left', y=0.9, x=0.02, fontsize='medium', backgroundcolor='white')
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

  plt.savefig('./res/Hospitalizations/Admissions_Age_WAverage_by_Vaccine_Daily.png')