from lib import load_file, parseAlts
import sys

if len(sys.argv) != 2:
    print("Usage: python3 parseAlts.py <file_path>")
    quit()

file = load_file(sys.argv[1])

output = []
for variant in file:
    if variant.startswith('#'): 
        output.append(variant)
        continue
    for goodline in parseAlts(variant):
        output.append(goodline)

with open(sys.argv[1].strip().split('.')[0]+'.sepAlts.vcf', 'w') as opened:
    opened.write(''.join(output))