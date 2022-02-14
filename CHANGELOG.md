# Changelog

All notable changes to this project will be documented in this file.

## 1.0.6 - 2022-02-14

### Added
- Added python scripts for Slovakia Covid Hospital Admission Daily ma7 - Stacked by age_group.
- Added new graph figures.

### Updated
- Minor tweaks on all hospitalization scripts.
- Updated workflow daily-figures-update.yaml
- Updated graph figures.

## 1.0.5 - 2022-02-11

### Added
- Added python scripts for Daily Slovakia Covid Hospital Admissions and age_group Weighted Average.
- Added new graph figures.

### Updated
- Updated Admissions_Age_WAverage_by_Vaccine_Daily.py - Updated raw data cleansing by changing age_group to middle value, updated y limit and minor ticks on Axis 0
- Updated workflow daily-figures-update.yaml

## 1.0.4 - 2022-01-28

### Updated
- Updated workflow daily-figures-update.yaml
- Updated Admissions_Age_WAverage_by_Vaccine_Daily.py - Daily admissions axis plot changed from bars to filled area, fixed raw data by cleansing NaN

## 1.0.3 - 2022-01-26

### Added
- Added python scripts for Daily Slovakia Covid Hospital Admissions by Vaccine status and age_group Weighted Average.
- Added graph figure.

### Updated
- Updated workflow daily-figures-update.yaml

## 1.0.2 - 2022-01-22

### Added
- Added workflow daily-figures-update.yaml

### Updated
- Minor tweaks in Ventilated_Admissions_Age_WAverage_by_Vaccine_Daily.py and Ventilated_Admissions_Age_WAverage_by_Vaccine_Monthly.py

## 1.0.1 - 2022-01-19

### Updated
- Minor update of Ventilated_Admissions_Age_WAverage_by_Vaccine_Daily.py - minor plot code update, code corrections, extended date range.
- Major update of Ventilated_Admissions_Age_WAverage_by_Vaccine_Monthly.py - new plot code, added 2nd axis, extended date range.
- Changed graph figures location (prepare for automatization).

## 1.0.0 - 2021-12-09

### Added
- Added README.md file.
- Added LICENSE file.
- Added requirements.txt file.
- Added python scripts for Daily Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average & 7ma.
- Added python scripts for Monthly Slovakia Covid Hospital Ventilated Admissions - age_group Weighted Average.
- Added graph figures.

### Fixed
- UPV_Admission_Age_WAverage_by_Vaccine_Daily.py & UPV_Admission_Age_WAverage_by_Vaccine_Monthly.py:
  - Fixed raw input due source file change. [See IZA commits from 06-12-2021](https://github.com/Institut-Zdravotnych-Analyz/covid19-data/tree/main/Hospitals)