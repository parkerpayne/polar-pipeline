from lib import mergeFiles
import sys

if len(sys.argv) != 6:
    print('Usage: python3 merge.py <vep_snv> <vep_sv> <snipeff> <sniffles> <output>')
    quit()

mergeFiles(
    sys.argv[1],
    sys.argv[2],
    sys.argv[3],
    sys.argv[4],
    sys.argv[5]
    )