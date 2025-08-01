import streamlit as st
import vcfpy
import requests
import pandas as pd
import io
from report_generator import generate_pdf

# ─────────── Variant Annotation Logic ───────────
def annotate_variant(chrom, pos, ref, alt):
    hgvs = f"{chrom}:g.{pos}{ref}>{alt}"
    url = f"https://myvariant.info/v1/variant/{hgvs}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return {'acmg': 'Uncertain', 'clinvar': 'NA'}

        data = res.json()
        clinvar = data.get('clinvar', {}).get('clinical_significance', 'NA')
        af = data.get('gnomad', {}).get('af', 0)
        rules = []
        if af is not None:
            if af < 0.0001:
                rules.append('PM2')
            elif af > 0.05:
                rules.append('BA1')
        if 'mutationtaster' in data:
            rules.append('PP3')

        if 'pathogenic' in str(clinvar).lower():
            acmg = 'Likely Pathogenic'
        elif 'benign' in str(clinvar).lower():
            acmg = 'Likely Benign'
        else:
            acmg = 'Uncertain'

        return {
            'clinvar': clinvar,
            'gnomad_af': af,
            'acmg': acmg,
            'rules_applied': rules
        }

    except Exception:
        return {'acmg': 'Error', 'clinvar': 'Error'}

# ─────────── VCF File Parsing ───────────
def parse_vcf(file_obj):
    reader = vcfpy.Reader(file_obj)
    records = []
    for record in reader:
        chrom = record.CHROM
        pos = record.POS
        ref = record.REF
        alt = record.ALT[0].value
        qual = record.QUAL
        annotation = annotate_variant(chrom, pos, ref, alt)
        records.append({
            'CHROM': chrom,
            'POS': pos,
            'REF': ref,
            'ALT': alt,
            'QUAL': qual,
            'ClinVar': annotation['clinvar'],
            'gnomAD_AF': annotation.get('gnomad_af'),
            'ACMG': annotation.get('acmg'),
            'Rules': ', '.join(annotation.get('rules_applied', []))
        })
    return pd.DataFrame(records)

# ─────────── Streamlit App ───────────
st.set_page_config(page_title="VCF Lab Tool", layout="wide")
st.title("🧬 Lab VCF Annotation Tool + Secure Login")

# 🔒 Require login
if "user" not in st.session_state:
    st.warning("🔐 Please login first using `login.py`.")
    st.stop()

st.success(f"Welcome, {st.session_state['user']}")

uploaded_file = st.file_uploader("Upload your `.vcf` file", type=["vcf"])

if uploaded_file:
    try:
        with io.TextIOWrapper(uploaded_file, encoding='utf-8') as vcf_io:
            df = parse_vcf(vcf_io)
            st.session_state["df"] = df
            st.success("✅ File processed successfully!")
            st.dataframe(df)

            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "annotated_variants.csv")

            # Download PDF
            if st.button("📄 Generate PDF"):
                generate_pdf(df, "clinical_report.pdf")
                with open("clinical_report.pdf", "rb") as f:
                    st.download_button("Download PDF", f, "clinical_report.pdf")
    except Exception as e:
        st.error(f"❌ Error processing VCF: {e}")
else:
    st.info("📂 Upload a file to continue.")
