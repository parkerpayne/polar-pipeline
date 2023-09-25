from lib import mergeFiles, addToolsColumn, collapseDuplicateRows
import sys

if len(sys.argv) != 6:
    print('Usage: python3 merge.py <vep_snv> <vep_sv> <snipeff> <sniffles> <output>')
    quit()

output = mergeFiles(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

output = addToolsColumn(output)

output = collapseDuplicateRows(output)

with open(sys.argv[5], 'w') as opened:
    opened.write(''.join(output))