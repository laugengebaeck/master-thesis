import logging

import pandas as pd
from table_plans.parsers.row_mapping import get_row_number_for_attribute
from yaramo.additional_signal import (
    AdditionalSignalZs1,
    AdditionalSignalZs2,
    AdditionalSignalZs2v,
    AdditionalSignalZs3,
    AdditionalSignalZs3Type,
    AdditionalSignalZs3v,
    AdditionalSignalZs6,
    AdditionalSignalZs7,
    AdditionalSignalZs13,
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


# TODO fuer O, Q Richtung nicht ableitbar
def get_signal_direction(signal_name: str) -> SignalDirection:
    signal_name = signal_name.upper()
    if len(signal_name) <= 2 and signal_name[0] in [
        "A",
        "B",
        "C",
        "D",
        "E",
    ]:  # Esig in km-Richtung (auch Gegengleis)
        return SignalDirection.IN
    elif len(signal_name) <= 2 and signal_name[0] in [
        "F",
        "G",
        "H",
        "J",
        "K",
    ]:  # Esig entgegen km-Richtung (auch Gegengleis)
        return SignalDirection.GEGEN
    elif signal_name[0] == "N":  # Asig in km-Richtung
        return SignalDirection.IN
    elif signal_name[0] == "P":
        return SignalDirection.GEGEN  # Asig entgegen km-Richtung
    elif len(signal_name) >= 2 and signal_name[0] == "Z":
        if signal_name[1] in ["R", "S", "T"]:  # Zsig in km-Richtung
            return SignalDirection.IN
        elif signal_name[1] in ["U", "V", "W"]:  # Zsig gegen km-Richtung
            return SignalDirection.GEGEN
    elif signal_name.isdigit():
        if int(signal_name) % 2 == 1:  # Bksig in km-Richtung
            return SignalDirection.IN
        else:  # Bksig entgegen km-Richtung
            return SignalDirection.GEGEN
    elif signal_name.startswith("VW"):  # VSigWdh, Richtung entsprechend zugehörigem Hauptsignal
        return get_signal_direction(signal_name[2:])
    elif signal_name.startswith("V"):  # VSig, Richtung entsprechend zugehörigem Hauptsignal
        return get_signal_direction(signal_name[1:])
    elif signal_name.endswith("X"):  # Sperrsig in km-Richtung
        return SignalDirection.IN
    elif signal_name.endswith("Y"):  # Sperrsig entgegen km-Richtung
        return SignalDirection.GEGEN

    logging.warning(
        f"Not able to extract signal direction from name for signal {signal_name}, assuming SignalDirection.IN"
    )
    return SignalDirection.IN


def get_signal_kind(df: pd.DataFrame, col: int, table_id: int) -> SignalKind:
    hp0_cell = df.iat[get_row_number_for_attribute(df, "Signalbegriff Hp", table_id), col]
    ks_cell = df.iat[get_row_number_for_attribute(df, "Signalbegriff Ks", table_id), col]
    ra_sh_cell = df.iat[get_row_number_for_attribute(df, "Signalbegriff Ra / Sh", table_id), col]

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


def get_zs_signal_strings(df: pd.DataFrame, col: int, table_id: int) -> list[str]:
    zs_rows = [
        get_row_number_for_attribute(df, "Signalbegriffe Zs (im Schirm)", table_id),
        get_row_number_for_attribute(df, "Zs am Signalmast", table_id),
        get_row_number_for_attribute(df, "Zs am Betonpfosten/Rohrmast (separat)", table_id),
    ]
    zs_signal_strings = []
    for row in zs_rows:
        if not pd.isna(df.iat[row, col]):
            for zs in str(df.iat[row, col]).split(","):
                zs_signal_strings.append(zs.strip())
    return zs_signal_strings


def get_signal_states(
    df: pd.DataFrame, col: int, signal_name: str, table_id: int
) -> set[SignalState]:
    states = set()

    hp0_cell = df.iat[get_row_number_for_attribute(df, "Signalbegriff Hp", table_id), col]
    if not pd.isna(hp0_cell) and str(hp0_cell) == "0":
        states.add(SignalState.HP0)

    ks_cell = df.iat[get_row_number_for_attribute(df, "Signalbegriff Ks", table_id), col]
    if not pd.isna(ks_cell):
        if "1" in str(ks_cell):
            states.add(SignalState.KS1)
        if "2" in str(ks_cell):
            states.add(SignalState.KS2)

    ra_sh_cell = df.iat[get_row_number_for_attribute(df, "Signalbegriff Ra / Sh", table_id), col]
    if not pd.isna(ra_sh_cell):
        # DV-Ra12 entspricht DS-Sh1
        if "Ra12" in str(ra_sh_cell):
            states.add(SignalState.RA12)
        if "Sh1" in str(ra_sh_cell):
            states.add(SignalState.SH1)

    zs_signal_strings = get_zs_signal_strings(df, col, table_id)

    if "1" in zs_signal_strings and "7" in zs_signal_strings:
        logging.warning(f"column {col}: Zs1 and Zs7 should not occur together")

    for zs in zs_signal_strings:
        if zs == "1":
            states.add(SignalState.ZS1)
        elif zs == "6" or zs == "6F":
            states.add(SignalState.ZS6)
        elif zs == "7":
            states.add(SignalState.ZS7)
        elif zs == "13":
            states.add(SignalState.ZS13)

    zs2_cell = df.iat[get_row_number_for_attribute(df, "Richtungsanzeiger", table_id), col]
    if not pd.isna(zs2_cell):
        states.add(SignalState.ZS2)

    zs2v_cell = df.iat[get_row_number_for_attribute(df, "Richtungsvoranzeiger", table_id), col]
    if not pd.isna(zs2v_cell):
        states.add(SignalState.ZS2V)

    zs3_cell = df.iat[
        get_row_number_for_attribute(df, "Geschwindigkeitsanzeiger 6)", table_id), col
    ]
    if not pd.isna(zs3_cell):
        states.add(SignalState.ZS3)

    zs3v_cell = df.iat[
        get_row_number_for_attribute(df, "Geschwindigkeitsvoranzeiger 6)", table_id), col
    ]
    if not pd.isna(zs3v_cell):
        states.add(SignalState.ZS3V)

    kl_zl_cell = df.iat[get_row_number_for_attribute(df, "Kenn- / Zusatzlicht", table_id), col]
    if not pd.isna(kl_zl_cell):
        kl_zl_str = str(kl_zl_cell)
        is_wiederholer = signal_name.upper().startswith("VW")
        if "Kl" in kl_zl_str:
            states.add(SignalState.KL)
        if "Zl" in kl_zl_str:
            states.add(SignalState.ZLU if is_wiederholer else SignalState.ZLO)

    mastschild_cell = df.iat[get_row_number_for_attribute(df, "Mastschild", table_id), col]
    if not pd.isna(mastschild_cell):
        if "H" in str(mastschild_cell):
            states.add(SignalState.MS_WS_RT_WS)
        if "V" in str(mastschild_cell):
            states.add(SignalState.MS_GE_D)
        if "Sp" in str(mastschild_cell):
            # TODO im DS-Bereich wsl. inkorrekt -> stattdessen WS_RT_WS
            states.add(SignalState.MS_WS_2SWP)

    vorsignaltafel_cell = df.iat[
        get_row_number_for_attribute(df, "Vorsignaltafel Rz S525.4.5 Bild Nr.", table_id), col
    ]
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


def get_additional_signals(df: pd.DataFrame, col: int, table_id: int) -> list[AdditionalSignal]:
    add_signals = []

    zs2_cell = df.iat[get_row_number_for_attribute(df, "Richtungsanzeiger", table_id), col]
    if not pd.isna(zs2_cell):
        add_signals.append(AdditionalSignalZs2(cell_to_zs2_symbols(str(zs2_cell))))

    zs2v_cell = df.iat[get_row_number_for_attribute(df, "Richtungsvoranzeiger", table_id), col]
    if not pd.isna(zs2v_cell):
        add_signals.append(AdditionalSignalZs2v(cell_to_zs2_symbols(str(zs2v_cell))))

    zs3_cell = df.iat[
        get_row_number_for_attribute(df, "Geschwindigkeitsanzeiger 6)", table_id), col
    ]
    if not pd.isna(zs3_cell):
        zs3_type = (
            AdditionalSignalZs3Type.FORM_SIGNAL
            if "F" in str(zs3_cell)
            else AdditionalSignalZs3Type.LIGHT_SIGNAL
        )
        add_signals.append(AdditionalSignalZs3(cell_to_zs3_symbols(str(zs3_cell)), type=zs3_type))

    zs3v_cell = df.iat[
        get_row_number_for_attribute(df, "Geschwindigkeitsvoranzeiger 6)", table_id), col
    ]
    if not pd.isna(zs3v_cell):
        zs3v_type = (
            AdditionalSignalZs3Type.FORM_SIGNAL
            if "F" in str(zs3v_cell)
            else AdditionalSignalZs3Type.LIGHT_SIGNAL
        )
        add_signals.append(
            AdditionalSignalZs3v(cell_to_zs3_symbols(str(zs3v_cell)), type=zs3v_type)
        )

    zs_signal_strings = get_zs_signal_strings(df, col, table_id)

    for zs in zs_signal_strings:
        if zs == "1":
            add_signals.append(
                AdditionalSignalZs1([AdditionalSignalZs1.AdditionalSignalSymbolZs1.Zs1])
            )
        elif zs == "6" or zs == "6F":
            # TODO handle 6F correctly later
            add_signals.append(
                AdditionalSignalZs6([AdditionalSignalZs6.AdditionalSignalSymbolZs6.Zs6])
            )
        elif zs == "7":
            add_signals.append(
                AdditionalSignalZs7([AdditionalSignalZs7.AdditionalSignalSymbolZs7.Zs7])
            )
        elif zs == "13":
            add_signals.append(
                AdditionalSignalZs13([AdditionalSignalZs13.AdditionalSignalSymbolZs13.Zs13])
            )

    return add_signals


def get_side_distance(df: pd.DataFrame, col: int, table_id: int) -> int | None:
    distance_left_row = get_row_number_for_attribute(
        df, "Abstände zu Gleismitte von Mastmitte [mm] 2) links rechts", table_id
    )
    distance_left_cell = df.iat[distance_left_row, col]
    distance_right_cell = df.iat[distance_left_row + 1, col]

    # if both distances are given, use left one for now (heuristic: signal probably belongs to track left of it)
    if not pd.isna(distance_left_cell):
        if not str(distance_left_cell).isdigit():
            logging.warning(f"column {col}: Wrong row was chosen for side distance.")
        else:
            return -1 * int(str(distance_left_cell))
    elif not pd.isna(distance_right_cell):
        if not str(distance_right_cell).isdigit():
            logging.warning(f"column {col}: Wrong row was chosen for side distance.")
        else:
            return int(str(distance_right_cell))
    else:
        logging.warning(f"column {col}: No side distance for signal given")

    return None


def parse_signal_column(df: pd.DataFrame, col: int, table_id: int) -> Signal | None:
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
    print(signal_name)

    signal = Signal(
        name=signal_name,
        edge=Edge(Node(), Node()),  # TODO fill later
        distance_edge=42,  # TODO fill later
        direction=get_signal_direction(signal_name),
        function=get_signal_function(signal_name),
        kind=get_signal_kind(df, col, table_id),
        system=SignalSystem.Ks,
        side_distance=get_side_distance(df, col, table_id),  # type: ignore
        supported_states=get_signal_states(df, col, signal_name, table_id),
        classification_number=classification_number,
    )

    signal.additional_signals = get_additional_signals(df, col, table_id)
    return signal
