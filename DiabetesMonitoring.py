"""
A Python module to import diabetes management data from various sources for use to
integrate multiple views.

Supported files:
- Dexcom
- Omnipod log files (manually copied from Omnipod)

- To utilize other data sources, check the ReadMe for detailed file structures.


Chelsea Lapeikis
University of Utah
11-24-2017


"""
import os
import re
import pandas as pd
import time
import datetime
import numpy as np



__version__ = '0.1'


class DiabetesManagement(object):
    """
    Converts .CSV data from

    Inputs:
        path:      Relative or absolute path to export.xml
        verbose:   Set to False for less verbose output

    Outputs:
        Writes a CSV file for each record type found, in the same
        directory as the input export.xml. Reports each file written
        unless verbose has been set to False.
    """

    def __init__(self, diagnosis_year, dob, sex, name="", a1c_target=7.0, diagnosis_type=1) -> object:
        """


        """
        self.__sex = sex.upper()[0]
        self.__name = name
        self.dob = dob
        self.a1c_target = a1c_target
        self.diagnosis_year = diagnosis_year
        self.diagnosis_type = diagnosis_type

    @property
    def name(self):
        if type(self.name) == str:
            return self.__name
        else:
            raise TypeError("Name must be a string.")

    @property
    def sex(self):
        return self.__sex

    @sex.setter
    def sex(self, value):
        if not isinstance(value, str):
            raise TypeError("Sex must be a string")
        if not value.upper()[0] in "MF":
            raise ValueError("Sex must be Male or Female")

    @property
    def diagnosis_type(self):
        return self.diagnosis_type

    @diagnosis_type.setter
    def diagnosis_type(self, value):
        try:
            int(value)
        except TypeError:
            raise TypeError("Diagnosis type must be an integer (1 or 2).")

    @property
    def a1c_target(self):
        return self.diagnosis_type

    @a1c_target.setter
    def a1c_target(self, value):
        if type(value) == float:
            pass
        try:
            float(value)
        except TypeError:
            raise TypeError("Target a1c value must be a number.")

    @property
    def eag(self):
        """
        Returns the average blood glucose level for the target a1c.
        Source: http://care.diabetesjournals.org/content/diacare/early/2008/06/07/dc08-0545.full.pdf
        """
        eag = 28.7*self.a1c_target-46.7
        return eag


# Insulin on board (IOB) information is only contained within a comment string and must be extracted.
Meal_IOB = r"""Meal IOB: (\d{0,2}\.\d{1,2})(?=;)"""
Correction_IOB = r"""Correction IOB: (\d{0,2}\.\d{0,2})"""
Override = "Override"


class DiabetesData(object):
    def __init__(self, file_folder, file_name, data_type=""):
        self.file_folder = file_folder
        self.path = os.path.abspath(os.path.join("..", file_folder, file_name))
        self.directory = os.path.abspath(os.path.join("..", file_folder))
        self.file_format = os.path.splitext(self.path)[1]
        self.data_type = data_type

        if self.file_format not in ['.xlsx', '.xls', '.csv']:
            raise TypeError('File must be .xlsx, .xls, or .csv.')

    @property
    def file_name(self):
        return self.file_name

    def read_data(self):
        """
        A function to read data into a dataframe from a variety of sources.
        :return:
        """
        if self.file_format == ".xlsx":
            diabetes_dataframe = pd.read_excel(self.path, na_values='').fillna('0 NoDescription').drop_duplicates()
        elif self.file_format == ".csv":
            diabetes_dataframe = pd.read_csv(self.path, na_values='').fillna('0 NoDescription').drop_duplicates()

        # Generate a pickle file to save the data REPLACE LATER
        # timestr = time.strftime("%Y%m%d-%H%M%S")
        # diabetes_dataframe.to_csv(self.directory+"Omnipod"+timestr+".csv")  #, compression='gzip')

        # Split units from values
        diabetes_dataframe['Value'], diabetes_dataframe['Units'] = diabetes_dataframe['Value'].str.split(' ', 1).str
        diabetes_dataframe[['Value']] = diabetes_dataframe[['Value']].apply(pd.to_numeric)
        diabetes_dataframe = diabetes_dataframe.fillna(float(0))

        return diabetes_dataframe

    def __str__(self):
        txt = "Datasource: %s\n"%self.data_type
        txt += "File is located at: %s\n"%self.path

        return txt


class Omnipod(DiabetesData):
    def __init__(self, file_folder, file_name, data_type="", diabetes_df=""):
        DiabetesData.__init__(self, file_folder, file_name, data_type)
        self.__diabetes_df = diabetes_df

    @property
    def diabetes_df(self):
        diabetes_df = DiabetesData.read_data(self)
        return diabetes_df

        #if type(diabetes_df) != 'z':
        #    pass


def remove_summary(x):
    df = x[x.Type != 'Insulin Summary']
    return df

def extract_dedup(df_i):
    df = remove_summary(df_i)

    #change is_copy to False to eliminate warnings
    df.is_copy = False

    # create datetime field
    df['Date'] = df['Date'].apply(lambda x: x.date())
    df['Date Time'] = df[['Date', 'Time']].apply(lambda x: datetime.datetime.combine(*list(x)), axis=1)

    #IOB values
    df['Meal IOB'] = df['Comment'].str.extract(Meal_IOB, expand=True)
    df['Meal IOB'] = df['Meal IOB'].apply(lambda x: float(x))
    df['Correction IOB'] = df['Comment'].str.extract(Correction_IOB, expand=True)
    df['Correction IOB'] = df['Correction IOB'].apply(lambda x: float(x))


    #Add override flag
    df['Manual Override'] = pd.np.where(df.Description.str.contains(Override), 1, 0)

    # remove redundancies to make data pivot table
    df['Bolus Clean'] = pd.np.where(df.Description.str.contains("Bolus-Meal"), "Meal Bolus",
                                    pd.np.where(df.Description.str.contains("Correction"), "Correction Bolus",
                                                pd.np.where(df.Description.str.contains("Extended"),
                                                            "Extended Meal Bolus",
                                                            pd.np.where(
                                                                df.Description.str.contains("Basal suspended"),
                                                                "Basal Suspended",
                                                                pd.np.where(df.Description.str.contains(
                                                                    "Temporary basal rate set"), "Temp Basal",
                                                                            pd.np.where(df.Description.str.contains(
                                                                                "Pod deactivated"),
                                                                                        "Pod Deactivated",
                                                                                        pd.np.where(
                                                                                            df.Description.str.contains(
                                                                                                "Basal resumed"),
                                                                                            "Basal Resumed",
                                                                                            df["Type"])))))))
    df.drop_duplicates()

    return df

def to_tabular(df_i):
    """
    A function to convert omnipod data to a usable (tabular) format for visualization
    :param df_i:
    :return:
    """
    df = remove_summary(df_i)
    df = extract_dedup(df)
    df_pivot = df.pivot(index='Date Time', columns='Bolus Clean', values='Value')
    df_pivot['Date Time'] = df_pivot.index  # Add Date Time index back into dataframe as a column

    new = pd.merge(df_pivot, df, how='inner', on='Date Time')
    new = new[['Date Time',
              'Glucose',
              'Meal', #carbohydrates
              'Meal Bolus', 'Bolus Insulin', 'Correction Bolus','Extended Meal Bolus',
              'Meal IOB', 'Correction IOB', 'Manual Override',
              'Basal Insulin', 'Basal Resumed', 'Basal Suspended', 'Temp Basal',
              'Pod Deactivated', 'Pump Alarm', 'Date', 'Time']]

    new = new.replace(np.NaN, 0.00).drop_duplicates()

    return new



#print(OData.__str__())

#OD = Omnipod(file_folder="BMI6018-TermProject/Omnipod", file_name="Omnipod_20171024.xlsx", data_type="Omnipod", diabetes_df=ODataF)
#ODataNew = OD.remove_summary()
#ODataNew2 = OD.to_tabular()

#print(ODataNew2.head())


OData = DiabetesData(file_folder="BMI6018-TermProject/Omnipod", file_name="Omnipod_20171024.xlsx", data_type="Omnipod")
ODataF = OData.read_data()
ODataF_1 = extract_dedup(ODataF)
ODataF_2 = to_tabular(ODataF)
#print(ODataF_2.head(10))
print(ODataF_2.head(10)) #.dtypes)




