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
Meal_IOB = re.compile(r"""Meal IOB: \d{1,2}(\.\d{1,2})""")
Correction_IOB = re.compile(r"""Correction IOB: \d{1,2}(\.\d{1,2})""")


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






