import logging

import pandas as pd
from yaramo.additional_signal import (
    AdditionalSignalZs2,
    AdditionalSignalZs2v,
    AdditionalSignalZs3,
    AdditionalSignalZs3Type,
    AdditionalSignalZs3v,
)
from yaramo.edge import Edge
from yaramo.node import Node
from yaramo.signal import (
    AdditionalSignal,
    Signal,
    SignalDirection,
    SignalFunction,
    SignalKind,
    SignalState,
    SignalSystem,
)


# splits in classification number and short name
def split_signal_name(signal_name: str) -> tuple[str, str]:
    if signal_name[1].isalpha():
        return signal_name[:1], signal_name[1:]
    else:
        return signal_name[:2], signal_name[2:]


# uses short signal name (without classification number)
def get_signal_function(signal_name: str):
    # TODO Logik deckt noch nicht alle Fälle ab
    if signal_name[0] == "V":
        return SignalFunction.Vorsignal_Vorsignalwiederholer
    elif (
        signal_name[0] == "Z"
        and signal_name[1] in ["R", "S", "T", "U", "V", "W"]
        and signal_name[2:].isdigit()
    ):
        return SignalFunction.Zwischen_Signal
    elif signal_name[0] == "L":
        # Sperrsignale grundsaetzlich "andere", außer wenn Ziel einer Zugfahrt
        # TODO Zugziel-Eigenschaft muesste man mittels Fahrstrassentabelle anreichern
        return SignalFunction.andere
    elif signal_name[0] in ["N", "P", "O", "Q"] and signal_name[1:].isdigit():
        return SignalFunction.Ausfahr_Signal
    elif signal_name[0] in ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"] and (
        len(signal_name) == 1 or (len(signal_name) == 2 and signal_name[0] == signal_name[1])
    ):
        return SignalFunction.Einfahr_Signal
    elif signal_name.isdigit():
        return SignalFunction.Block_Signal
    else:
        return SignalFunction.andere


def get_signal_kind(df: pd.DataFrame, col: int) -> SignalKind:
    hp0_cell = df.iat[20, col]
    ks_cell = df.iat[21, col]
    ra_sh_cell = df.iat[22, col]

    is_main_signal = (
        not pd.isna(hp0_cell) and not pd.isna(ks_cell) and "0" in str(hp0_cell)
    )  # Hp0 + mindestens 1 Ks = Hauptsignal
    is_distant_signal = not pd.isna(ks_cell) and "2" in str(
        ks_cell
    )  # Ks2 nur wenn Vorsignalfunktion
    is_shunting_signal = not pd.isna(ra_sh_cell)

    if is_main_signal:
        if is_distant_signal:
            return SignalKind.Mehrabschnittssignal
        if is_shunting_signal:
            return SignalKind.Hauptsperrsignal
        return SignalKind.Hauptsignal
    elif is_distant_signal:
        name_cell = df.iat[0, col]
        if not pd.isna(name_cell) and "VW" in str(name_cell):
            return SignalKind.Vorsignalwiederholer
        else:
            return SignalKind.Vorsignal
    elif is_shunting_signal:
        return SignalKind.Sperrsignal

    return SignalKind.andere


def get_signal_states(df: pd.DataFrame, col: int, signal_name: str) -> set[SignalState]:
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

    zs_signal_strings = []
    zs_rows = [25, 26, 27]
    for row in zs_rows:
        if not pd.isna(df.iat[row, col]):
            for zs in str(df.iat[row, col]).split(","):
                zs_signal_strings.append(zs.strip())

    if "1" in zs_signal_strings and "7" in zs_signal_strings:
        logging.warning(f"column {col}: Zs1 and Zs7 should not occur together")

    for zs in zs_signal_strings:
        if "1" in zs_signal_strings:
            states.add(SignalState.ZS1)
        elif "6" in zs_signal_strings:
            states.add(SignalState.ZS6)
        elif "7" in zs_signal_strings:
            states.add(SignalState.ZS7)
        elif "13" in zs_signal_strings:
            states.add(SignalState.ZS13)

    zs2_cell = df.iat[16, col]
    if not pd.isna(zs2_cell):
        states.add(SignalState.ZS2)

    zs2v_cell = df.iat[17, col]
    if not pd.isna(zs2v_cell):
        states.add(SignalState.ZS2V)

    zs3_cell = df.iat[18, col]
    if not pd.isna(zs3_cell):
        states.add(SignalState.ZS3)

    zs3v_cell = df.iat[19, col]
    if not pd.isna(zs3v_cell):
        states.add(SignalState.ZS3V)

    kl_zl_cell = df.iat[24, col]
    if not pd.isna(kl_zl_cell):
        kl_zl_str = str(kl_zl_cell)
        is_wiederholer = signal_name.upper().startswith("VW")
        if "Kl" in kl_zl_str:
            states.add(SignalState.KL)
        if "Zl" in kl_zl_str:
            states.add(SignalState.ZLU if is_wiederholer else SignalState.ZLO)

    mastschild_cell = df.iat[32, col]
    if not pd.isna(mastschild_cell):
        if "H" in str(mastschild_cell):
            states.add(SignalState.MS_WS_RT_WS)
        if "V" in str(mastschild_cell):
            states.add(SignalState.MS_GE_D)
        if "Sp" in str(mastschild_cell):
            # TODO im DS-Bereich wsl. inkorrekt -> stattdessen WS_RT_WS
            states.add(SignalState.MS_WS_2SWP)

    vorsignaltafel_cell = df.iat[33, col]
    if not pd.isna(vorsignaltafel_cell):
        states.add(SignalState.NE2)

    return states


def cell_to_zs3_symbols(cell_content: str) -> list[AdditionalSignalZs3.AdditionalSignalSymbolZs3]:
    zs3_symbols = []
    for number_str in cell_content.split(","):
        # form Zs3 handled elsewhere
        number_str = number_str.replace(" ", "").removesuffix("F")
        number = int(number_str)
        if number > 16:
            # if the OCR obviously missed commas, we assume each char is its own Zs3 value
            # TODO this fails if one of the actual values is 10-16, or if the OCR erroneously grouped this cell with the next one
            for part_number in number_str:
                zs3_symbols.append(AdditionalSignalZs3.AdditionalSignalSymbolZs3(int(part_number)))
        else:
            zs3_symbols.append(AdditionalSignalZs3.AdditionalSignalSymbolZs3(number))
    return zs3_symbols


def cell_to_zs2_symbols(cell_content: str) -> list[AdditionalSignalZs2.AdditionalSignalSymbolZs2]:
    is_valid_symbol = (
        lambda letter: len(
            list(
                filter(
                    lambda enum: enum.value == letter, AdditionalSignalZs2.AdditionalSignalSymbolZs2
                )
            )
        )
        != 0
    )
    return [
        AdditionalSignalZs2.AdditionalSignalSymbolZs2(letter.strip())
        for letter in cell_content.split(",")
        if is_valid_symbol(letter)
    ]


def get_additional_signals(df: pd.DataFrame, col: int) -> list[AdditionalSignal]:
    add_signals = []

    zs2_cell = df.iat[16, col]
    if not pd.isna(zs2_cell):
        add_signals.append(AdditionalSignalZs2(cell_to_zs2_symbols(str(zs2_cell))))

    zs2v_cell = df.iat[17, col]
    if not pd.isna(zs2v_cell):
        add_signals.append(AdditionalSignalZs2v(cell_to_zs2_symbols(str(zs2v_cell))))

    zs3_cell = df.iat[18, col]
    if not pd.isna(zs3_cell):
        zs3_type = (
            AdditionalSignalZs3Type.FORM_SIGNAL
            if "F" in str(zs3_cell)
            else AdditionalSignalZs3Type.LIGHT_SIGNAL
        )
        add_signals.append(AdditionalSignalZs3(cell_to_zs3_symbols(str(zs3_cell)), type=zs3_type))

    zs3v_cell = df.iat[19, col]
    if not pd.isna(zs3v_cell):
        zs3v_type = (
            AdditionalSignalZs3Type.FORM_SIGNAL
            if "F" in str(zs3v_cell)
            else AdditionalSignalZs3Type.LIGHT_SIGNAL
        )
        add_signals.append(
            AdditionalSignalZs3v(cell_to_zs3_symbols(str(zs3v_cell)), type=zs3v_type)
        )

    # TODO Zs1, Zs6, Zs7, Zs13
    # TODO 6F is also possible

    return add_signals


def get_side_distance(df: pd.DataFrame, col: int) -> int | None:
    distance_left_cell = df.iat[36, col]
    distance_right_cell = df.iat[37, col]

    # TODO Was, wenn beide Zahlen dastehen?
    if not pd.isna(distance_left_cell):
        if not str(distance_left_cell).isdigit():
            logging.warning(f"column {col}: Wrong row was chosen for side distance (TODO).")
        else:
            return -1 * int(str(distance_left_cell))
    elif not pd.isna(distance_right_cell):
        if not str(distance_right_cell).isdigit():
            logging.warning(f"column {col}: Wrong row was chosen for side distance (TODO).")
        else:
            return int(str(distance_right_cell))
    else:
        logging.warning(f"column {col}: No side distance for signal given")

    return None


def parse_signal_column(df: pd.DataFrame, col: int) -> Signal | None:
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
        logging.warning(f"column {col}: Column contains no signal name")
        return None

    classification_number, signal_name = split_signal_name(full_signal_name)

    signal = Signal(
        name=signal_name,
        edge=Edge(Node(), Node()),  # TODO fill later
        distance_edge=42,  # TODO fill later
        direction=SignalDirection.IN,  # TODO fill later
        function=get_signal_function(signal_name),
        kind=get_signal_kind(df, col),
        system=SignalSystem.Ks,
        side_distance=get_side_distance(df, col),  # type: ignore
        supported_states=get_signal_states(df, col, signal_name),
        classification_number=classification_number,
    )

    signal.additional_signals = get_additional_signals(df, col)
    return signal
