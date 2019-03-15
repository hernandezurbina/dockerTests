
def validateString(stringToValidate):

    stringToValidate = stringToValidate.replace('"', '')
    stringToValidate = stringToValidate.replace("'", "")
    stringToValidate = stringToValidate.replace('%', '')
    stringToValidate = stringToValidate.replace(',', '')
    stringToValidate = stringToValidate.lower()
    stringToValidate = stringToValidate.strip()
    stringToValidate = "%".join(stringToValidate.split(' '))

    return stringToValidate

def validateNumber(stringToValidate):

    stringToValidate = stringToValidate.replace('"', '')
    stringToValidate = stringToValidate.replace("'", "")
    stringToValidate = stringToValidate.replace('%', '')
    stringToValidate = stringToValidate.replace(',', '')
    stringToValidate = stringToValidate.lower()
    stringToValidate = stringToValidate.strip()

    return stringToValidate
