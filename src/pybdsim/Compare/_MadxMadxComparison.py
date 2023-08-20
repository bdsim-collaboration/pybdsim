

def MadxVsMadx(first, second, first_name=None,
               second_name=None, **kwargs):
    """
    Display all the optical function plots for the two input optics files.
    """
    import pymadx as _pymadx
    _pymadx.Compare.MadxVsMadx(first, second, first_name, second_name, **kwargs)
