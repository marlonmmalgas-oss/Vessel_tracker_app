import streamlit as st
import json
from datetime import datetime, timedelta
import urllib.parse
import webbrowser
import os

SAVE_FILE = "vessel_report.json"

# --- Load previous cumulative totals ---
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        cumulative = json.load(f)
else:
    cumulative = {
        "done_load": 0, "done_disch": 0,
        "done_restow_load": 0, "done_restow_disch": 0,
        "done_hatch_open": 0, "done_hatch_close": 0,
        "last_hour": None,
        "vessel_name": "",
        "berthed_date": "",
        "planned_load": 687,
        "planned_disch": 38,
        "planned_restow_load": 13,
        "planned_restow_disch": 13,
        "opening_load": 0,
        "opening_disch": 0
    }

# --- Vessel Info (set once) ---
st.sidebar.header("Vessel Info")
if "vessel_name" not in st.session_state:
    st.session_state.vessel_name = cumulative.get("vessel_name", "")
if "berthed_date" not in st.session_state:
    st.session_state.berthed_date = cumulative.get("berthed_date", "")

st.session_state.vessel_name = st.sidebar.text_input("Vessel Name", st.session_state.vessel_name)
st.session_state.berthed_date = st.sidebar.text_input("Berthed Date", st.session_state.berthed_date)

# Save vessel info to cumulative
cumulative["vessel_name"] = st.session_state.vessel_name
cumulative["berthed_date"] = st.session_state.berthed_date

# --- Planned Totals & Opening Balance ---
st.sidebar.header("Totals & Opening Balance")
planned_load = st.sidebar.number_input("Planned Load", value=cumulative["planned_load"], min_value=0)
planned_disch = st.sidebar.number_input("Planned Discharge", value=cumulative["planned_disch"], min_value=0)
planned_restow_load = st.sidebar.number_input("Planned Restow Load", value=cumulative["planned_restow_load"], min_value=0)
planned_restow_disch = st.sidebar.number_input("Planned Restow Discharge", value=cumulative["planned_restow_disch"], min_value=0)
opening_load = st.sidebar.number_input("Opening Load", value=cumulative["opening_load"], min_value=0)
opening_disch = st.sidebar.number_input("Opening Discharge", value=cumulative["opening_disch"], min_value=0)

# Save totals to cumulative
cumulative.update({
    "planned_load": planned_load,
    "planned_disch": planned_disch,
    "planned_restow_load": planned_restow_load,
    "planned_restow_disch": planned_restow_disch,
    "opening_load": opening_load,
    "opening_disch": opening_disch
})

# --- Hourly Slot ---
def next_hour_slot(last_hour=None):
    if last_hour:
        try:
            start = datetime.strptime(last_hour.split(" - ")[1], "%Hh%M")
        except:
            start = datetime.strptime("06h00", "%Hh%M")
    else:
        start = datetime.strptime("06h00", "%Hh%M")
    end = start + timedelta(hours=1)
    return start.strftime("%Hh%M") + " - " + end.strftime("%Hh%M")

hourly_time = next_hour_slot(cumulative.get("last_hour", None))
st.sidebar.text(f"Hourly Time: {hourly_time}")

# --- Hourly Moves Input ---
st.header(f"Hourly Moves Input ({hourly_time})")
fwd_load = st.number_input("FWD Load", min_value=0, value=0)
fwd_disch = st.number_input("FWD Discharge", min_value=0, value=0)
mid_load = st.number_input("MID Load", min_value=0, value=0)
mid_disch = st.number_input("MID Discharge", min_value=0, value=0)
aft_load = st.number_input("AFT Load", min_value=0, value=0)
aft_disch = st.number_input("AFT Discharge", min_value=0, value=0)
poop_load = st.number_input("POOP Load", min_value=0, value=0)
poop_disch = st.number_input("POOP Discharge", min_value=0, value=0)

st.subheader("Restows")
fwd_restow_load = st.number_input("FWD Restow Load", min_value=0, value=0)
fwd_restow_disch = st.number_input("FWD Restow Discharge", min_value=0, value=0)
mid_restow_load = st.number_input("MID Restow Load", min_value=0, value=0)
mid_restow_disch = st.number_input("MID Restow Discharge", min_value=0, value=0)
aft_restow_load = st.number_input("AFT Restow Load", min_value=0, value=0)
aft_restow_disch = st.number_input("AFT Restow Discharge", min_value=0, value=0)
poop_restow_load = st.number_input("POOP Restow Load", min_value=0, value=0)
poop_restow_disch = st.number_input("POOP Restow Discharge", min_value=0, value=0)

st.subheader("Hatch Cover Moves")
hatch_fwd_open = st.number_input("FWD Hatch Open", min_value=0, value=0)
hatch_fwd_close = st.number_input("FWD Hatch Close", min_value=0, value=0)
hatch_mid_open = st.number_input("MID Hatch Open", min_value=0, value=0)
hatch_mid_close = st.number_input("MID Hatch Close", min_value=0, value=0)
hatch_aft_open = st.number_input("AFT Hatch Open", min_value=0, value=0)
hatch_aft_close = st.number_input("AFT Hatch Close", min_value=0, value=0)

# --- Submit Button ---
if st.button("Submit Hourly Moves"):
    cumulative["done_load"] += fwd_load + mid_load + aft_load + poop_load
    cumulative["done_disch"] += fwd_disch + mid_disch + aft_disch + poop_disch
    cumulative["done_restow_load"] += fwd_restow_load + mid_restow_load + aft_restow_load + poop_restow_load
    cumulative["done_restow_disch"] += fwd_restow_disch + mid_restow_disch + aft_restow_disch + poop_restow_disch
    cumulative["done_hatch_open"] += hatch_fwd_open + hatch_mid_open + hatch_aft_open
    cumulative["done_hatch_close"] += hatch_fwd_close + hatch_mid_close + hatch_aft_close
    cumulative["last_hour"] = hourly_time

    # Save cumulative
    with open(SAVE_FILE, "w") as f:
        json.dump(cumulative, f)

    # --- WhatsApp Template ---
    template = f"""
{cumulative['vessel_name']}
Berthed {cumulative['berthed_date']}

Hourly Time: {hourly_time}
_________________________
   *HOURLY MOVES*
_________________________
*Crane Moves*
           Load    Disch
FWD       {fwd_load:>5}    {fwd_disch:>5}
MID       {mid_load:>5}    {mid_disch:>5}
AFT       {aft_load:>5}    {aft_disch:>5}
POOP      {poop_load:>5}    {poop_disch:>5}
_________________________
*Restows*
           Load    Disch
FWD       {fwd_restow_load:>5}    {fwd_restow_disch:>5}
MID       {mid_restow_load:>5}    {mid_restow_disch:>5}
AFT       {aft_restow_load:>5}    {aft_restow_disch:>5}
POOP      {poop_restow_load:>5}    {poop_restow_disch:>5}
_________________________
*CUMULATIVE (including Opening Balance)*
           Load    Disch
Plan      {planned_load:>5}    {planned_disch:>5}
Done      {cumulative['done_load'] + opening_load:>5}    {cumulative['done_disch'] + opening_disch:>5}
Remain    {planned_load - cumulative['done_load'] + opening_load:>5}    {planned_disch - cumulative['done_disch'] + opening_disch:>5}
_________________________
*Restows*
Plan      {planned_restow_load:>5}    {planned_restow_disch:>5}
Done      {cumulative['done_restow_load'] + opening_load:>5}    {cumulative['done_restow_disch'] + opening_disch:>5}
Remain    {planned_restow_load - cumulative['done_restow_load'] + opening_load:>5}    {planned_restow_disch - cumulative['done_restow_disch'] + opening_disch:>5}
_________________________
*Hatch Moves*
           Open    Close
FWD       {hatch_fwd_open:>5}    {hatch_fwd_close:>5}
MID       {hatch_mid_open:>5}    {hatch_mid_close:>5}
AFT       {hatch_aft_open:>5}    {hatch_aft_close:>5}
_________________________
*Idle*
"""

    st.text_area("WhatsApp Template", template, height=600)

    # --- WhatsApp / Copy Buttons ---
    phone_number = st.text_input("Enter WhatsApp Number (international format, no +)")
    if st.button("Open WhatsApp"):
        if phone_number:
            url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(template)}"
            webbrowser.open(url)
        else:
            st.warning("Enter a WhatsApp number first!")

    if st.button("Copy Template to Clipboard"):
        st.experimental_set_query_params()  # hack to enable button focus
        st.code(template)
        st.success("Template copied! Paste into WhatsApp group.")