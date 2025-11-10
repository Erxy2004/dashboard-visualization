import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import numpy as np

# ===== KONFIGURASI PAGE =====
st.set_page_config(
    page_title="Universal Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    .main-header {
        padding: 1.5rem 0;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, rgba(var(--primary-color-rgb), 0.1) 0%, rgba(var(--secondary-background-color-rgb), 0.1) 100%);
    }
    
    .info-box {
        background-color: var(--secondary-background-color);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }
    
    .stMetric {
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 8px;
    }
    
    .step-box {
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNGSI HELPER =====
@st.cache_data
def load_data(uploaded_file):
    """Load data dari CSV yang diupload"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

def create_sample_data():
    """Buat data sampel untuk demonstrasi"""
    np.random.seed(42)
    n = 100
    
    sample_data = {
        'Tanggal': pd.date_range('2024-01-01', periods=n, freq='D').strftime('%Y-%m-%d').tolist(),
        'Kategori': np.random.choice(['Kategori A', 'Kategori B', 'Kategori C', 'Kategori D'], n),
        'Wilayah': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Bali'], n),
        'Tipe': np.random.choice(['Tipe 1', 'Tipe 2', 'Tipe 3'], n),
        'Status': np.random.choice(['Aktif', 'Tidak Aktif', 'Pending'], n),
        'Jumlah': np.random.randint(1, 100, n),
        'Harga': np.random.randint(10000, 1000000, n),
        'Nilai': np.random.randint(100000, 10000000, n),
    }
    return pd.DataFrame(sample_data)

def get_aggregation_name(agg_type):
    """Nama operasi yang mudah dipahami"""
    mapping = {
        'count': 'Hitung Jumlah Baris',
        'sum': 'Jumlahkan (Total)',
        'mean': 'Rata-rata',
        'median': 'Nilai Tengah',
        'min': 'Nilai Terkecil',
        'max': 'Nilai Terbesar',
        'std': 'Standar Deviasi',
        'nunique': 'Hitung Nilai Unik'
    }
    return mapping.get(agg_type, agg_type)

# ===== HEADER =====
st.markdown('<div class="main-header"><h1>📊 Dashboard Data Universal</h1><p>Untuk Semua Jenis Data - Inventory, Penjualan, Keuangan, dll</p></div>', unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    # Upload file
    st.subheader("📁 1. Upload Data Anda")
    uploaded_file = st.file_uploader(
        "Pilih file CSV",
        type=['csv'],
        help="Upload file Excel yang sudah disimpan sebagai CSV"
    )
    
    use_sample = st.checkbox("Gunakan Data Contoh", value=not uploaded_file)
    
    if use_sample and not uploaded_file:
        df_original = create_sample_data()
        st.success("✅ Menggunakan data contoh")
    elif uploaded_file:
        df_original, error = load_data(uploaded_file)
        if error:
            st.error(f"❌ Error: {error}")
            st.stop()
        else:
            st.success(f"✅ Data dimuat: {len(df_original)} baris")
    else:
        st.markdown("""
        <div class='info-box'>
            <h4>👋 Selamat Datang!</h4>
            <p>Upload file CSV Anda atau gunakan data contoh untuk memulai</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    st.divider()

# ===== PILIH KOLOM & OPERASI =====
st.subheader("🎯 Langkah 1: Pilih Kolom yang Ingin Ditampilkan")

all_columns = df_original.columns.tolist()

col1, col2 = st.columns([2, 1])

with col1:
    selected_columns = st.multiselect(
        "Pilih kolom dari data Anda:",
        all_columns,
        default=all_columns,
        help="Pilih kolom mana saja yang ingin Anda lihat dan analisis"
    )

with col2:
    if st.button("✅ Pilih Semua Kolom", use_container_width=True):
        selected_columns = all_columns
        st.rerun()

if not selected_columns:
    st.warning("⚠️ Silakan pilih minimal 1 kolom untuk melanjutkan")
    st.stop()

# Filter data dengan kolom yang dipilih
df = df_original[selected_columns].copy()

st.success(f"✅ Menampilkan {len(selected_columns)} kolom dari total {len(all_columns)} kolom")

st.divider()

# ===== ANALISIS & OPERASI DATA =====
st.subheader("🔧 Langkah 2: Tentukan Cara Analisis Data")

st.markdown("""
<div class='info-box'>
    <h4>💡 Penjelasan:</h4>
    <p><b>Kelompokkan berdasarkan</b>: Pilih kategori untuk mengelompokkan data (misal: Wilayah, Kategori, Bulan)</p>
    <p><b>Kolom untuk dihitung</b>: Pilih kolom angka yang ingin dianalisis (misal: Harga, Jumlah, Nilai)</p>
    <p><b>Cara perhitungan</b>: Pilih operasi matematika yang ingin dilakukan</p>
</div>
""", unsafe_allow_html=True)

# Deteksi tipe kolom
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

# Coba deteksi kolom tanggal
date_cols = []
for col in df.columns:
    try:
        pd.to_datetime(df[col], errors='raise')
        date_cols.append(col)
    except:
        pass

# Tab untuk berbagai mode analisis
analysis_mode = st.radio(
    "Pilih Mode Analisis:",
    ["📊 Mode Sederhana (Otomatis)", "🔬 Mode Advanced (Kustom)"],
    help="Mode Sederhana: Dashboard otomatis. Mode Advanced: Anda atur sendiri perhitungannya"
)

if analysis_mode == "🔬 Mode Advanced (Kustom)":
    st.markdown("### Pengaturan Analisis Kustom")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**A. Kelompokkan Berdasarkan:**")
        if categorical_cols:
            group_by_cols = st.multiselect(
                "Pilih kategori untuk pengelompokan:",
                categorical_cols,
                default=[categorical_cols[0]] if categorical_cols else [],
                help="Data akan dikelompokkan berdasarkan kolom ini"
            )
        else:
            st.info("Tidak ada kolom kategori")
            group_by_cols = []
    
    with col2:
        st.markdown("**B. Kolom yang Dihitung:**")
        if numeric_cols:
            value_col = st.selectbox(
                "Pilih kolom angka:",
                numeric_cols,
                help="Kolom ini yang akan dihitung (dijumlah, dirata-rata, dll)"
            )
        else:
            st.warning("Tidak ada kolom angka untuk dihitung!")
            value_col = None
    
    with col3:
        st.markdown("**C. Cara Perhitungan:**")
        agg_options = {
            'sum': '➕ Jumlahkan (Total)',
            'mean': '📊 Rata-rata',
            'median': '📍 Nilai Tengah',
            'count': '🔢 Hitung Jumlah',
            'min': '⬇️ Nilai Terkecil',
            'max': '⬆️ Nilai Terbesar',
            'std': '📏 Standar Deviasi',
        }
        
        agg_type = st.selectbox(
            "Pilih operasi:",
            list(agg_options.keys()),
            format_func=lambda x: agg_options[x],
            help="Operasi matematika yang akan dilakukan pada data"
        )
    
    # Tombol untuk menghitung
    if st.button("🚀 Hitung & Tampilkan Hasil", use_container_width=True, type="primary"):
        if group_by_cols and value_col:
            try:
                # Lakukan agregasi
                if agg_type == 'count':
                    result_df = df.groupby(group_by_cols).size().reset_index(name='Hasil')
                else:
                    result_df = df.groupby(group_by_cols)[value_col].agg(agg_type).reset_index()
                    result_df.columns = list(group_by_cols) + ['Hasil']
                
                # Simpan hasil ke session state
                st.session_state['analysis_result'] = result_df
                st.session_state['analysis_config'] = {
                    'group_by': group_by_cols,
                    'value_col': value_col,
                    'agg_type': agg_type
                }
                st.success("✅ Perhitungan selesai! Lihat hasil di bawah.")
            except Exception as e:
                st.error(f"❌ Error dalam perhitungan: {str(e)}")
        else:
            st.warning("⚠️ Silakan pilih kolom untuk dikelompokkan dan kolom untuk dihitung")

st.divider()

# ===== TAMPILAN DATA & FILTER =====
st.subheader("📋 Langkah 3: Lihat & Filter Data")

# Filter dinamis
with st.expander("🔍 Filter Data (Opsional)", expanded=False):
    st.write("Filter data berdasarkan kondisi tertentu:")
    
    filters = {}
    filter_cols = st.columns(min(3, len(categorical_cols)))
    
    for idx, col in enumerate(categorical_cols[:6]):  # Max 6 filter
        with filter_cols[idx % 3]:
            unique_vals = ['Semua'] + sorted(df[col].dropna().astype(str).unique().tolist())
            filters[col] = st.multiselect(
                f"Filter {col}:",
                unique_vals,
                default=['Semua'],
                key=f"filter_{col}"
            )

# Terapkan filter
df_filtered = df.copy()
for col, filter_val in filters.items():
    if 'Semua' not in filter_val and filter_val:
        df_filtered = df_filtered[df_filtered[col].astype(str).isin(filter_val)]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total Baris", f"{len(df_filtered):,}")
col2.metric("📑 Jumlah Kolom", len(selected_columns))
col3.metric("🔢 Kolom Angka", len(numeric_cols))
col4.metric("🏷️ Kolom Kategori", len(categorical_cols))

# Search
search = st.text_input("🔎 Cari data (ketik apapun):", placeholder="Cari dalam semua kolom...")
if search:
    mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
    df_display = df_filtered[mask]
    st.info(f"Ditemukan {len(df_display)} baris dari pencarian '{search}'")
else:
    df_display = df_filtered

# Tampilkan tabel
st.dataframe(df_display, use_container_width=True, height=400)

# Download
csv_buffer = io.StringIO()
df_display.to_csv(csv_buffer, index=False)
st.download_button(
    "📥 Download Data (CSV)",
    csv_buffer.getvalue(),
    f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    "text/csv",
    use_container_width=True
)

st.divider()

# ===== HASIL ANALISIS =====
if 'analysis_result' in st.session_state and analysis_mode == "🔬 Mode Advanced (Kustom)":
    st.subheader("📊 Hasil Analisis Kustom Anda")
    
    result_df = st.session_state['analysis_result']
    config = st.session_state['analysis_config']
    
    # Info analisis
    st.markdown(f"""
    <div class='info-box'>
        <h4>📋 Detail Analisis:</h4>
        <p>✅ <b>Dikelompokkan berdasarkan:</b> {', '.join(config['group_by'])}</p>
        <p>✅ <b>Kolom yang dihitung:</b> {config['value_col']}</p>
        <p>✅ <b>Cara perhitungan:</b> {get_aggregation_name(config['agg_type'])}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabel hasil
    st.write("**Tabel Hasil:**")
    st.dataframe(result_df, use_container_width=True)
    
    # Visualisasi hasil
    st.write("**Visualisasi:**")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Bar Chart
        if len(config['group_by']) == 1:
            fig_bar = px.bar(
                result_df,
                x=config['group_by'][0],
                y='Hasil',
                title=f"{get_aggregation_name(config['agg_type'])} - {config['value_col']}",
                color='Hasil',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            fig_bar = px.bar(
                result_df,
                x=config['group_by'][0],
                y='Hasil',
                color=config['group_by'][1] if len(config['group_by']) > 1 else None,
                title=f"{get_aggregation_name(config['agg_type'])} - {config['value_col']}",
                barmode='group'
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with viz_col2:
        # Pie Chart (hanya jika 1 group)
        if len(config['group_by']) == 1:
            fig_pie = px.pie(
                result_df,
                values='Hasil',
                names=config['group_by'][0],
                title=f"Proporsi {get_aggregation_name(config['agg_type'])}",
                hole=0.3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            # Sunburst untuk multi-level
            fig_sun = px.sunburst(
                result_df,
                path=config['group_by'],
                values='Hasil',
                title=f"Hierarki {get_aggregation_name(config['agg_type'])}"
            )
            st.plotly_chart(fig_sun, use_container_width=True)
    
    # Download hasil analisis
    csv_result = io.StringIO()
    result_df.to_csv(csv_result, index=False)
    st.download_button(
        "📥 Download Hasil Analisis (CSV)",
        csv_result.getvalue(),
        f"hasil_analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

# ===== VISUALISASI OTOMATIS (Mode Sederhana) =====
if analysis_mode == "📊 Mode Sederhana (Otomatis)":
    st.subheader("📈 Visualisasi Otomatis")
    
    st.info("💡 Dashboard ini menampilkan grafik secara otomatis berdasarkan data Anda")
    
    tab1, tab2, tab3 = st.tabs(["📊 Grafik Kategori", "📈 Grafik Angka", "📋 Statistik"])
    
    with tab1:
        if categorical_cols:
            st.write("**Distribusi Data Kategori:**")
            
            num_charts = min(4, len(categorical_cols))
            cols = st.columns(2)
            
            for idx, col in enumerate(categorical_cols[:num_charts]):
                value_counts = df_display[col].value_counts().reset_index()
                value_counts.columns = [col, 'Jumlah']
                
                with cols[idx % 2]:
                    fig = px.pie(
                        value_counts.head(10),
                        values='Jumlah',
                        names=col,
                        title=f'Distribusi {col}',
                        hole=0.3
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data kategori untuk ditampilkan")
    
    with tab2:
        if numeric_cols:
            st.write("**Analisis Data Angka:**")
            
            for col in numeric_cols[:3]:  # Max 3 kolom
                st.write(f"**{col}:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogram
                    fig_hist = px.histogram(
                        df_display,
                        x=col,
                        title=f'Distribusi {col}',
                        nbins=30,
                        color_discrete_sequence=['#636EFA']
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Box plot
                    fig_box = px.box(
                        df_display,
                        y=col,
                        title=f'Statistik {col}',
                        color_discrete_sequence=['#EF553B']
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Tidak ada data angka untuk ditampilkan")
    
    with tab3:
        st.write("**Ringkasan Statistik:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if numeric_cols:
                st.write("**Statistik Kolom Angka:**")
                st.dataframe(df_display[numeric_cols].describe(), use_container_width=True)
            else:
                st.info("Tidak ada kolom angka")
        
        with col2:
            if categorical_cols:
                st.write("**Info Kolom Kategori:**")
                cat_info = []
                for col in categorical_cols:
                    cat_info.append({
                        'Kolom': col,
                        'Jumlah Unik': df_display[col].nunique(),
                        'Terbanyak': df_display[col].mode()[0] if len(df_display[col].mode()) > 0 else '-'
                    })
                st.dataframe(pd.DataFrame(cat_info), use_container_width=True)
            else:
                st.info("Tidak ada kolom kategori")

# ===== PANDUAN PENGGUNAAN =====
with st.expander("❓ Panduan Penggunaan Dashboard"):
    st.markdown("""
    ### 📚 Cara Menggunakan Dashboard Ini:
    
    #### 1️⃣ **Upload Data:**
    - Siapkan file CSV Anda (bisa dari Excel: Save As → CSV)
    - Upload di sidebar kiri
    
    #### 2️⃣ **Pilih Kolom:**
    - Centang kolom yang ingin Anda analisis
    - Tidak perlu pilih semua, pilih yang penting saja
    
    #### 3️⃣ **Pilih Mode:**
    - **Mode Sederhana**: Dashboard otomatis membuat grafik
    - **Mode Advanced**: Anda tentukan sendiri cara perhitungannya
    
    #### 4️⃣ **Mode Advanced - Contoh Penggunaan:**
    
    **Contoh 1: Menghitung Total Penjualan per Wilayah**
    - Kelompokkan berdasarkan: `Wilayah`
    - Kolom yang dihitung: `Penjualan`
    - Cara perhitungan: `Jumlahkan (Total)`
    
    **Contoh 2: Rata-rata Harga per Kategori Produk**
    - Kelompokkan berdasarkan: `Kategori`
    - Kolom yang dihitung: `Harga`
    - Cara perhitungan: `Rata-rata`
    
    **Contoh 3: Hitung Jumlah Transaksi per Bulan**
    - Kelompokkan berdasarkan: `Bulan`
    - Kolom yang dihitung: (Kolom apapun)
    - Cara perhitungan: `Hitung Jumlah`
    
    #### 5️⃣ **Tips:**
    - Gunakan filter untuk fokus pada data tertentu
    - Download hasil untuk dibuka di Excel
    - Coba berbagai kombinasi kelompok dan perhitungan
    
    #### 📊 **Penjelasan Operasi Perhitungan:**
    - **Jumlahkan**: Menjumlahkan semua nilai (misal: total penjualan)
    - **Rata-rata**: Nilai tengah dari semua data
    - **Nilai Tengah**: Median, nilai di posisi tengah
    - **Hitung Jumlah**: Menghitung berapa banyak baris data
    - **Nilai Terkecil/Terbesar**: Mencari nilai minimum/maksimum
    """)

# ===== FOOTER =====
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem 0;'>
    <p>📊 Universal Data Dashboard | Untuk Semua Jenis Data</p>
    <p style='font-size: 0.8rem;'>Inventory • Penjualan • Keuangan • HR • dan lainnya</p>
</div>
""", unsafe_allow_html=True)