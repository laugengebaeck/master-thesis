from typing import List, Set, Tuple
from yaramo.signal import Signal, SignalDirection, SignalFunction, SignalKind, SignalState, SignalSystem, AdditionalSignal
from yaramo.additional_signal import AdditionalSignalZs2, AdditionalSignalZs2v, AdditionalSignalZs3, AdditionalSignalZs3v

import pandas as pd

# splits in classification number nad short name
def split_signal_name(signal_name: str) -> Tuple[str, str]:
    if signal_name[1].isalpha():
        return signal_name[:1], signal_name[1:]
    else:
        return signal_name[:2], signal_name[2:]

# uses short signal name (without classification number)
def get_signal_function(signal_name: str):
    # TODO Logik deckt noch nicht alle Fälle ab
    if signal_name[0] == "V":
        return SignalFunction.Vorsignal_Vorsignalwiederholer
    elif signal_name[0] == "Z":
        return SignalFunction.Zwischen_Signal
    elif signal_name[0] == "L":
        # TODO wie Sperrsignale in Yaramo abbilden?
        return SignalFunction.andere
    elif signal_name[0] in ["N", "P", "O", "Q"]:
        return SignalFunction.Ausfahr_Signal
    elif signal_name[0] in ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]:
        return SignalFunction.Einfahr_Signal
    else:
        return SignalFunction.andere
    
def get_signal_kind(df: pd.DataFrame, col: int) -> SignalKind:
    hp0_cell = df.iat[20, col]
    ks_cell = df.iat[21, col]
    ra_sh_cell = df.iat[22, col]

    is_main_signal = not pd.isna(hp0_cell) and "0" in str(hp0_cell) # Hp0 nur wenn Hauptsignalfunktion
    is_distant_signal = not pd.isna(ks_cell) and "2" in str(ks_cell) # Ks2 nur wenn Vorsignalfunktion
    is_shunting_signal = not pd.isna(ra_sh_cell)

    if is_main_signal:
        if is_distant_signal:
            return SignalKind.Mehrabschnittssignal
        if is_shunting_signal:
            return SignalKind.Hauptsperrsignal
    elif is_distant_signal:
        name_cell = df.iat[0, col]
        if not pd.isna(name_cell) and "VW" in str(name_cell):
            return SignalKind.Vorsignalwiederholer
        else:
            return SignalKind.Vorsignal
    elif is_shunting_signal:
        return SignalKind.Sperrsignal
    
    return SignalKind.andere
        
    
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

def cell_to_zs3_symbols(cell_content: str) -> List[AdditionalSignalZs3.AdditionalSignalSymbolZs3]:
    zs3_symbols = []
    for number in cell_content.split(","):
        # TODO yaramo kann Form-Zs3 nicht extra angeben
        number = int(number.strip().removesuffix("F"))
        zs3_symbols.append(AdditionalSignalZs3.AdditionalSignalSymbolZs3.from_number(number))
    return zs3_symbols

def cell_to_zs2_symbols(cell_content: str) -> List[AdditionalSignalZs2.AdditionalSignalSymbolZs2]:
    # TODO Was bei Buchstaben, die nicht als Zs2 existieren?
    return [AdditionalSignalZs2.AdditionalSignalSymbolZs2(letter.strip()) for letter in cell_content.split(",")]


def get_additional_signals(df: pd.DataFrame, col: int) -> List[AdditionalSignal]:
    add_signals = []

    zs2_cell = df.iat[16, col]
    if not pd.isna(zs2_cell):
        add_signals.append(AdditionalSignalZs2(cell_to_zs2_symbols(str(zs2_cell))))

    zs2v_cell = df.iat[17, col]
    if not pd.isna(zs2v_cell):
        add_signals.append(AdditionalSignalZs2v(cell_to_zs2_symbols(str(zs2v_cell))))

    zs3_cell = df.iat[18, col]
    if not pd.isna(zs3_cell):
        add_signals.append(AdditionalSignalZs3(cell_to_zs3_symbols(str(zs3_cell))))

    zs3v_cell = df.iat[19, col]
    if not pd.isna(zs3v_cell):
        add_signals.append(AdditionalSignalZs3v(cell_to_zs3_symbols(str(zs3v_cell))))

    # TODO Zs1?

    return add_signals

def get_side_distance(df: pd.DataFrame, col: int) -> int:
    distance_left_cell = df.iat[37, col]
    distance_right_cell = df.iat[38, col]

    # TODO Was, wenn beide Zahlen dastehen?
    if not pd.isna(distance_left_cell):
        return -1 * int(str(distance_left_cell))
    elif not pd.isna(distance_right_cell):
        return int(str(distance_right_cell))
    else:
        raise ValueError("No side distance for signal given")


def parse_signal_column(df: pd.DataFrame, col: int) -> Signal:
    main_signal_cell = df.iat[0, col]
    shunting_signal_cell = df.iat[1, col]
    misc_signal_cell = df.iat[2, col]
    
    full_signal_name = ""
    if not pd.isna(main_signal_cell):
        full_signal_name = str(main_signal_cell)
    elif not pd.isna(shunting_signal_cell):
        full_signal_name = str(shunting_signal_cell)
    elif not pd.isna(misc_signal_cell):
        full_signal_name = str(misc_signal_cell)
    else:
        raise ValueError("Column contains no signal name")

    classification_number, signal_name = split_signal_name(full_signal_name)

    signal = Signal(
        name = signal_name,
        edge = Edge(), # TODO
        distance_edge = 42, # TODO
        direction =  SignalDirection.IN, # TODO
        function = get_signal_function(signal_name),
        kind = get_signal_kind(df, col),
        system = SignalSystem.Ks,
        side_distance = get_side_distance(df, col),
        supported_states = get_signal_states(df, col),
        classification_number = classification_number,
    )

    signal.additional_signals = get_additional_signals(df, col)
    return signal
