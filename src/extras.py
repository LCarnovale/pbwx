from astropy import units as u

def parse_val(val, out_as=None, out_type=None, assume=None, rounding=False, round_digits=None):
    """ Parse a string written with units. 
    If `out_as=None` (default), then the quantity with units is returned.
    
    If `out_as` is set to a unit, then the value is converted into that unit.
    
    If `out_type` is provided, the output is, if possible, converted to that type.
    
    If `assume` is set, then that unit is assumed if none provided in the input.

    """
    
    q = u.Quantity(val)
    if str(q.unit) == "":
        q *= u.ns

    if type(out_as) is str:
        out_as = u.Unit(out_as)

    if out_as is not None:
        try:
            q = q.to(out_as).value
        except:
            raise ValueError("Output unit %s is not compatible with input unit %s" % (out_as, q.unit)) 

    if rounding:
        try:
            q = round(q, ndigits=round_digits)
        except:
            pass
    if out_type is not None:
        q = out_type(q)
    
    return q
