import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from html import escape


# =====================================================
# CONFIG
# =====================================================



st.set_page_config(
    page_title="Dashboard Monitoring Petugas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

/* =======================================
   GLOBAL
======================================= */

.main {
    padding-top: 1rem;
}

/* =======================================
   TABS
======================================= */

button[data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 600;
    padding-top: 10px;
    padding-bottom: 10px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #3b82f6;
}

/* =======================================
   KPI METRIC
======================================= */

div[data-testid="stMetric"] {
    background-color: rgba(128,128,128,0.08);
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 12px;
    padding: 14px;
}

div[data-testid="stMetricLabel"] {
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    font-size: 28px;
}

/* =======================================
   DATAFRAME
======================================= */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(128,128,128,0.15);
}

/* =======================================
   CONTAINER CARD
======================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}

/* =======================================
   ALERT CARD (MERAH)
======================================= */

div[data-testid="stAlertContainer"][kind="error"] {
    border-left: 6px solid #dc2626;
    border-radius: 10px;
}

/* =======================================
   ALERT CARD (HIJAU)
======================================= */

div[data-testid="stAlertContainer"][kind="success"] {
    border-left: 6px solid #16a34a;
    border-radius: 10px;
}

/* =======================================
   MULTISELECT
======================================= */

div[data-baseweb="select"] {
    border-radius: 10px;
}

/* =======================================
   SELECTBOX
======================================= */

div[data-baseweb="popover"] {
    border-radius: 10px;
}

/* =======================================
   DOWNLOAD BUTTON
======================================= */

button[kind="secondary"] {
    border-radius: 10px;
}

/* =======================================
   SCROLLBAR
======================================= */

::-webkit-scrollbar {
    height: 10px;
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(120,120,120,0.4);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

FILE = "mapping_petugas.xlsx"

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    xls = pd.ExcelFile(FILE)

    df_ppl = pd.read_excel(xls, sheet_name="PPL")
    df_pml = pd.read_excel(xls, sheet_name="PML")
    df_harian = pd.read_excel(xls, sheet_name="HARIAN")
    df_target = pd.read_excel(xls, sheet_name="TARGET")

    df_harian.columns = (
        df_harian.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df_ppl, df_pml, df_harian, df_target

df_ppl, df_pml, df_harian, df_target = load_data()

persentase_ppl = (
    df_ppl.set_index("PPL")["PERSENTASE"]
    .to_dict()
)

update_file = datetime.fromtimestamp(
    os.path.getmtime(FILE)
)

tanggal_data = (
    update_file - timedelta(days=1)
).date()

df_target["TANGGAL"] = pd.to_datetime(
    df_target["TANGGAL"]
).dt.date

df_target["TARGET"] = (
    df_target["TARGET"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

target_hari_ini = (
    df_target.loc[
        df_target["TANGGAL"] == tanggal_data,
        "TARGET"
    ]
)

if len(target_hari_ini) > 0:
    target_hari_ini = float(target_hari_ini.iloc[0])
else:
    target_hari_ini = 0

tanggal_kemarin = tanggal_data.strftime(
    "%d %B %Y"
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

def singkat_nama(nama, panjang=22):
    nama = str(nama)

    if len(nama) <= panjang:
        return nama

    return nama[:panjang] + "..."

def tampil_card(
    nama,
    dua_hari_lalu,
    kemarin,
    hari_ini,
    progress,
    persentase,
    warna
):
    st.markdown(
        f"""
        <div style="
            background-color:{warna};
            color:white;
            border-radius:10px;
            padding:8px;
            text-align:center;
            min-height:110px;
            margin:4px;
            margin-bottom:12px;
        ">

        <div style="
            font-weight:bold;
            font-size:12px;
            margin-bottom:6px;
        ">
        {nama}
        </div>

        <div style="font-size:11px;">
        {int(dua_hari_lalu)} → {int(kemarin)} → {int(hari_ini)}
        </div>

        <div style="font-size:11px;">
        Capaian: {persentase:.2f}%
        </div>

        <div style="
            margin-top:6px;
            font-size:18px;
            font-weight:bold;
        ">
        +{int(progress)}
        </div>

        </div>
        """,
        unsafe_allow_html=True
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

tab_harian, tab_ppl, tab_pml, tab_ringkasan = st.tabs(
    [
        "📈 Progress Harian",
        "📋 Data PPL",
        "👤 Data PML",
        "📊 Ringkasan"
    ]
)

with tab_harian:

    st.subheader("📈 Progress Harian Petugas")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        pilih_pml_harian = st.multiselect(
            "Filter PML",
            sorted(
                df_harian["PML"]
                .dropna()
                .unique()
            ),
            key="filter_pml_harian"
        )

    with filter_col2:

        pilih_taskforce_harian = st.multiselect(
            "Filter Taskforce",
            sorted(
                df_harian["TASKFORCE"]
                .dropna()
                .unique()
            ),
            key="filter_taskforce_harian"
        )

    col1, col2 = st.columns(2)

    with col1:

        filter_jabatan = st.multiselect(
            "Filter Jabatan",
            sorted(
                df_harian["JABATAN"]
                .dropna()
                .unique()
            ),
            key="filter_jabatan_harian"
        )

    with col2:

        sort_harian = st.selectbox(
            "Urutkan Berdasarkan",
            [
                "KEMARIN",
                "HARI INI",
                "PROGRESS"
            ],
            index=2,
            key="sort_harian"
        )

    urutan_harian = st.radio(
        "Urutan",
        [
            "Kecil ke besar",
            "Besar ke kecil"
        ],
        horizontal=True,
        key="urutan_harian"
    )

    data_harian = df_harian.copy()

    if pilih_pml_harian:

        data_harian = data_harian[
            data_harian["PML"]
            .isin(pilih_pml_harian)
        ]

    if pilih_taskforce_harian:

        data_harian = data_harian[
            data_harian["TASKFORCE"]
            .isin(pilih_taskforce_harian)
        ]

    if filter_jabatan:

        data_harian = data_harian[
            data_harian["JABATAN"]
            .isin(filter_jabatan)
        ]

    data_harian = data_harian.sort_values(
        by=sort_harian,
        ascending=(
            urutan_harian
            == "Kecil ke besar"
        )
    )

    display_harian = (
        data_harian
        .reset_index(drop=True)
    )

    display_harian.insert(
        0,
        "No",
        range(
            1,
            len(display_harian)+1
        )
    )

    

    st.divider()

    batas_progress = 10

      

    chart_data = (
        data_harian[
            data_harian["PROGRESS"] < batas_progress
        ]
        .sort_values(
            by="PROGRESS",
            ascending=True
        )
    )

    batas_progress = 10

    petugas_stagnan = (
        data_harian[
            (data_harian["JABATAN"] == "PPL")
            &
            (
                data_harian["STATUS"]
                .astype(str)
                .str.upper()
                == "TRUE"
            )
        ]
    )
    
    nama_rendah = df_ppl.loc[
        df_ppl["PERSENTASE"] < target_hari_ini,
        "PPL"
    ]

    petugas_rendah = (
        data_harian[
            data_harian["NAMA PETUGAS"].isin(nama_rendah)
        ]
        .sort_values(
            by="PROGRESS",
            ascending=True
        )
    )

    # Cari nama PPL yang mencapai target
    nama_unggul = df_ppl.loc[
        df_ppl["PERSENTASE"] >= target_hari_ini,
        "PPL"
    ]

    # Ambil data lengkap dari sheet HARIAN
    petugas_unggul = (
        data_harian[
            data_harian["NAMA PETUGAS"].isin(nama_unggul)
        ]
        .sort_values(
            by="PROGRESS",
            ascending=False
        )
    )

    st.subheader(
        f"⛔ {len(petugas_stagnan)} PPL dengan Progress Stagnan Selama 3 Hari"
    )

    if len(petugas_stagnan) > 0:

        jumlah_kolom = 3

        for i in range(
            0,
            len(petugas_stagnan),
            jumlah_kolom
        ):

            cols = st.columns(
                jumlah_kolom,
                gap="medium"
            )

            for j, (_, row) in enumerate(
                petugas_stagnan.iloc[
                    i:i+jumlah_kolom
                ].iterrows()
            ):

                with cols[j]:

                    tampil_card(
                        row["NAMA PETUGAS"],
                        row.iloc[4],
                        row["KEMARIN"],
                        row["HARI INI"],
                        row["PROGRESS"],
                        target_hari_ini,
                        "#7f1d1d"
                    )

    else:

        st.success(
            "🎉 Tidak ada petugas yang stagnan selama 3 hari."
        )
    st.subheader(
        f"🚨 {len(petugas_rendah)} PPL dengan Capaian di Bawah Target yaitu {target_hari_ini:.2f}% pada {tanggal_kemarin}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Petugas",
        len(data_harian)
    )

    col2.metric(
        "PPL di bawah Target",
        len(petugas_rendah)
    )

    col3.metric(
        "Rata-rata Progress",
        round(data_harian["PROGRESS"].mean(), 1)
    )

    if len(petugas_rendah) > 0:

        jumlah_kolom = 6

        for i in range(
            0,
            len(petugas_rendah),
            jumlah_kolom
        ):

            cols = st.columns(
                jumlah_kolom,
                gap="medium"
            )

            for j, (_, row) in enumerate(
                petugas_rendah.iloc[
                    i:i+jumlah_kolom
                ].iterrows()
            ):

                with cols[j]:
                    tampil_card(
                    row["NAMA PETUGAS"],
                    row.iloc[4],
                    row["KEMARIN"],
                    row["HARI INI"],
                    row["PROGRESS"],
                    persentase_ppl.get(
                        row["NAMA PETUGAS"],
                        0
                    ),
                    "#bd480a"
                )
    else:

        st.success(
            "🎉 Semua petugas memiliki progress minimal 10."
        )

    st.subheader("Tabel Progress Harian")

    st.dataframe(
        display_harian,
        use_container_width=True,
        height=500,
        hide_index=True
    )

    st.divider()

    st.subheader(
        f"🏆 {len(petugas_unggul)} PPL Melampaui Target pada {tanggal_kemarin}"
    )
    
    if len(petugas_unggul) > 0:

        jumlah_kolom = 10

        for i in range(
            0,
            len(petugas_unggul),
            jumlah_kolom
        ):

            cols = st.columns(
                jumlah_kolom,
                gap="small"
            )

            for j, (_, row) in enumerate(
                petugas_unggul.iloc[
                    i:i+jumlah_kolom
                ].iterrows()
            ):

                with cols[j]:
                    tampil_card(
                    row["NAMA PETUGAS"],
                    row.iloc[4],
                    row["KEMARIN"],
                    row["HARI INI"],
                    row["PROGRESS"],
                    persentase_ppl.get(
                        row["NAMA PETUGAS"],
                        0
                    ),
                    "#166534"
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
        sort_ppl = st.selectbox(
        "Urutkan Berdasarkan",
        [
            "PERSENTASE",
            "PROGRESS",
            "TOTAL",
            "APPROVED BY Pengawas",
            "DRAFT",
            "OPEN",
            "REJECTED BY Pengawas"
        ],
        index=6,   # agar default langsung Persentase
        key="sort_ppl"
    )

    with col4:

        tampilkan_bawah_target = st.checkbox(
            f"Tampilkan hanya PPL dengan capaian di bawah target ({target_hari_ini:.2f}%)",
            value=False
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

    if tampilkan_bawah_target:
            data_ppl = data_ppl[
                data_ppl["PERSENTASE"] < target_hari_ini
            ]

    data_ppl = data_ppl.sort_values(
        by=sort_ppl,
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
            columns=[
            "REVOKED BY Pengawas",
            "SUBMITTED RESPONDENT",
            "OPEN", "email"
        ],
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
        columns=["email", "OPEN", "SUBMITTED RESPONDENT", "DRAFT"],
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

    st.subheader(
        f"📅 Monitoring Petugas {tanggal_kemarin}"
    )
    col_stagnan, col_rendah, col_unggul = st.columns(3)

    with col_stagnan:

        st.error(
            f"⛔ STAGNAN ({len(petugas_stagnan )} PPL)"
        )

        for nama in petugas_stagnan["NAMA PETUGAS"]:
            st.markdown(
                f"""
                <div style="
                    color:inherit;
                    font-weight:700;
                    font-size:14px;
                    margin-bottom:2px;
                ">
                    {nama}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col_rendah:

        st.warning(
            f"🚨 DI BAWAH TARGET ({len(petugas_rendah)} PPL)"
        )

        subcols = st.columns(3)

        for i, nama in enumerate(
            petugas_rendah["NAMA PETUGAS"]
        ):

            with subcols[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        color:inherit;
                        font-weight:700;
                        font-size:14px;
                        margin-bottom:2px;
                    ">
                        {nama}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col_unggul:

        st.success(
            f"🏆 CAPAI TARGET ({len(petugas_unggul)} PPL)"
        )

        subcols = st.columns(4)

        for i, nama in enumerate(
            petugas_unggul["NAMA PETUGAS"]
        ):

            with subcols[i % 4]:
                st.markdown(
                    f"""
                    <div style="
                        color:inherit;
                        font-weight:700;
                        font-size:14px;
                        margin-bottom:2px;
                    ">
                        {nama}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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