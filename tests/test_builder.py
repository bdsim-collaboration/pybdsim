import pybdsim

def test_element_split_drift():
    c = pybdsim.Builder.Element('d1', 'drift', l=(0.4, 'm'), aper1=(2, 'cm'))
    b = c/2
    first = b[0]
    l = first.Length()
    assert(l == 0.2)

def test_element_split_sbend():
    c = pybdsim.Builder.Element('sb1', 'sbend', l=(0.4,'m'), angle=0.2)
    b = c/2
    first = b[0]
    l = first.Length()
    assert(l == 0.2)
    assert(first['angle'] == 0.1)


#test_element_split_sbend()
