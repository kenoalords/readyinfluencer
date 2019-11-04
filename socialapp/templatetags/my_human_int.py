from django import template
import numpy as np

register = template.Library()

def normalize_int(value):
    value = int(value)
    if value > 1000 and value < 1000000:
        return  '%sK' % (str(np.round( value/1000, 2 )))

    if value > 1000000 and value < 1000000000:
        return '%sM' % (str(np.round( value/1000000, 2 )))

    if value > 1000000000:
        return '%sB' % (str(np.round( value/1000000000, 2 )))

    return value

register.filter('normalize_int', normalize_int)
