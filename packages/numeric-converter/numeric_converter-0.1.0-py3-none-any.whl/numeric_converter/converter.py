"""
Converter functions for Roman numerals and written numbers.
"""


def roman_to_int(s):
    """
    Convert a Roman numeral string to an integer.
    
    Args:
        s (str): Roman numeral string (e.g., 'IV', 'IX', 'MCMXC')
        
    Returns:
        int: The integer value of the Roman numeral
        
    Examples:
        >>> roman_to_int('IV')
        4
        >>> roman_to_int('MCMXC')
        1990
    """
    if not s:
        return 0
        
    roman_numerals = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }
    
    total = 0
    prev_value = 0
    
    for char in reversed(s.upper()):
        if char not in roman_numerals:
            raise ValueError(f"Invalid Roman numeral character: {char}")
            
        curr_value = roman_numerals[char]
        if curr_value < prev_value:
            total -= curr_value
        else:
            total += curr_value
        prev_value = curr_value
        
    return total


def written_number_to_int(s):
    """
    Convert a written number word to an integer.
    
    Args:
        s (str): Written number word (e.g., 'one', 'two', 'ten')
        
    Returns:
        int: The integer value of the written number, or -1 if not found
        
    Examples:
        >>> written_number_to_int('five')
        5
        >>> written_number_to_int('invalid')
        -1
    """
    if not s:
        return -1
        
    written_numbers = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20
    }
    
    return written_numbers.get(s.lower(), -1)