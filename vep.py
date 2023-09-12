from lib import vep
import sys

if len(sys.argv) != 5 and len(sys.argv) != 3:
    print('Usage: python3 vep.py <input_snv> <input_sv> <output_snv> <output_sv>')
    quit()

if len(sys.argv) == 5:
    vep(
        sys.argv[1], 
        sys.argv[2], 
        sys.argv[3], 
        sys.argv[4]
        )
elif len(sys.argv) == 3:
    vep(
        sys.argv[1], 
        sys.argv[2]
        )