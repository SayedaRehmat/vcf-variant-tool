import streamlit as st
import vcfpy
import requests
import pandas as pd
import io
from report_generator import generate_pdf

# Annotate variant using MyVariant.info
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

# Parse uploaded VCF file
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

# Streamlit UI
st.set_page_config(page_title="VCF ClinVar Annotator", layout="wide")
st.title("🧬 VCF Variant Annotator + ACMG Classifier")

st.markdown("Upload a `.vcf` file to classify variants using ClinVar & ACMG rules")

uploaded_file = st.file_uploader("Upload VCF File", type=["vcf"])

if uploaded_file is not None:
    try:
        with io.TextIOWrapper(uploaded_file, encoding='utf-8') as vcf_io:
            df = parse_vcf(vcf_io)
            st.success("✅ File annotated successfully!")
            st.dataframe(df)

            # CSV Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "annotated_variants.csv", "text/csv")

            # PDF Download
            if st.button("📄 Generate PDF Report"):
                pdf_path = "clinical_report.pdf"
                generate_pdf(df, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, "clinical_report.pdf")

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("📂 Please upload a `.vcf` file.")
