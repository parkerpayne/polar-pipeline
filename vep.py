from lib import vep
import sys

if len(sys.argv) != 6 and len(sys.argv) != 4:
    print('Usage: python3 vep.py <input_snv> <input_sv> <reference_path> <threads> <output_snv> <output_sv>')
    print('\tOptional params:')
    print('\tthreads default: 30')
    print('\toutput_snv default: same directory, runName_vep_snv.tsv')
    print('\toutput_snv default: same directory, runName_vep_sv.tsv')
    quit()

if len(sys.argv) == 7:
    vep(
        sys.argv[1], 
        sys.argv[2],
        sys.argv[3], 
        sys.argv[4],
        sys.argv[5],
        sys.argv[6]
        )
elif len(sys.argv) == 4:
    vep(
        sys.argv[1], 
        sys.argv[2],
        sys.argv[3]
        )
elif len(sys.argv) == 5:
    vep(sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4]
        )