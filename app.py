from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, send_from_directory
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from datetime import datetime
from lib import update_db
from tasks import process
import urllib.parse
import configparser
import subprocess
import psycopg2
import hashlib
import time
import os


app = Flask(__name__)



db_config = {
    'dbname': 'polarDB',
    'user': 'threadripper',
    'password': 'Epididymis0!',
    'host': 'localhost',
    'port': '5432',
}

conn = psycopg2.connect(**db_config)

CONFIG_FILE_PATH = '/home/threadripper/shared_storage/webapp/polarPipeline/assets/config.ini'

base_path = '/mnt'

@app.route('/browse/<path:path>')
@app.route('/')
def browse(path=None):
    if path is None:
        path = base_path

    full_path = os.path.join('/', path)
    directory_listing = {}
    for item in os.listdir(full_path):
        is_dir = False
        if os.path.isdir(os.path.join(full_path, item)):
            is_dir = True
        directory_listing[item] = is_dir
    up_level_path = os.path.dirname(path)
    
    bed_files = os.listdir('/home/threadripper/shared_storage/shared_resources/bed_files')
    gene_sources = os.listdir('/home/threadripper/shared_storage/shared_resources/gene_source')
    clair_models = os.listdir('/home/threadripper/shared_storage/shared_resources/clair_models')
    reference_files = os.listdir('/home/threadripper/shared_storage/shared_resources/reference_files')
    for item in reference_files:
        if item.endswith('.fai') or item.endswith('.index'):
            reference_files.remove(item)

    return render_template('index.html', current_path=full_path, directory_listing=directory_listing, up_level_path=up_level_path, bed_files=bed_files, gene_sources=gene_sources, clair_models = clair_models, reference_files = reference_files)
# @app.route('/')
# def index():
#     directory_listing = {}
#     for item in os.listdir(base_path):
#         is_dir = False
#         if os.path.isdir(os.path.join(base_path, item)):
#             is_dir = True
#         directory_listing[item] = is_dir
#     up_level_path = os.path.dirname(base_path)
#     return render_template('index.html', current_path=base_path, directory_listing=directory_listing, up_level_path=up_level_path)

# @app.route('/browse/<path:path>')
# def browse(path):
#     full_path = os.path.join('/', path)
#     directory_listing = {}
#     for item in os.listdir(full_path):
#         is_dir = False
#         if os.path.isdir(os.path.join(full_path, item)):
#             is_dir = True
#         directory_listing[item] = is_dir
#     up_level_path = os.path.dirname(path)
#     return render_template('index.html', current_path=full_path, directory_listing=directory_listing, up_level_path=up_level_path)

@app.template_filter('urlencode')
def urlencode_filter(s):
    return urllib.parse.quote(str(s))

@app.template_filter('urldecode')
def urldecode_filter(s):
    return urllib.parse.unquote(s)

@app.route('/trigger_processing', methods=['POST'])
def trigger_processing():
    path = request.json.get("path")
    clair_model = request.json.get("clair")
    grch_reference = request.json.get("grch_reference")
    grch_bed = request.json.get("grch_bed")
    chm_reference = request.json.get("chm_reference")
    chm_bed = request.json.get("chm_bed")
    grch_gene = request.json.get("grch_gene")
    
    file_name = path.strip().split('/')[-1].split('.')[0]
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    if grch_reference != 'none':
        concatenated_string = file_name + current_time
        id = hashlib.sha256(concatenated_string.encode()).hexdigest()
        process(path, clair_model, grch_gene, grch_gene, grch_reference, id)
        # print(path, clair_model, grch_reference, grch_bed, grch_gene)
    if chm_reference != 'none':
        concatenated_string = file_name + 'T2T' + current_time
        id = hashlib.sha256(concatenated_string.encode()).hexdigest()
        # print(path, clair_model, chm_reference, chm_bed)

    return 'hi'


# @app.route('/file_chosen/<path:path>/<clair_model>/<gene_source>/<bed_file>/<reference_file>')
# def file_chosen(path, clair_model, gene_source, bed_file, reference_file):
    
#     file_name = path.strip().split('/')[-1].split('.')[0]

#     current_time = datetime.now().strftime("%Y%m%d%H%M%S")
#     concatenated_string = file_name + current_time
#     id = hashlib.sha256(concatenated_string.encode()).hexdigest()

#     # try:
#     #     query = "INSERT INTO progress (file_name, status, id, clair_model, bed_file, reference, gene_source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
#     #     with conn.cursor() as cursor:
#     #         cursor.execute(query, (file_name, 'waiting', id, clair_model, bed_file, reference_file, gene_source))
#     #     conn.commit()
#     # except Exception as e:
#     #     print(f"Error updating the database: {e}")
#     #     conn.rollback()
#     # cursor.close()

#     print(path, clair_model, gene_source, bed_file, reference_file)
    

#     # process.delay('/'+path, clair_model, gene_source, bed_file, reference_file, id)
    
#     time.sleep(1)

#     return redirect(url_for('dashboard'))

# uploading = False
# @app.route('/upload', methods=['POST'])
# def upload():
#     print(request.files)
#     if 'file' in request.files:
#         uploaded_file = request.files['file']
#         file_name = uploaded_file.filename

#         # Remove the file extension
#         file_name_sans_extension = file_name.split('.')[0]

#         # Get the current timestamp
#         current_time = datetime.now()

#         # Insert a new row into the progress table
#         try:
#             query = "INSERT INTO progress (file_name, status) VALUES (%s, %s)"
#             with conn.cursor() as cursor:
#                 cursor.execute(query, (file_name_sans_extension, 'waiting'))
#             conn.commit()
#         except Exception as e:
#            print(f"Error updating the database: {e}")
#            conn.rollback()
#         cursor.close()

#         # Create a directory with the same name as the uploaded file
#         save_directory = os.path.join("/home/threadripper/shared_storage/workspace/", file_name_sans_extension)
#         os.makedirs(save_directory, exist_ok=True)
#         # Save the uploaded file inside the created directory
#         uploaded_file.save(os.path.join(save_directory, file_name))

#         process.delay(file_name)

#         return redirect(url_for('dashboard'))
#     else:

#         return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor. execute("SELECT file_name, status, id FROM progress ORDER BY start_time")
        rows = cursor.fetchall()

        cursor.execute("SELECT * FROM status;")
        statusList = cursor.fetchall()
        status = []
        for item in statusList:
            status.append(item[0] + ': ' + item[1])

        cursor.close()
        conn.close()


        return render_template('dashboard.html', rows = rows, status=status)
        # return render_template('dashboard.html', rows = rows)
    except Exception as e:
        return f"Error: {e}"
    
@app.route('/deleteRun/<string:id>')
def deleteRun(id):
    print(id)
    # conn = psycopg2.connect(**db_config)
    # try:
    #     query = f"DELETE FROM progress WHERE id = '{id}'"
    #     with conn.cursor() as cursor:
    #         cursor.execute(query)
    #         print(query)
    #     conn.commit()
    # except Exception as e:
    #     print(f"Error updating the database: {e}")
    #     conn.rollback()
    # finally:
    #     conn.close()
    return redirect(url_for('dashboard'))

# Function to read the config.ini file and return the configuration values as a dictionary
def read_config(computer_name=None):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    if computer_name is None or computer_name not in config.sections():
        computer_name = 'Default'

    return parse_config_dict(config[computer_name])

def parse_config_dict(config_dict):
    parsed_dict = {}
    for key, value in config_dict.items():
        key = key
        value = value

        parsed_dict[key] = value

    return parsed_dict

# Function to save the updated configurations to the config.ini file
def save_config(computer_name, config_values):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    if not config.has_section(computer_name):
        config.add_section(computer_name)

    for key, value in config_values.items():
        value = str(value)  # Convert other data types to strings

        config.set(computer_name, key, value)

    with open(CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)

def get_all_configurations():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    all_configurations = {}
    for section_name in config.sections():
        all_configurations[section_name] = parse_config_dict(config[section_name])
    return all_configurations

@app.route('/id')
def id():
 return render_template('id.html')

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    all_configurations = get_all_configurations()
    
    clair_models = []
    bed_files = []
    gene_sources = []
    reference_files = []

    bed_files = os.listdir('/home/threadripper/shared_storage/shared_resources/bed_files')
    gene_sources = os.listdir('/home/threadripper/shared_storage/shared_resources/gene_source')
    clair_models = os.listdir('/home/threadripper/shared_storage/shared_resources/clair_models')
    reference_files = os.listdir('/home/threadripper/shared_storage/shared_resources/reference_files')

    if request.method == 'POST':
        computer_name = request.form['computer_name']
        config_values = read_config(computer_name)
        return render_template('configuration.html', computer_name=computer_name, config_values=config_values, all_configurations=all_configurations, clair_models=clair_models, bed_files=bed_files, gene_sources=gene_sources, reference_files=reference_files)
    elif request.method == 'GET':
        # If no computer name is specified, show the default configuration
        config_values = read_config()
        return render_template('configuration.html', computer_name=None, config_values=config_values, all_configurations=all_configurations, clair_models=clair_models, bed_files=bed_files, gene_sources=gene_sources, reference_files=reference_files)


@app.route('/add_computer', methods=['POST'])
def add_computer():
    if request.method == 'POST':
        computer_name = request.form['computer_name']

        # Read the default configuration
        default_config_values = read_config()

        # Create a new section in the config for the new computer and copy the default configurations
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        if not config.has_section(computer_name):
            config.add_section(computer_name)
            for key, value in default_config_values.items():
                config.set(computer_name, str(key), str(value))

            # Save the updated config.ini file
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)

        # Save the default values for the new computer
        save_config(computer_name, default_config_values)

    return redirect(url_for('configuration'))

@app.route('/save_configuration', methods=['POST'])
def save_configuration():
    if request.method == 'POST':
        computer_name = request.form['computer_name']
        config_values = {}

        for key in request.form:
            if key != 'computer_name':
                value = request.form[key]
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        pass  # Keep the value as a string

                config_values[key] = value

        save_config(computer_name, config_values)

    return redirect(url_for('configuration'))

@app.route('/delete_configuration', methods=['POST'])
def delete_configuration():
    if request.method == 'POST':
        computer_name = request.form['computer_name']

        # Read the config file
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)

        # Check if the configuration exists
        if config.has_section(computer_name):
            # Remove the configuration section
            config.remove_section(computer_name)

            # Save the updated config.ini file
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)

    return redirect(url_for('configuration'))

@app.route('/setup')
def setup():
 return render_template('setup.html')


@app.route('/info/<string:id>')
def info(id):

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM progress WHERE id = %s", (id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row[3]:
            runtime = str(row[3] - row[1])
            runtime = runtime.split('.')[0]
            startTime = str(row[1])
            startTime = startTime.split('.')[0]
            endTime = str(row[3])
            endTime = endTime.split('.')[0]
        elif row[1]:
            runtime = str(datetime.now() - row[1])
            runtime = runtime.split('.')[0]
            startTime = str(row[1])
            startTime = startTime.split('.')[0]
            endTime = 'N/A'
        else:
            runtime = 'N/A'
            startTime = 'N/A'
            endTime = 'N/A'
        
        file_name = row[0]
        status = str(row[2])
        computer = str(row[4])

        folder_list = os.listdir('/home/threadripper/shared_storage/workspace')
        
        statsPath = os.path.join('/mnt/synology3/polar_pipeline', startTime.replace(' ', '_').replace(':', '.')+'_'+file_name, '0_nextflow/run_summary.txt')
        if os.path.isfile(statsPath):
            rows = []
            for line in open(statsPath, 'r'):
                splitline = line.split('\t')
                rows.append([splitline[0], splitline[1]])
        else:
            rows = []
        
        clair_model = row[7]
        bed_file = row[8]
        reference = row[9]
        gene_source = row[10]
        
        return render_template('info.html', file_name = file_name, startTime = startTime, endTime = endTime, status = status, runtime=runtime, folder_list = folder_list, computer=computer, id=id, rows=rows, clair_model=clair_model, bed_file=bed_file, reference=reference, gene_source=gene_source)
    except Exception as e:
        return f"Error: {e}"
    
@app.route('/get_info/<string:id>')
def get_info(id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM progress WHERE id = %s", (id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row[3]:
            runtime = str(row[3] - row[1])
            runtime = runtime.split('.')[0]
            startTime = str(row[1])
            startTime = startTime.split('.')[0]
            endTime = str(row[3])
            endTime = endTime.split('.')[0]
        elif row[1]:
            runtime = str(datetime.now() - row[1])
            runtime = runtime.split('.')[0]
            startTime = str(row[1])
            startTime = startTime.split('.')[0]
            endTime = 'N/A'
        else:
            runtime = 'N/A'
            startTime = 'N/A'
            endTime = 'N/A'

        status = str(row[2])
        computer = str(row[4])

        info = {
            "startTime": startTime,
            "endTime": endTime,
            "runtime": runtime,
            "status": status,
            "computer": computer
        }

        return jsonify(info)
    except Exception as e:
        return str(e)
    
@app.route('/abort/<string:id>')
def abort(id):
    update_db(id, 'signal', 'stop')
    update_db(id, 'status', 'cancelling')
    time.sleep(1)
    return redirect(url_for('dashboard'))
