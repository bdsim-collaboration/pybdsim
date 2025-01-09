import pybdsim


def test_element_split():
    c = pybdsim.Builder.Element('sb1', 'sbend', l=(0.4,'m'), angle=0.2)
    b = c/2
    assert(len(b) == 0.2)



#if __name__ == "__main__":
#    test_element_split()
