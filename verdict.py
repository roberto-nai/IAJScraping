# sentence.py

# Sentence Class
from urllib.parse import urlparse, parse_qs

class Verdict:

    @staticmethod
    def check_null_or_empty(value):
        if (value!=None):
            if (len(value) == 0):
                return "n.d."
            else:
                return str(value)
        else:
            return "n.d."
        
    @staticmethod
    def extract_nrg_from_url(url:str) -> str:
        """
        Extracts the value of the 'nrg' parameter from the given URL (nrg is the complaint number).

        Args:
            url (str): The URL from which to extract the 'nrg' parameter value.

        Returns:
            str: The value of the 'nrg' parameter if found in the URL, otherwise an empty string.
        """

        nrg_value = None
        
        # Parse the URL
        parsed_url = urlparse(url)
    
        # Get the query parameters as a dictionary
        query_params = parse_qs(parsed_url.query)
    
        # Get the value of the 'nrg' parameter
        nrg_value = query_params.get('nrg', [''])[0]  # Default to empty string if 'nrg' parameter is not present
    
        return nrg_value
    
    def __init__(self):
        """
        Initializes an instance of Sentence with default attribute values.
        This method initializes the instance with default values for its attributes.

        Args:
            self: The object instance.

        Returns:
            None

        Example:
            obj = MyClass()
        """

        default_values = {
            "sentence_ecli": None,
            "sentence_title": None,
            "sentence_type": None,
            "sentence_number": None,
            "tribunal_code": None,
            "tribunal_city": None,
            "tribunal_section": None,
            "complaint_number": None,
            "sentence_url": None,
            "sentence_filename": None
        }
        for attr, value in default_values.items():
            setattr(self, attr, value)
        

    def toString(self) -> None:
        """
        Convert the object to a string representation.
        This method prints the properties of the object in a formatted manner.

        Args:
            self: The object instance.

        Retursn:
            None
        """

        
        properties = [
        ("Provvedimento - ECLI:", self.sentence_ecli),
        ("Provvedimento - titolo:", self.sentence_title),
        ("Provvedimento - tipo:", self.sentence_type),
        ("Provvedimento - numero:", self.sentence_number),
        ("Tribunale - codice:", self.tribunal_code),
        ("Tribunale - città:", self.tribunal_city),
        ("Tribunale - sezione:", self.tribunal_section),
        ("Ricorso - numero:", self.complaint_number),
        ("Sentenza - URL:", self.sentence_url),
        ("Sentenza - file:", self.sentence_filename)
        ]

        self.complaint_number = Verdict.extract_nrg_from_url(self.sentence_url)

        for label, value in properties:
            print(label, Verdict.check_null_or_empty(value))

    def toCSV(self) -> str:

        self.complaint_number = Verdict.extract_nrg_from_url(self.sentence_url)

        csv_values = [
        Verdict.check_null_or_empty(self.sentence_ecli),
        Verdict.check_null_or_empty(self.sentence_title),
        Verdict.check_null_or_empty(self.sentence_type),
        Verdict.check_null_or_empty(self.sentence_number),
        Verdict.check_null_or_empty(self.tribunal_code),
        Verdict.check_null_or_empty(self.tribunal_city),
        Verdict.check_null_or_empty(self.tribunal_section),
        Verdict.check_null_or_empty(self.complaint_number),
        Verdict.check_null_or_empty(self.sentence_url),
        Verdict.check_null_or_empty(self.sentence_filename)
        ]
    
        # Join the values with ';' separator
        csv_string = ";".join(csv_values)

        # Add a header row
        # header_row = "ECLI;Title;Type;Number;Tribunal Code;Tribunal City;Tribunal Section;Recourse Number;URL;Filename\n"

        # Return the CSV string with header row
        return csv_string
