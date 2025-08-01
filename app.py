import streamlit as st
import vcfpy
import requests
import pandas as pd
import io

# ─────────────────────────────────────────────
# Function to annotate a variant using myvariant.info
# ─────────────────────────────────────────────
def annotate_variant(chrom, pos, ref, alt):
    hgvs = f"{chrom}:g.{pos}{ref}>{alt}"
    url = f"https://myvariant.info/v1/variant/{hgvs}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return data.get('clinvar', {}).get('clinical_significance', 'NA')
        else:
            return 'Not found'
    except Exception as e:
        return f"Error: {e}"

# ─────────────────────────────────────────────
# Function to parse VCF and return DataFrame
# ─────────────────────────────────────────────
def parse_vcf(file_obj):
    reader = vcfpy.Reader(file_obj)
    records = []
    for record in reader:
        chrom = record.CHROM
        pos = record.POS
        ref = record.REF
        alt = record.ALT[0].value  # get alt string
        qual = record.QUAL
        clinvar = annotate_variant(chrom, pos, ref, alt)
        records.append({
            'CHROM': chrom,
            'POS': pos,
            'REF': ref,
            'ALT': alt,
            'QUAL': qual,
            'ClinVar': clinvar
        })
    return pd.DataFrame(records)

# ─────────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────────
st.set_page_config(page_title="VCF ClinVar Annotator", layout="wide")
st.title("🧬 VCF Variant Annotator")

st.markdown("""
Upload a `.vcf` file to see real-time **ClinVar annotations** using the [MyVariant.info](https://myvariant.info) API.
""")

uploaded_file = st.file_uploader("Upload VCF File", type=["vcf"])

if uploaded_file is not None:
    try:
        with io.TextIOWrapper(uploaded_file, encoding='utf-8') as vcf_io:
            df = parse_vcf(vcf_io)
            st.success("✅ VCF parsed and annotated successfully!")
            st.dataframe(df)

            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "annotated_variants.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ Error reading VCF: {e}")
else:
    st.info("📂 Please upload a `.vcf` file to begin.")
