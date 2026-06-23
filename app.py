import streamlit as st
import pandas as pd
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard Monitoring Petugas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

FILE = "mapping_petugas.xlsx"

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data(file_time):
    df_ppl = pd.read_excel(FILE, sheet_name="PPL")
    df_pml = pd.read_excel(FILE, sheet_name="PML")

    return df_ppl, df_pml


df_ppl, df_pml = load_data(
    os.path.getmtime(FILE)
)

# =====================================================
# UTILITIES
# =====================================================

SORT_COLUMNS = [
    "PROGRESS",
    "total",
    "APPROVED BY Pengawas",
    "DRAFT",
    "OPEN",
    "REJECTED BY Pengawas",
    "REVOKED BY Pengawas",
    "SUBMITTED BY Pencacah",
    "SUBMITTED RESPONDENT"
    
]


def convert_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# =====================================================
# WAKTU UPDATE FILE
# =====================================================

def waktu_update_file():

    waktu = os.path.getmtime(FILE)

    waktu_utc = datetime.fromtimestamp(
        waktu,
        tz=ZoneInfo("UTC")
    )

    waktu_indonesia = waktu_utc.astimezone(
        ZoneInfo("Asia/Makassar")
    )

    return waktu_indonesia.strftime(
        "%d %B %Y %H:%M"
    )

def format_table(df):

    return (
        df.style
        .apply(
            warna_status,
            axis=1
        )
        .set_properties(
            **{
                "font-size": "11px",
                "max-width": "80px",
                "white-space": "normal",
                "text-align": "center"
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("font-size", "11px"),
                        ("white-space", "pre-line"),
                        ("word-wrap", "break-word"),
                        ("max-width", "80px"),
                        ("text-align", "center")
                    ]
                }
            ]
        )
    )

# =====================================================
# TARGET HARIAN DINAMIS
# =====================================================



def warna_status(row):

    return [
        "color: green"
        if col == "APPROVED BY Pengawas"
        else "color: orange"
        if col == "DRAFT"
        else "color: red"
        if col in [
            "REJECTED BY Pengawas",
            "REVOKED BY Pengawas"
        ]
        else "color: deepskyblue"
        if col in [
            "SUBMITTED BY Pencacah",
            "SUBMITTED RESPONDENT"
        ]
        else ""
        for col in row.index
            
    ]


# =====================================================
# HEADER
# =====================================================

st.title("📊 Dashboard Monitoring Petugas SE2026 BPS Kota Bitung")

st.caption(
    f"Monitoring progres pekerjaan PPL dan PML | "
    f"Update terakhir: {waktu_update_file()}"
)

# =====================================================
# TABS
# =====================================================

tab_ppl, tab_pml, tab_ringkasan = st.tabs(
    [
        "📋 Data PPL",
        "👤 Data PML",
        "📊 Ringkasan"
    ]
)

# =====================================================
# TAB PPL
# =====================================================

with tab_ppl:

    st.subheader("Monitoring PPL")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pilih_pml = st.multiselect(
            "Filter PML",
            sorted(df_ppl["PML"].dropna().unique()),
            key="filter_pml_ppl"
        )

    with col2:
        pilih_taskforce = st.multiselect(
            "Filter Taskforce",
            sorted(df_ppl["TASKFORCE"].dropna().unique()),
            key="filter_taskforce_ppl"
        )

    with col3:
        sort_column = st.selectbox(
            "Urutkan Berdasarkan",
            SORT_COLUMNS,
            key="sort_column_ppl"
        )

    with col4:

        target_ppl = st.number_input(
            "⚠️ Filter PPL dibawah target",
            min_value=0,
            value=60,
            step=10,
            key="input_target_ppl"
        )

        hanya_belum_target = st.checkbox(
            f"Tampilkan PPL progress < {target_ppl}",
            key="filter_target_ppl"
        )

    ascending = st.radio(
        "Urutan",
        ["Besar ke kecil", "Kecil ke besar"],
        horizontal=True,
        key="order_ppl"
    )

    data_ppl = df_ppl.copy()

    if pilih_pml:
        data_ppl = data_ppl[
            data_ppl["PML"].isin(pilih_pml)
        ]

    if pilih_taskforce:
        data_ppl = data_ppl[
            data_ppl["TASKFORCE"].isin(pilih_taskforce)
        ]

    if hanya_belum_target:

        data_ppl = data_ppl[
            data_ppl["PROGRESS"] < target_ppl
        ]

    data_ppl = data_ppl.sort_values(
        by=sort_column,
        ascending=(ascending == "Kecil ke besar")
    )

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        "Jumlah PPL",
        len(data_ppl)
    )

    kpi2.metric(
        "Total Dokumen",
        f"{int(data_ppl['total'].sum()):,}"
    )

    kpi3.metric(
        "Rata-rata Progress",
        f"{data_ppl['PROGRESS'].mean():.1f}"
    )

    st.divider()

    display_ppl = data_ppl.copy()

    display_ppl.columns = [
        col.replace(" ", "\n")
        for col in display_ppl.columns
    ]
    display_ppl = (
        data_ppl
        .drop(
            columns=["email"],
            errors="ignore"
        )
        .reset_index(drop=True)
    )

    display_ppl.insert(
        0,
        "No",
        range(1, len(display_ppl) + 1)
    )


    st.dataframe(
        format_table(display_ppl),
        use_container_width=True,
        height=700,
        hide_index=True,
        column_config={
            "PPL": st.column_config.TextColumn(
                width="medium"
            ),
            "PML": st.column_config.TextColumn(
                width="medium"
            ),
            "TASKFORCE": st.column_config.TextColumn(
                width="small"
            )
        }
    )

    st.download_button(
        "⬇️ Download Hasil Filter PPL",
        convert_csv(data_ppl),
        "hasil_filter_ppl.csv",
        "text/csv",
        key="download_ppl"
    )

# =====================================================
# TAB PML
# =====================================================

with tab_pml:

    st.subheader("Monitoring PML")

    col1, col2 = st.columns(2)

    with col1:
        pilih_taskforce_pml = st.multiselect(
            "Filter Taskforce",
            sorted(
                df_pml["TASKFORCE"]
                .dropna()
                .unique()
            ),
            key="filter_taskforce_pml"
        )

    with col2:
        sort_column_pml = st.selectbox(
            "Urutkan Berdasarkan",
            SORT_COLUMNS,
            key="sort_column_pml"
        )

    ascending_pml = st.radio(
        "Urutan",
        ["Besar ke kecil", "Kecil ke besar"],
        horizontal=True,
        key="order_pml"
    )

    data_pml = df_pml.copy()

    if pilih_taskforce_pml:
        data_pml = data_pml[
            data_pml["TASKFORCE"]
            .isin(pilih_taskforce_pml)
        ]

    data_pml = data_pml.sort_values(
        by=sort_column_pml,
        ascending=(
            ascending_pml == "Kecil ke besar"
        )
    )

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        "Jumlah PML",
        len(data_pml)
    )

    kpi2.metric(
        "Total Dokumen",
        f"{int(data_pml['total'].sum()):,}"
    )

    kpi3.metric(
        "Rata-rata Progress",
        f"{data_pml['PROGRESS'].mean():.1f}"
    )

    st.divider()

    display_pml = (
        data_pml
        .drop(
        columns=["email"],
        errors="ignore"
        )
        .reset_index(drop=True)
    )
    


    display_pml.insert(
        0,
        "No",
        range(1, len(display_pml) + 1)
    )
    st.dataframe(
        format_table(display_pml),
        use_container_width=True,
        height=700,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Hasil Filter PML",
        convert_csv(data_pml),
        "hasil_filter_pml.csv",
        "text/csv",
        key="download_pml"
    )

# =====================================================
# TAB RINGKASAN
# =====================================================

with tab_ringkasan:

    st.subheader("📊 Ringkasan Monitoring")

    total_dokumen = df_ppl["total"].sum()


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total PPL",
        len(df_ppl)
    )

    col2.metric(
        "Total PML",
        len(df_pml)
    )

    col3.metric(
        "Total Dokumen",
        f"{int(total_dokumen):,}"
    )


    st.divider()

    st.subheader("📌 Distribusi Status Pekerjaan")


    status_list = [
        "OPEN",
        "SUBMITTED BY Pencacah",
        "DRAFT",
        "APPROVED BY Pengawas",
        "REJECTED BY Pengawas",
        "REVOKED BY Pengawas",
        "SUBMITTED RESPONDENT"
    ]


    warna_status = {

        "OPEN": "#555555",

        "DRAFT": "#f39c12",

        "APPROVED BY Pengawas": "#27ae60",

        "REJECTED BY Pengawas": "#e74c3c",

        "REVOKED BY Pengawas": "#e74c3c",

        "SUBMITTED BY Pencacah": "#3498db",

        "SUBMITTED RESPONDENT": "#3498db"

    }


    cards = st.columns(4)


    for i, status in enumerate(status_list):

        jumlah = df_ppl[status].sum()

        persen = (
            jumlah / total_dokumen * 100
            if total_dokumen > 0
            else 0
        )


        with cards[i % 4]:

            st.markdown(
                f"""
                <div style="
                        border-radius:12px;
                        padding:18px;
                        text-align:center;
                        height:140px;
                        border:1px solid rgba(128,128,128,0.25);
                ">

                <div style="
                    font-size:14px;
                    font-weight:bold;
                    color:{warna_status[status]};
                    margin-bottom:15px;
                ">
                    {status}
                </div>


                <div style="
                    font-size:28px;
                    font-weight:bold;
                    color:inherit;
                ">
                    {int(jumlah):,}
                </div>


                <div style="
                    font-size:13px;
                    color:inherit;
                    opacity:0.7;
                    margin-top:10px;
                ">
                    {persen:.1f}% dari total
                </div>


                </div>
                """,
                unsafe_allow_html=True
            )