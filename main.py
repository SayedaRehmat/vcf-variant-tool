from src.parser import parse_vcf
from src.annotator import annotate_variant
from src.reporter import print_report

vcf_path = "data/test_sample.vcf"

variants = parse_vcf(vcf_path)

for var in variants:
    annotation = annotate_variant(var)
    var['clinvar'] = annotation

print_report(variants)

