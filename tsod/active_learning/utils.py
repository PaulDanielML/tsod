from copy import deepcopy
import datetime
import random
import os
from typing import Any, Dict, List, Sequence
import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict
from tsod.active_learning.data_structures import AnnotationState

MODEL_OPTIONS = {"RF_1": "Random Forest Classifier"}


SELECT_OPTIONS = {"Point": "zoom", "Box": "select", "Lasso": "lasso"}
SELECT_INFO = {
    "Point": "Select individual points, drag mouse to zoom in.",
    "Box": "Draw Box to select all points in range.",
    "Lasso": "Draw Lasso to select all points in range.",
}


def custom_text(
    text: str,
    font_size: int = 30,
    centered: bool = True,
    font: str = "sans-serif",
    vertical_align: str = "baseline",
    base_obj=None,
):
    obj = base_obj or st
    if centered:
        text_align = "center"
    else:
        text_align = "left"
    md = f'<p style="text-align: {text_align}; vertical-align: {vertical_align}; font-family:{font}; font-size: {font_size}px;">{text}</p>'

    return obj.markdown(md, unsafe_allow_html=True)


@st.cache(allow_output_mutation=True)
def load_data(file_name: str = "TODO"):
    df = pd.read_csv("data/Elev_NW1.csv", index_col=0, parse_dates=True)
    df["Water Level"] = df["Water Level"].astype(np.float16)
    # df["ts"] = df.index.values.astype(np.int64) // 10**6
    return df


def get_as() -> AnnotationState:
    return st.session_state.AS


def _add_to_ss_if_not_in_it(key: str, init_value: Any):
    if key not in st.session_state:
        st.session_state[key] = init_value


def init_session_state():
    _add_to_ss_if_not_in_it("df_full", load_data())
    _add_to_ss_if_not_in_it("AS", AnnotationState(st.session_state["df_full"]))
    _add_to_ss_if_not_in_it("annotation_data_loaded", True)
    _add_to_ss_if_not_in_it("uploaded_annotation_data", {})
    _add_to_ss_if_not_in_it("prediction_models", {})
    _add_to_ss_if_not_in_it("prediction_data", {})
    # _add_to_ss_if_not_in_it("last_model_name", None)
    _add_to_ss_if_not_in_it("use_date_picker", True)
    _add_to_ss_if_not_in_it("inference_results", {})
    _add_to_ss_if_not_in_it("number_outliers", defaultdict(dict))
    _add_to_ss_if_not_in_it("uploaded_ds_features", {})
    _add_to_ss_if_not_in_it(
        "plot_start_date",
        st.session_state["df_full"].index.max().date() - datetime.timedelta(days=3),
    )
    _add_to_ss_if_not_in_it("plot_end_date", st.session_state["df_full"].index.max().date())
    _add_to_ss_if_not_in_it("date_shift_buttons_used", False)
    _add_to_ss_if_not_in_it("hide_choice_menus", False)
    _add_to_ss_if_not_in_it("models_to_visualize", defaultdict(set))
    _add_to_ss_if_not_in_it("RF_features_computed_start", 0)
    _add_to_ss_if_not_in_it("RF_features_computed_end", 0)
    _add_to_ss_if_not_in_it("model_library", {})
    _add_to_ss_if_not_in_it("available_models", defaultdict(set))
    _add_to_ss_if_not_in_it("current_outlier_value_store", {})
    _add_to_ss_if_not_in_it("page_index", 0)


def set_session_state_items(key: str | List[str], value: Any | List[Any]):
    if [type(key), type(value)].count(list) == 1:
        raise ValueError("Either both or neither of key and value should be list.")

    if isinstance(key, list):
        assert len(key) == len(value)
        for k, v in zip(key, value):
            st.session_state[k] = v

    else:
        st.session_state[key] = value


def recursive_length_count(data: Dict, exclude_keys: Sequence = None) -> int:
    total = 0
    _exclude = exclude_keys or []
    for k, v in data.items():
        if k in _exclude:
            continue
        if isinstance(v, (set, list)):
            total += len(v)
        elif isinstance(v, dict):
            total += recursive_length_count(v)

    return total


def recursive_sum(data: Dict) -> int | float:
    total = 0
    for v in data.values():
        if isinstance(v, (int, float)):
            total += v
        elif isinstance(v, dict):
            total += recursive_sum(v)

    return total


def recursive_round(data: Dict, decimals: int = 3):
    def value_round(v):
        if isinstance(v, np.ndarray):
            return v.round(decimals)
        elif isinstance(v, float):
            return round(v, decimals)

    local_data = deepcopy(data)

    for k, v in local_data.items():
        if isinstance(v, (np.ndarray, float)):
            local_data[k] = value_round(v)
        elif isinstance(v, list):
            local_data[k] = [value_round(e) for e in v]
        elif isinstance(v, tuple):
            local_data[k] = tuple(
                [value_round(x) if isinstance(x, (float, np.ndarray)) else x for x in v]
            )
        elif isinstance(v, set):
            local_data[k] = {value_round(e) for e in v}
        elif isinstance(v, dict):
            local_data[k] = recursive_round(v)

    return local_data


def fix_random_seeds(seed=30):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
