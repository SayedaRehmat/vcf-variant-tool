import vcfpy
import requests
import pandas as pd
import argparse

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

def parse_vcf(path):
    reader = vcfpy.Reader.from_path(path)
    records = []
    for record in reader:
        chrom = record.CHROM
        pos = record.POS
        ref = record.REF
        alt = record.ALT[0].value
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VCF Variant Annotator")
    parser.add_argument("vcf_path", help="Path to the .vcf file")
    parser.add_argument("--out", help="CSV output file (optional)", default="annotated_output.csv")
    args = parser.parse_args()

    df = parse_vcf(args.vcf_path)
    print(df.to_string(index=False))

    df.to_csv(args.out, index=False)
    print(f"\n✅ Results saved to {args.out}")
