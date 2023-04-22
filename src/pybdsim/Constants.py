PDGind = {
    0     : ('Total',                 'Total'),
#COMMON
    2212  : ('Proton',                'p'),
    -2212 : ('Antiproton',            r'$\overline{p}$'),
    2112  : ('Neutron',               'n'),
    -2112 : ('AntiNeutron',           r'$\overline{n}$'),
    11    : ('Electron',              r'$e^{-}$'),
    -11   : ('Positron',              r'$e^{+}$'),
    22    : ('Photon',                r'$\gamma$'),
    12    : ('Electron Neutrino',     r'$\nu_{e}$'),
    -12   : ('Electron Antineutrino', r'$\overline\nu_{e}$'),
    13    : ('Muon',                  r'$\mu^{-}$'),
    -13   : ('Antimuon',              r'$\mu^{+}$'),
    14    : ('Muon Neutrino',         r'$\nu_{\mu}$'),
    -14   : ('Muon Antineutrino',     r'$\overline\nu_{\mu}$'),
    15    : ('Tau',                   r'$\tau^{-}$'),
    -15   : ('Anti Tau',              r'$\tau^{+}$'),
    16    : ('Tau Neutrino',          r'$\nu_{\tau}$'),
    -16   : ('Tau Antineutrino ',     r'$\overline\nu_{\tau}$'),
#LIGHT MESONS
    111   : ('Pion0',                 r'$\pi^{0}$'),
    211   : ('Pion+',                 r'$\pi^{+}$'),
    -211  : ('Pion-',                 r'$\pi^{-}$'),
#STRANGE MESONS
    321   : ('Kaon+',                 r'$K^{+}$'),
    -321  : ('Kaon-',                 r'$K^{-}$'),
    130   : ('K-Long',                r'$K_{L}^{0}$'),
    310   : ('K-Short',               r'$K_{S}^{0}$'),
#STRANGE BARYONS
    3122  : ('Lambda',                r'$\Lambda$'),
    -3122 : ('Anti Lambda',           r'$\overline{\Lambda}$'),
    3222  : ('Sigma+',                r'$\Sigma^{+}$'),
    -3222 : ('Anti Sigma+',           r'$\overline{\Sigma^{+}}$'),
    3212  : ('Sigma0',                r'$\Sigma^{0}$'),
    3112  : ('Sigma-',                r'$\Sigma^{-}$'),
    -3112 : ('Anti Sigma-',           r'$\overline{\Sigma^{-}}$'),
    3322  : ('Xi0',                   r'$\Xi^{0}$'),
    -3322 : ('Anti Xi0',              r'$\overline{\Xi^{0}}$'),
    3312  : ('Xi-',                   r'$\Xi^{-}$'),
    -3312 : ('Anti Xi-',              r'$\overline{\Xi^{-}}$')
}

PDGname = {}
for k,v in list(PDGind.items()):
    PDGname[v[0]] = k
    PDGname[v[0].lower()] = k
del k,v

def GetPDGInd(particlename):
    if particlename in PDGname:
        return PDGname[particlename]
    elif particlename.lower() in PDGname:
        return PDGname[particlename.lower()]
    else:
        raise ValueError("Unknown particle type")

def GetPDGName(particleid):
    try:
        return PDGind[particleid]
    except KeyError:
        print('Unknown particle id ',particleid)
        return ('','')
