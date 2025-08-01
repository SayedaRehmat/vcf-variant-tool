def print_report(variants):
    print("CHROM\tPOS\tREF\tALT\tQUAL\tClinVar")
    for v in variants:
        print(f"{v['chrom']}\t{v['pos']}\t{v['ref']}\t{v['alt']}\t{v['qual']}\t{v['clinvar']}")

