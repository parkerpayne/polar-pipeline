from lib import nextflow
import sys

if len(sys.argv) != 5:
    print('Usage: python3 nextflow.py <input_file_path> <output_directory> <reference_file_path> <clair3_model_path>')
    quit()

input_file = sys.argv[1]
output_directory = sys.argv[2]
reference_file = sys.argv[3]
clair3_model_path = sys.argv[4]

nextflow(input_file, output_directory, reference_file, clair3_model_path)