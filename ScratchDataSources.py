import pandas as pd
# import xlrd

HRData = pd.read_excel('C:\\Users\chelsea.lapeikis\Desktop\HealthPython\HKQuantityTypeIdentifierHeartRate.xlsx')
# want to read in all possible files but we will start with HR data
Omnipod = pd.read_excel('C:\\Users\chelsea.lapeikis\Desktop\HealthPython\Omnipod\Omnipod_20171024_clean01.xlsx')

Omnipod_bg = pd.read_excel('C:\\Users\chelsea.lapeikis\Desktop\HealthPython\Omnipod\Omnipod_20171024_clean01.xlsx')

Dexcom = pd.read_csv('C:\\Users\chelsea.lapeikis\Desktop\HealthPython\Dexcom\CLARITY_Export__Mlapeikis.csv',
                     header=0, skiprows=range(1, 9)).dropna(how="all", axis=1)
Dexcom.rename(columns={'Timestamp (YYYY-MM-DDThh:mm:ss)': 'event_time'}, inplace=True)
Dexcom['event_time'] = Dexcom['event_time'].astype('datetime64[ns]')

Exercise = pd.read_excel('C:\\Users\chelsea.lapeikis\Desktop\HealthPython\AppleHealth\ExerciseClean_20171024.xlsx',
                         sheetname="Clean").dropna(how="all", axis=1)
Exercise['creation_date'] = Exercise['creation_date'].apply(
    lambda x: x.date())  # to remove the datetime from the creation date

Exercise['PreworkoutPeriodBegin'] = Exercise['start_date'] - pd.Timedelta("2 hours")
Exercise['PostworkoutPeriodEnd'] = Exercise['start_date'] + pd.Timedelta("4 hours")
# print(Exercise.head())
# print(Dexcom.head())
# print(Omnipod.head())
# print(Exercise.head())

# Combined = pd.merge_asof(Exercise,Dexcom, how='inner',left_on= 'start_date', right_on='event_time')
Combined_Ex = pd.merge_asof(Exercise, Dexcom, left_on='start_date', right_on='event_time',
                            tolerance=pd.Timedelta("4.5 minutes"), direction="nearest").fillna('NaN').dropna(how="all",
                                                                                                             axis=1)

# Dexcom is the base of the data
Combined_Dex = pd.merge_asof(Dexcom, Exercise, left_on='event_time', right_on='start_date',
                             tolerance=pd.Timedelta("4.5 minutes"), direction="nearest").fillna('NaN').dropna(how="all",
                                                                                                              axis=1)


test_pivot = Omnipod_bg.pivot(index=['Date', 'Time'], columns='Type', values='Value')

print(test_pivot.head())