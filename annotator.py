import requests
import time

def annotate_variant(var):
    chrom = var['chrom']
    pos = var['pos']
    ref = var['ref']
    alt = var['alt']
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

