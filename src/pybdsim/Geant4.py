_processes = {
    "-1" : "fPrimary",
    "0" : "fNotDefined",
    "1" : "fTransportation",
    "2" : "fElectromagnetic",
    "3" : "fOptical",
    "4" : "fHadronic",
    "5" : "fPhotolepton_hadron",
    "6" : "fDecay",
    "7" : "fGeneral",
    "8" : "fParameterisation",
    "9" : "fUserDefined",
    "10" : "fParallel",
    "11" : "fPhonon",
    "12" : "fUCN"
}

_transportationProcesses = {
    "91" : "TRANSPORTATION",
    "92" : "COUPLED_TRANSPORTATION"
}

_electromagneticProcesses = {
    "1" : "fCoulombScattering",
    "2" : "fIonisation",
    "3" : "fBremsstrahlung",
    "4" : "fPairProdByCharged",
    "5" : "fAnnihilation",
    "6" : "fAnnihilationToMuMu",
    "7" : "fAnnihilationToHadrons",
    "8" : "fNuclearStopping",
    "10" : "fMultipleScattering",
    "11" : "fRayleigh",
    "12" : "fPhotoElectricEffect",
    "13" : "fComptonScattering",
    "14" : "fGammaConversion",
    "15" : "fGammaConversionToMuMu",
    "21" : "fCerenkov",
    "22" : "fScintillation",
    "23" : "fSynchrotronRadiation",
    "23" : "fTransitionRadiation"
}

_opticalProcesses = {
    "0" : "kCerenkov",
    "1" : "kScintillation",
    "2" : "kAbsorption",
    "3" : "kRayleigh",
    "4" : "kMieHG",
    "5" : "kBoundary",
    "6" : "kWLS",
    "7" : "kNoProcess"
}

_hadronicProcesses = {
    "111" : "fHadronElastic",
    "121" : "fHadronInelastic",
    "131" : "fCapture",
    "141" : "fFission",
    "151" : "fHadronAtRest",
    "152" : "fLeptonAtRest",
    "161" : "fChargeExchange",
    "210" : "fRadioactiveDecay"
}

_decayProcesses = {
    "201" : "DECAY",
    "202" : "DECAY_WithSpin",
    "203" : "DECAY_PionMakeSpin",
    "210" : "DECAY_Radioactive",
    "211" : "DECAY_Unknown",
    "231" : "DECAY_External"
}

_generalProcesses = {
    "401" : "STEP_LIMITER",
    "402" : "USER_SPECIAL_CUTS",
    "403" : "NEUTRON_KILLER"
}

_parallelProcesses = {
    "491" : "Parallel"
}

_notDefinedProcesses = {}
_photolepton_hadronProcesses = {}
_parameterisationProcesses = {}
_userDefinedProcesses = {}
_phononProcesses = {}
_uCNProcesses = {}

_subprocesses = [_notDefinedProcesses, _transportationProcesses, _electromagneticProcesses,
_opticalProcesses, _hadronicProcesses, _photolepton_hadronProcesses, _decayProcesses,
_generalProcesses, _parameterisationProcesses, _userDefinedProcesses, _parallelProcesses,
_phononProcesses, _uCNProcesses]

def GetProcess(processID):
    return _processes[str(processID)]

def GetSubProcess(processID, subprocessID):
    if processID == -1:
        return "PRIMARY"
    else:
        subprocess = _subprocesses[processID]
        if len(subprocess) == 0:
            return _processes[str(processID)]
        else:
            return subprocess[str(subprocessID)]