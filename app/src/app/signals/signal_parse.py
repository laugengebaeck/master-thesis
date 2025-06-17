from typing import Set
from yaramo.signal import Signal, SignalFunction, SignalState

import pandas as pd

def get_signal_function(signal_name: str):
    # TODO Logik deckt noch nicht alle Fälle ab
    short_name = signal_name[1:] if signal_name[1].isalpha() else signal_name[2:]
    if short_name[0] == "V":
        return SignalFunction.Vorsignal_Vorsignalwiederholer
    elif short_name[0] == "Z":
        return SignalFunction.Zwischen_Signal
    elif short_name[0] == "L":
        # TODO wie Sperrsignale in Yaramo abbilden?
        return SignalFunction.andere
    elif short_name[0] in ["N", "P", "O", "Q"]:
        return SignalFunction.Ausfahr_Signal
    elif short_name[0] in ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]:
        return SignalFunction.Einfahr_Signal
    else:
        return SignalFunction.andere
    
def get_signal_states(df: pd.DataFrame, col: int) -> Set[SignalState]:
    states = set()

    hp0_cell = df.iat[20, col]
    if not pd.isna(hp0_cell) and str(hp0_cell) == "0":
        states.add(SignalState.HP0)
    
    ks_cell = df.iat[21, col]
    if not pd.isna(ks_cell):
        if "1" in str(ks_cell):
            states.add(SignalState.KS1)
        if "2" in str(ks_cell):
            states.add(SignalState.KS2)

    ra_sh_cell = df.iat[22, col]
    if not pd.isna(ra_sh_cell):
        # DV-Ra12 entspricht DS-Sh1
        if "Ra12" in str(ra_sh_cell):
            states.add(SignalState.RA12)
        if "Sh1" in str(ra_sh_cell):
            states.add(SignalState.SH1)
        # TODO weitere Signale?

    zs1_zs7_cell = df.iat[25, col]
    if not pd.isna(zs1_zs7_cell):
        zs_str = str(zs1_zs7_cell)
        if "1" in zs_str and "7" in zs_str:
            raise ValueError("Zs1 and Zs2 should not occur together")
        elif "1" in zs_str:
            states.add(SignalState.ZS1)
        elif "7" in zs_str:
            # TODO yaramo doesn't know Zs7
            pass

    zs2_cell = df.iat[16, col]
    if not pd.isna(zs2_cell):
        states.add(SignalState.ZS2)
    # TODO Kennbuchstaben auslesen

    zs2v_cell = df.iat[17, col]
    if not pd.isna(zs2v_cell):
        states.add(SignalState.ZS2V)
    # TODO Kennbuchstaben auslesen

    zs3_cell = df.iat[18, col]
    if not pd.isna(zs3_cell):
        states.add(SignalState.ZS3)
    # TODO Kennziffern auslesen

    zs3v_cell = df.iat[19, col]
    if not pd.isna(zs3v_cell):
        states.add(SignalState.ZS3V)
    # TODO Kennziffern auslesen

    mastschild_cell = df.iat[32, col]
    if not pd.isna(mastschild_cell):
        if "H" in str(mastschild_cell):
            states.add(SignalState.MS_WS_RT_WS)
        if "V" in str(mastschild_cell):
            states.add(SignalState.MS_GE_D)
        if "Sp" in str(mastschild_cell):
            # TODO yaramo kann Mastschild "weiß mit zwei schwarzen Punkten" noch nicht
            pass

    vorsignaltafel_cell = df.iat[33, col]
    if not pd.isna(vorsignaltafel_cell):
        states.add(SignalState.NE2)

    return states



def parse_signal_column(df: pd.DataFrame, col_idx: int) -> Signal:
    # var signal = Signal()
    # TODO: wo kriegen wir Richtung relativ zur jeweiligen Edge her?
    pass
