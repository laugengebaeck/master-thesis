from yaramo.signal import Signal, SignalFunction

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

def parse_signal_column(df: pd.DataFrame, col_idx: int) -> Signal:
    # var signal = Signal()
    # TODO: wo kriegen wir Richtung relativ zur jeweiligen Edge her?
    pass
