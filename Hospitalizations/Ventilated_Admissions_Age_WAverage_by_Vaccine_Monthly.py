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
  row_no = raw.loc[raw['Date'] == '2021-08-01'].last_valid_index()
  raw = raw.drop(raw.index[row_no:])

  # --- Convert date to month no.
  raw['Date'] = raw['Date'].apply(pd.to_datetime)
  raw['Date'] = raw['Date'].values.astype('datetime64[M]') # OUT: YYYY-mm-dd, result is first date in month
  # raw['Date'] = raw['Date'].to_period('M') # >>> OUT: YYYY-mm, result is not of the datetime64
  # month_grp = pd.Grouper(key='Date',freq='M') # >>> OUT: YYYY-mm-dd, result is last date in month 

  # --- Create pivot table
  p = pd.pivot_table(raw, index=['Date', 'age_group'] , columns=['Vaccinated'], values='Admissions', aggfunc=np.sum, fill_value=0)
  p = p.rename(columns={False:'unvaccinated', True:'vaccinated'})

  # --- Split Data into categories

  # Remove rows with zero
  # When using the average function, if weights are given, they can not add up to 0 because that leads to division by 0
  wa_unvax = p.loc[~(p['unvaccinated'] == 0)]
  # Applay reset_index to avoid MultiIndex
  wa_unvax = wa_unvax.reset_index(1)

  wa_vax = p.loc[~(p['vaccinated'] == 0)]
  wa_vax = wa_vax.reset_index(1)

  # --- Calculate Average by weights for each category
  # https://stackoverflow.com/questions/31521027/groupby-weighted-average-and-sum-in-pandas-dataframe
  wa_unvax = wa_unvax.groupby(wa_unvax.index).apply(lambda x: np.average(x.age_group.astype(np.int8), weights=x.unvaccinated))
  wa_unvax = wa_unvax.rename('unvaccinated') # Renamed for proper graph legend

  wa_vax = wa_vax.groupby(wa_vax.index).apply(lambda x: np.average(x.age_group.astype(np.int8), weights=x.vaccinated))
  wa_vax = wa_vax.rename('vaccinated')

  # --- Result Data as new DataFrame
  result = pd.DataFrame.join(wa_unvax.to_frame(), wa_vax.to_frame(), on='Date')
  result['unvaccinated_qty'] = p['unvaccinated'].groupby(level=['Date']).sum()
  result['vaccinated_qty'] = p['vaccinated'].groupby(level=['Date']).sum()
  # print(result.head())
  # print(type(result))

  # --- Plot
  # plt.figure("SVK C19 Hospital Ventilated Admissions")
  fig, axs = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

  # Custom plot layout (set constrained_layout=False)
  # plt.subplots_adjust(left=0.07, right=0.99, bottom= 0.07, top=0.99)

  # Common axis settings:
  for ax in axs:
      ax.set_prop_cycle(color=['#ffa500', '#069af3'])
      # Grid, major and minor ticks settings
      ax.grid(visible=True, which='both')
      ax.minorticks_on()
      ax.grid(which='major', color='#a9a9a9', linewidth=1)
      ax.grid(which='minor', color='#e0e0e0', linewidth=0.6)
      ax.tick_params(which='minor', color='#e0e0e0')
      ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
      ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
      ax.xaxis.set_minor_locator(mticker.NullLocator())
      ax.set_xlabel(None)
      # Set x axis range
      xlimoOffset = datetime.timedelta(days=7)
      ax.set_xlim(datetime.datetime(2021, 8, 1) - xlimoOffset, datetime.datetime(2022, 5, 1) + xlimoOffset)
      
  # 0. Axis - Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average
  ax = axs[0]
  ax.plot(result['unvaccinated'], label='unvaccinated', marker='o')
  ax.plot(result['vaccinated'], label='vaccinated', marker='o')
  ax.set_title('Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average', loc='left', y=0.9, x=0.02, fontsize='medium', backgroundcolor='white')
  ax.set_xticklabels([])
  ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(1))
  ax.legend()
  ax.set_ylabel('Age')
  ax.set_ylim(40, 80)
  # Create marker labels
  yAnnotateOffset = 0.03
  for idx, row in result.iterrows():
    ax.annotate(row['unvaccinated'].round(2), xy=(idx, row['unvaccinated']*(1-yAnnotateOffset)), fontsize=8, ha='center', va='top')
    ax.annotate(row['vaccinated'].round(2), xy=(idx, row['vaccinated']*(1+yAnnotateOffset)), fontsize=8, ha='center', va='center')

  # 1. Axis - Slovakia Covid Hospital Ventilated Admissions
  ax = axs[1]
  ax.bar(result.index, result['unvaccinated_qty'].values, bottom=result['vaccinated_qty'].values, width=10)
  ax.bar(result.index, result['vaccinated_qty'].values, width=10)
  ax.set_title('Slovakia Covid Hospital Ventilated Admissions', loc='left', y=0.9, x=0.02, fontsize='medium', backgroundcolor='white')
  ax.yaxis.set_major_locator(mticker.MultipleLocator(100))
  ax.yaxis.set_minor_locator(mticker.MultipleLocator(50))
  # Format x tick labels
  for label in ax.get_xticklabels(which='major'):
    label.set(rotation=0, horizontalalignment='center')
  ax.set_ylabel('Admissions')
  ax.set_ylim(0, 900)

  # Note inside plot area - foot note
  ax.annotate('Source: github.com/Institut-Zdravotnych-Analyz/covid19-data (' + str(release_date) + ')',
                xy = (1.0, -0.12),
                xycoords='axes fraction',
                ha='right',
                va='center',
                fontsize=8)

  plt.savefig('./res/Hospitalizations/Ventilated_Admissions_Age_WAverage_by_Vaccine_Monthly.png')