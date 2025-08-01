import requests
import time

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

    except Exception as e:
        return {'acmg': 'Error', 'clinvar': 'Error'}


