# filename: vessel_tracker_app.py
import streamlit as st
import json
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
import os

SAVE_FILE = "vessel_report.json"

# ==========================
# Load previous cumulative totals
# ==========================
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        cumulative = json.load(f)
else:
    cumulative = {
        "done_load": 0, "done_disch": 0,
        "done_restow_load": 0, "done_restow_disch": 0,
        "done_hatch_open": 0, "done_hatch_close": 0
    }

# ==========================
# Sidebar: Vessel Info
# ==========================
st.sidebar.header("Vessel Info")
vessel_name = st.sidebar.text_input("Vessel Name", "MSC NILA")
berthed_date = st.sidebar.text_input("Berthed Date", "14/08/2025 @ 10H55")
first_lift = st.sidebar.text_input("First Lift", "18h25")
last_lift = st.sidebar.text_input("Last Lift", "10h31")
todays_date = st.sidebar.date_input("Today's Date", datetime.today())

# ==========================
# Calculate Hourly Time
# ==========================
def next_hour_slot(last_hour=None):
    if last_hour:
        start = datetime.strptime(last_hour.split(" - ")[1], "%Hh%M")
    else:
        start = datetime.strptime("06h00", "%Hh%M")
    end = start + timedelta(hours=1)
    return start.strftime("%Hh%M") + " - " + end.strftime("%Hh%M")

last_hour = cumulative.get("last_hour", None)
hourly_time = next_hour_slot(last_hour)

st.sidebar.text(f"Hourly Time: {hourly_time}")

# ==========================
# Input Planned Totals
# ==========================
st.sidebar.header("Planned Totals")
planned_load = st.sidebar.number_input("Planned Load", min_value=0, value=687)
planned_disch = st.sidebar.number_input("Planned Discharge", min_value=0, value=38)
planned_restow_load = st.sidebar.number_input("Planned Restow Load", min_value=0, value=13)
planned_restow_disch = st.sidebar.number_input("Planned Restow Discharge", min_value=0, value=13)

# ==========================
# Hourly Input
# ==========================
st.header("Hourly Moves Input")
st.subheader("Crane Moves")
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

# ==========================
# Generate WhatsApp Message
# ==========================
if st.button("Generate WhatsApp Message"):

    # Update cumulative totals
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

    # Align numbers using <5 spacing
    template = f"""
{vessel_name}
Berthed {berthed_date}

First Lift @ {first_lift}
Last Lift @ {last_lift}

{todays_date.strftime('%d/%m/%Y')}
{hourly_time}
_________________________
   *HOURLY MOVES*
_________________________
*Crane Moves*
           Load      Discharge
FWD       {fwd_load:<5}     {fwd_disch}
MID       {mid_load:<5}     {mid_disch}
AFT       {aft_load:<5}     {aft_disch}
POOP      {poop_load:<5}     {poop_disch}
_______________________
*Restows*
           Load      Discharge
FWD       {fwd_restow_load:<5}     {fwd_restow_disch}
MID       {mid_restow_load:<5}     {mid_restow_disch}
AFT       {aft_restow_load:<5}     {aft_restow_disch}
POOP      {poop_restow_load:<5}     {poop_restow_disch}
_______________________
      *CUMULATIVE*
_______________________
                Load      Disch
Plan.      {planned_load:<5}    {planned_disch}
Done       {cumulative['done_load']:<5}    {cumulative['done_disch']}
Remain     {planned_load - cumulative['done_load']:<5}    {planned_disch - cumulative['done_disch']}
________________________
  *Restows*
               Load     Disch
Plan      {planned_restow_load:<5}    {planned_restow_disch}
Done      {cumulative['done_restow_load']:<5}    {cumulative['done_restow_disch']}
Remain    {planned_restow_load - cumulative['done_restow_load']:<5}    {planned_restow_disch - cumulative['done_restow_disch']}
_______________________
*Hatch Moves*
           Open     Close
FWD       {hatch_fwd_open:<5}     {hatch_fwd_close}
MID       {hatch_mid_open:<5}     {hatch_mid_close}
AFT       {hatch_aft_open:<5}     {hatch_aft_close}
_________________________
*Idle*
"""
    st.text_area("WhatsApp Message", template, height=600)

    # WhatsApp link
    phone_number = st.text_input("Enter WhatsApp Number (international format, no +)")
    if st.button("Open WhatsApp"):
        if phone_number:
            url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(template)}"
            webbrowser.open(url)
        else:
            st.warning(27794183256)
            