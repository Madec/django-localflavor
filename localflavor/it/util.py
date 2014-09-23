# -*- coding: utf-8 -*

from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from .it_codici import CODICI_CHOICES
import re

PATTERN = '^[A-Z]{6}[0-9]{2}([ABCDEHLMPRST])[0-9]{2}[A-Z][0-9]([A-Z]|[0-9])[0-9][A-Z]$'

MONTHSCODE = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'P', 'R', 'S', 'T']

def ssn_isvalid(code):
    """``ssn_isvalid(code) -> bool``

    This function checks if the given fiscal code is syntactically valid.

    eg: isvalid('RCCMNL83S18D969H') -> True
        isvalid('RCCMNL83S18D969') -> False
    """
    return isinstance(code, str) and re.match(PATTERN, code) is not None

def ssn_get_birthday(code):
    """``ssn_get_birthday(code) -> string``

    Birthday of the person whose fiscal code is 'code', in the format DD-MM-YY.

    Unfortunately it's not possible to guess the four digit birth year, given
    that the Italian fiscal code uses only the last two digits (1983 -> 83).
    Therefore, this function returns a string and not a datetime object.

    eg: ssn_get_birthday('RCCMNL83S18D969H') -> 18-11-83
    """
    assert ssn_isvalid(code)

    day = int(code[9:11])
    day = day < 32 and day or day - 40

    month = MONTHSCODE.index(code[8]) + 1
    year = int(code[6:8])

    return "%02d/%02d/%02d" % (day, month, year)


def ssn_get_municipality(code):
    """``ssn_get_municipality(code) -> string``

    The municipality of the person whose fiscal code is 'code'.

    eg: ssn_get_municipality('RCCMNL83S18D969H') -> 'Genova'
        ssn_get_municipality('CNTCHR83T41D969D') -> 'Genova'
    """
    assert ssn_isvalid(code)
    return CODICI_CHOICES.get(code[-5:-1], 'Altro')


def ssn_get_sex(code):
    """``get_sex(code) -> string``

    The sex of the person whose fiscal code is 'code'.

    eg: get_sex('RCCMNL83S18D969H') -> 'M'
        get_sex('CNTCHR83T41D969D') -> 'F'
    """

    assert ssn_isvalid(code)

    return int(code[9:11]) < 32 and 'M' or 'F'

def ssn_check_digit(value):
    "Calculate Italian social security number check digit."
    ssn_even_chars = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, 'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7,
        'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15,
        'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
        'Y': 24, 'Z': 25
    }
    ssn_odd_chars = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8':
        19, '9': 21, 'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15,
        'H': 17, 'I': 19, 'J': 21, 'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11,
        'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14, 'U': 16, 'V': 10, 'W': 22,
        'X': 25, 'Y': 24, 'Z': 23
    }
    # Chars from 'A' to 'Z'
    ssn_check_digits = [chr(x) for x in range(65, 91)]

    ssn = value.upper()
    total = 0
    for i in range(0, 15):
        try:
            if i % 2 == 0:
                total += ssn_odd_chars[ssn[i]]
            else:
                total += ssn_even_chars[ssn[i]]
        except KeyError:
            msg = "Character '%(char)s' is not allowed." % {'char': ssn[i]}
            raise ValueError(msg)
    return ssn_check_digits[total % 26]


def ssn_validation(ssn_value):
    """
    Validate Italian SSN for persons

    ``ValueError`` is raised if validation fails.
    """
    check_digit = ssn_check_digit(ssn_value)
    if ssn_value[15] != check_digit:
        raise ValueError(_('Check digit does not match.'))
    return ssn_value


def vat_number_validation(vat_number):
    """
    Validate Italian VAT number. Used also for entities SSN validation.

    ``ValueError`` is raised if validation fails.
    """
    vat_number = str(int(vat_number)).zfill(11)
    check_digit = vat_number_check_digit(vat_number[0:10])
    if vat_number[10] != check_digit:
        raise ValueError(_('Check digit does not match.'))
    return smart_text(vat_number)


def vat_number_check_digit(vat_number):
    "Calculate Italian VAT number check digit."
    normalized_vat_number = smart_text(vat_number).zfill(10)
    total = 0
    for i in range(0, 10, 2):
        total += int(normalized_vat_number[i])
    for i in range(1, 11, 2):
        quotient, remainder = divmod(int(normalized_vat_number[i]) * 2, 10)
        total += quotient + remainder
    return smart_text((10 - total % 10) % 10)
