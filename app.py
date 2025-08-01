import streamlit as st
import vcf
import requests
import pandas as pd
import io

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
    except:
        return 'error'

def parse_vcf(vcf_file):
    vcf_reader = vcf.Reader(vcf_file)
    rows = []
    for record in vcf_reader:
        chrom = record.CHROM
        pos = record.POS
        ref = record.REF
        alt = str(record.ALT[0])
        qual = record.QUAL
        clinvar = annotate_variant(chrom, pos, ref, alt)
        rows.append({
            'CHROM': chrom,
            'POS': pos,
            'REF': ref,
            'ALT': alt,
            'QUAL': qual,
            'ClinVar': clinvar
        })
    return pd.DataFrame(rows)

st.title("VCF Variant Annotator (Streamlit)")
st.write("Upload a `.vcf` file to annotate variants using ClinVar (via MyVariant.info API)")

uploaded_file = st.file_uploader("Choose a VCF file", type="vcf")

if uploaded_file is not None:
    vcf_io = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    try:
        df = parse_vcf(vcf_io)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "annotated_variants.csv", "text/csv")
    except Exception as e:
        st.error(f"Error processing VCF: {e}")
