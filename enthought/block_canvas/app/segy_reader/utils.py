""" Helper functions for segy reader
"""


def ibm2ieee(ibm):
    """ Converts an IBM floating number to IEEE format
    """

    sign, exponent = ibm >> 31 & 0x01, ibm >> 24 & 0x7f

    mantissa = ibm & 0x00ffffff
    mantissa = (mantissa*1.0)/pow(2, 24)

    return (1-2*sign)*mantissa*pow(16.0, exponent-64)


### EOF -----------------------------------------------------------------------
