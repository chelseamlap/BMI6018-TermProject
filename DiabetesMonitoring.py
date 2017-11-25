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
        self.sex = sex.upper()[0]
        self.name = name
        self.dob = dob
        self.a1c_target = a1c_target
        self.diagnosis_year = diagnosis_year
        self.diagnosis_type = diagnosis_type

    @property
    def name(self):
        if type(self.name) == str:
            return self.name
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


# Now that the targets are defined for your monitoring, we can start looking at the data itself.

class Omnipod(DiabetesManagement):
    def __init__(self, path, diagnosis_year, dob, sex, name, a1c_target, diagnosis_type\
                 ):
        DiabetesManagement.__init__(self, diagnosis_year, dob, sex, name, a1c_target, diagnosis_type)
        self.path = path


