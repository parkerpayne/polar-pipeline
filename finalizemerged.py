from lib import load_file, intersect, addToolsColumn_addGeneSource, collapseDuplicateRows, findCandidates
import sys

gene_path = '/mnt/shared_storage/shared_resources/gene_source/GENE_SOURCE_column.txt'
bed_path = '/mnt/shared_storage/shared_resources/bed_files/intersect_wiht_these_clinically_relevant3.bed'

if len(sys.argv) != 4 and len(sys.argv) != 5:
    print('Usage: python3 finalizemerged.py <merged_file> <output> <bed_file> <gene_file>')
    quit()

merged_path = sys.argv[1]
run_name = merged_path.strip().split('/')[-1].split('.')[0]
output_path = '/'.join(merged_path.strip().split('/')[:-1])+'/'+run_name+'_finalCandidates.vcf'

if sys.argv[2]:
    output_path = sys.argv[2]
if sys.argv[3]:
    bed_path = sys.argv[3]
if sys.argv[4]:
    gene_path = sys.argv[4]


output = intersect(load_file(merged_path), load_file(bed_path))

output = addToolsColumn_addGeneSource(output, load_file(gene_path))

output = collapseDuplicateRows(output)

output = findCandidates(output)

with open(output_path, 'w') as opened:
    opened.write(''.join(output))

