PDGid = {
    2212  : ('Proton','p'),
    -2212 : ('Antiproton',r'\={p}'),
    2112  : ('Neutrom','n'),
    11    : ('Electron',r'e^{-}'),
    -11   : ('Positron',r'e^{+}'),
    22    : ('Photon',r'\gamma'),
    12    : ('Electron Neutrino',r'\nu_{e}'),
    -12   : ('Electron Antineutrino',r'\=\nu_{e}'),
    -13   : ('Positive Muon',r'\mu^{+}'),
    13    : ('Negative Muon',r'\mu^{-}')
}

PDGname = {}
for k,v in PDGid.iteritems():
    PDGname[v[0]] = k
    PDGname[v[0].lower()] = k

def GetPDGInd(particlename):
    if particlename in PDGname:
        return PDGname[particlename]
    elif particlename.lower() in PDGname:
        return PDGname[particlename.lower()]
    else:
        raise ValueError("Unknown particle type")
