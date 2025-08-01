from cyvcf2 import VCF

def parse_vcf(path):
    vcf = VCF(path)
    variant_list = []
    for var in vcf:
        variant = {
            'chrom': var.CHROM,
            'pos': var.POS,
            'ref': var.REF,
            'alt': var.ALT[0],
            'qual': var.QUAL
        }
        variant_list.append(variant)
    return variant_list

