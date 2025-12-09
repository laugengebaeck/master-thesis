import pandas as pd
from table_plans.parsers.signals import parse_signal_column
from table_plans.validation.validator import TableValidator


def handle_az_plan(tables: list[pd.DataFrame]):
    pass


def handle_dweg_plan(tables: list[pd.DataFrame]):
    pass


def handle_flank_plan(tables: list[pd.DataFrame]):
    pass


def handle_gm_plan(tables: list[pd.DataFrame]):
    pass


def handle_gp_plan(tables: list[pd.DataFrame]):
    pass


def handle_rang_plan(tables: list[pd.DataFrame]):
    pass


def handle_sb_plan(tables: list[pd.DataFrame]):
    pass


def handle_sig1_plan(tables: list[pd.DataFrame]):
    print("Processing Signaltabelle 1...")
    validator = TableValidator()
    for i, table in enumerate(tables):
        signals = [parse_signal_column(table, col, i) for col in range(3, table.shape[1])]
        signals = [signal for signal in signals if signal is not None]
        print(f"Processed page {i+1}.")
        for signal in signals:
            print(signal.to_json())
        validator.check(signals, table)


def handle_sig2_plan(tables: list[pd.DataFrame]):
    pass


def handle_wei_plan(tables: list[pd.DataFrame]):
    pass


def handle_zug_plan(tables: list[pd.DataFrame]):
    pass


def handle_zwie_plan(tables: list[pd.DataFrame]):
    pass
