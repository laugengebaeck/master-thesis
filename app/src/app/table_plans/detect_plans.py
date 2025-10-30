from collections.abc import Callable

import pandas as pd
import table_plans.handlers as handlers

plan_file_map = {
    # "Az": handlers.handle_az_plan,
    # "D-Weg": handlers.handle_dweg_plan,
    # "Flank": handlers.handle_flank_plan,
    # "GM": handlers.handle_gm_plan,
    # "Gp": handlers.handle_gp_plan,
    # "Rang": handlers.handle_rang_plan,
    # "Sb": handlers.handle_sb_plan,
    "Sig1": handlers.handle_sig1_plan,
    # "Sig2": handlers.handle_sig2_plan,
    # "Wei": handlers.handle_wei_plan,
    # "Zug": handlers.handle_zug_plan,
    # "Zwie": handlers.handle_zwie_plan,
}


def detect_and_handle_plans(read_function: Callable[[str], list[pd.DataFrame]]):
    for plan_type, handler in plan_file_map.items():
        handler(read_function(plan_type))
