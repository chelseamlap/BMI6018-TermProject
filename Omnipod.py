import os
import re
import pandas as pd
import time

# Insulin on board (IOB) information is only contained within a comment string and must be extracted.
Meal_IOB = re.compile(r"""Meal IOB: \d{1,2}(\.\d{1,2})""")
Correction_IOB = re.compile(r"""Correction IOB: \d{1,2}(\.\d{1,2})""")
Override = "Override."


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
        if self.file_format == "excel":
            diabetes_dataframe = pd.read_excel(self.path, na_values='').fillna('No Description').drop_duplicates()
        elif self.file_format == "csv":
            diabetes_dataframe = pd.read_csv(self.path, na_values='').fillna('No Description').drop_duplicates()

        # Generate a pickle file to save the data
        timestr = time.strftime("%Y%m%d-%H%M%S")
        diabetes_dataframe.to_csv(self.directory+"Omnipod"+timestr+".csv")  #, compression='gzip')

        return diabetes_dataframe

    def __str__(self):
        txt = "Datasource: %s\n"%self.data_type
        txt += "File is located at: %s\n"%self.path

        return txt


#OData = DiabetesData(file_folder="BMI6018-TermProject/Omnipod", file_name="Omnipod_20171024.xlsx", data_type="Omnipod")
#print(OData.__str__())


