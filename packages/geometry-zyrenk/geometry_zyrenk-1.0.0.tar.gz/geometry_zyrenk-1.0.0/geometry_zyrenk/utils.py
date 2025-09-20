import math

def validate_positive(*args):
    for arg in args:
        if arg <= 0:
            raise ValueError("جميع القيم يجب أن تكون موجبة")