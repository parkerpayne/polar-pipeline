from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, send_from_directory
from wtforms import StringField, SubmitField
from tasks import process, processT2T
from flask_wtf import FlaskForm
from datetime import datetime
from lib import update_db
import urllib.parse
import configparser
import subprocess
import psycopg2
import hashlib
import time
import svg
import ast
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
FIGURE_PRESETS_CONFIG = '/home/threadripper/shared_storage/webapp/polarPipeline/assets/presets.ini'

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
        try:
            query = "INSERT INTO progress (file_name, status, id, clair_model, bed_file, reference, gene_source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            with conn.cursor() as cursor:
                cursor.execute(query, (file_name, 'waiting', id, clair_model, ', '.join(grch_bed), grch_reference, ', '.join(grch_gene)))
            conn.commit()
        except Exception as e:
            print(f"Error updating the database: {e}")
            conn.rollback()
        cursor.close()
        process.delay(path, clair_model, grch_gene, grch_bed, grch_reference, id)
        # print(path, clair_model, grch_reference, grch_bed, grch_gene)
    if chm_reference != 'none':
        file_name = file_name+'_T2T'
        concatenated_string = file_name + 'T2T' + current_time
        id = hashlib.sha256(concatenated_string.encode()).hexdigest()
        try:
            query = "INSERT INTO progress (file_name, status, id, clair_model, bed_file, reference, gene_source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            with conn.cursor() as cursor:
                cursor.execute(query, (file_name, 'waiting', id, clair_model, ', '.join(chm_bed), chm_reference, 'N/A'))
            conn.commit()
        except Exception as e:
            print(f"Error updating the database: {e}")
            conn.rollback()
        cursor.close()
        processT2T.delay(path, clair_model, chm_bed, chm_reference, id)
        # print(path, clair_model, chm_reference, chm_bed)

    return redirect(url_for('dashboard'))


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
@app.route('/upload/<string:filetype>', methods=['POST'])
def upload(filetype):
    print('request:',request.files)
    print('filetype:',filetype)
    uploaded_file = request.files['file']
    file_name = uploaded_file.filename

    # Remove the file extension
    file_name_sans_extension = file_name.strip().split('/')[-1].split('.')[0]

    print('filename:',file_name)
    print('sans extension:',file_name_sans_extension)

    # Create a directory with the same name as the uploaded file
    save_directory = os.path.join(f"/home/threadripper/shared_storage/shared_resources/", filetype)

    # Save the uploaded file inside the created directory
    uploaded_file.save(os.path.join(save_directory, file_name))

    if file_name.endswith('.gz'):
        if 'tar' not in file_name:
            subprocess.run(['pigz', '-d', os.path.join(save_directory, file_name)], cwd=save_directory)
        else:
            subprocess.run(['tar', '-xf', os.path.join(save_directory, file_name)], cwd=save_directory)
            subprocess.run(['rm', os.path.join(save_directory, file_name)], cwd=save_directory)

    return redirect(url_for('configuration'))

@app.route('/remove/<path:removepath>')
def remove(removepath):
    print(removepath)
    base = '/home/threadripper/shared_storage/shared_resources'
    full_path = os.path.join(base, removepath)
    if os.path.isdir(full_path):
        subprocess.run(['rm', '-r', full_path])
    elif os.path.isfile(full_path):
        subprocess.run(['rm', full_path])
    return redirect(url_for('configuration'))

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
    conn = psycopg2.connect(**db_config)
    try:
        query = f"DELETE FROM progress WHERE id = '{id}'"
        with conn.cursor() as cursor:
            cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Error updating the database: {e}")
        conn.rollback()
    finally:
        conn.close()
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

@app.route('/figuregenerator')
def figuregenerator():
    return render_template('figuregenerator.html')

def save_preset(preset_name, preset_vals):
    config = configparser.ConfigParser()
    config.read(FIGURE_PRESETS_CONFIG)

    if not config.has_section(preset_name):
        config.add_section(preset_name)

    for key, value in preset_vals.items():
        value = str(value)  # Convert other data types to strings

        config.set(preset_name, key, value)

    with open(FIGURE_PRESETS_CONFIG, 'w') as configfile:
        config.write(configfile)

@app.route('/saveState', methods=['POST'])
def saveState():
    preset_name = request.json.get("presetname")
    homo = request.json.get("homo")
    abproteinname = request.json.get("abproteinname")
    proteinname = request.json.get("proteinname")
    if homo == True:
        homolen = request.json.get("homolen")
        homostructures = request.json.get("homostructures")
        homofeatures = request.json.get("homofeatures")

        preset_vals = {
            "homo": homo,
            "abproteinname": abproteinname,
            "proteinname": proteinname,
            "homolen": homolen,
            "homostructures": homostructures,
            "homofeatures": homofeatures
        }

    else:
        leftlen = request.json.get("leftlen")
        leftstructures = request.json.get("leftstructures")
        rightlen = request.json.get("rightlen")
        rightstructures = request.json.get("rightstructures")
        leftfeatures = request.json.get("leftfeatures")
        rightfeatures = request.json.get("rightfeatures")

        preset_vals = {
            "homo": homo,
            "abproteinname": abproteinname,
            "proteinname": proteinname,
            "leftlen": leftlen,
            "leftstructures": leftstructures,
            "rightlen": rightlen,
            "rightstructures": rightstructures,
            "leftfeatures": leftfeatures,
            "rightfeatures": rightfeatures
        }

    save_preset(str(preset_name), preset_vals)

    response_data = {
        "message": "Data received successfully"
    }

    return jsonify(response_data)

def load_presets():
    config = configparser.ConfigParser()
    config.read(FIGURE_PRESETS_CONFIG)
    return config.sections()

@app.route('/loadStates', methods=['POST'])
def loadStates():
    presets = load_presets()
    response_data = {
        "data": presets
    }

    return jsonify(response_data)
    
def load_preset(section_name):
    config = configparser.ConfigParser()
    config.read(FIGURE_PRESETS_CONFIG)
    if section_name in config:
        return parse_config_dict(config[section_name])
    else:
        return None  # Section not found

def parse_config_dict(config_section):
    parsed_data = {}
    for key, value in config_section.items():
        try:
            # Attempt to evaluate the value as literal Python expression
            parsed_value = ast.literal_eval(value)
            if isinstance(parsed_value, list):
                parsed_data[key] = parsed_value
            else:
                parsed_data[key] = parsed_value
        except (SyntaxError, ValueError):
            # If evaluation fails, store the value as is
            parsed_data[key] = value
    return parsed_data

@app.route('/loadState', methods=['POST'])
def loadState():
    preset = request.json.get('preset')

    preset_data = load_preset(preset)
    print(preset_data)

    response_data = {
        "data": preset_data
    }

    return jsonify(response_data)

def customsortfeatures(feature):
    num = -int(feature[1])
    return num

@app.route('/generatefigure', methods=['POST'])
def generatefigure():
    homo = request.json.get("homo")
    abproteinname = request.json.get("abproteinname")
    proteinname = request.json.get("proteinname")

    topbar = []
    bottombar = []
    leftfeatureelements = []
    rightfeatureelements = []
    homobar = []
    homofeatureelements = []

    base = [
        svg.Rect( # BACKGROUND
            fill="white",
            x=0,
            y=0,
            width=480*2,
            height=480
        ),
        svg.Text( # PROTEIN NAME
            text=f'{abproteinname} | {proteinname}',
            x=5,
            y=45,
            fill="black",
            font_family="Sans,Arial",
            font_weight="bold",
            font_size="30",
            font_stretch="ultra-condensed"
        ),
    ]

    if not homo:
        leftlen = request.json.get("leftlen")
        leftstructures = request.json.get("leftstructures")
        rightlen = request.json.get("rightlen")
        rightstructures = request.json.get("rightstructures")
        leftfeatures = request.json.get("leftfeatures")
        rightfeatures = request.json.get("rightfeatures")

        maxlen = max(int(leftlen), int(rightlen))

        base.append(svg.Line( # FIRST LINE
            stroke_width=5,
            stroke="grey",
            x1=50,
            y1=200,
            x2=50+((int(leftlen)/maxlen) * 550) + ((1/maxlen) * 550),
            y2=200
        ))
        base.append(svg.Line( # SECOND LINE
            stroke_width=5,
            stroke="grey",
            x1=50,
            y1=360,
            x2=50+((int(rightlen)/maxlen) * 550) + ((1/maxlen) * 550),
            y2=360
        ))
        base.append(svg.Text( # 0|1 TEXT
            text='0|1',
            x=5,
            y=205,
            fill="black",
            font_family="monospace",
            stroke_width=1,
            font_size=20
        ))
        base.append(svg.Text( # 1|0 TEXT
            text='1|0',
            x=5,
            y=365,
            fill="black",
            font_family="monospace",
            stroke_width=1,
            font_size=20
        ))
        base.append(svg.Text( # TOP AA LENGTH
            text=f'{leftlen} AA',
            x=50+((int(leftlen)/maxlen) * 550) + ((1/maxlen) * 550) + 10,
            y=205,
            fill="black",
            font_family="monospace",
            stroke_width=1,
            font_size=20
        ))
        base.append(svg.Text( # BOTTOM AA LENGTH
            text=f'{rightlen} AA',
            x=50+((int(rightlen)/maxlen) * 550) + ((1/maxlen) * 550) + 10,
            y=365,
            fill="black",
            font_family="monospace",
            stroke_width=1,
            font_size=20
        ))

        for item in leftstructures:
            if len(item) != 4: continue
            fontsize = 20
            if (len(item[0]) * fontsize * (3/5)) > (((int(item[2])-int(item[1]))/maxlen)*550):
                fontsize = (((((int(item[2])-int(item[1]))/maxlen)*550) * 0.9) / (3/5)) / len(item[0])
            topbar.append(
                svg.Rect(
                    fill=item[3],
                    x=50+((int(item[1])/maxlen)*550),
                    y=185,
                    width=(((int(item[2])-int(item[1]))/maxlen)*550),
                    height=30,
                )
            )
            fontcol = "black"
            if item[0] == "DEGEN": fontcol="red"
            print(50+((int(item[1])+int(item[2]))/2))
            topbar.append(
                svg.Text(
                    text=item[0],
                    x=50+((((int(item[1])+int(item[2]))/2)/maxlen)*550)-(fontsize*(3/5)*len(item[0])/2),
                    y=205,
                    fill=fontcol,
                    font_family="monospace",
                    font_size=fontsize
                )
            )
            
        for item in rightstructures:
            if len(item) != 4: continue
            fontsize = 20
            if (len(item[0]) * fontsize * (3/5)) > (((int(item[2])-int(item[1]))/maxlen)*550):
                fontsize = (((((int(item[2])-int(item[1]))/maxlen)*550) * 0.9) / (3/5)) / len(item[0])
            bottombar.append(
                svg.Rect(
                    fill=item[3],
                    x=50+((int(item[1])/maxlen)*550),
                    y=345,
                    width=(((int(item[2])-int(item[1]))/maxlen)*550),
                    height=30,
                )
            )
            fontcol = "black"
            if item[0] == "DEGEN": fontcol="red"
            bottombar.append(
                svg.Text(
                    text=item[0],
                    x=50+((((int(item[1])+int(item[2]))/2)/maxlen)*550)-(fontsize*(3/5)*len(item[0])/2),
                    y=365,
                    fill=fontcol,
                    font_family="monospace",
                    font_size=fontsize
                )
            )
        
        leftfeaturestemp = sorted([x for x in leftfeatures if x], key=customsortfeatures)
        leftfeatureswithoverlap = []
        for i in range(len(leftfeaturestemp)):
            height = 0
            if '^' in leftfeaturestemp[i][0]:
                height = (len(leftfeaturestemp[i][0].split('^'))-1)*30
            leftfeatureswithoverlap.append(leftfeaturestemp[i]+[height])
            print(leftfeatureswithoverlap)
        for item in leftfeatureswithoverlap:
            leftfeatureelements.append(
                svg.Line(
                    stroke_width=3,
                    stroke="red",
                    x1=50+((int(item[1])/maxlen) * 550),
                    y1=185,
                    x2=50+((int(item[1])/maxlen) * 550),
                    y2=155-item[2]
                )
            )
            leftfeatureelements.append(
                svg.Text(
                    text=item[0].replace('^', ''),
                    x=50 + ((int(item[1]) / maxlen) * 550) + 6,
                    y=170-item[2],
                    font_family="monospace",
                    font_size=20
                )
            )
            
        rightfeaturestemp = sorted([x for x in rightfeatures if x], key=customsortfeatures)
        rightfeatureswithoverlap = []
        for i in range(len(rightfeaturestemp)):
            height = 0
            if '^' in rightfeaturestemp[i][0]:
                height = (len(rightfeaturestemp[i][0].split('^'))-1)*30
            rightfeatureswithoverlap.append(rightfeaturestemp[i]+[height])
            print(rightfeatureswithoverlap)
        for item in rightfeatureswithoverlap:
            rightfeatureelements.append(
                svg.Line(
                    stroke_width=3,
                    stroke="red",
                    x1=50+((int(item[1])/maxlen) * 550),
                    y1=345,
                    x2=50+((int(item[1])/maxlen) * 550),
                    y2=315-item[2]
                )
            )
            rightfeatureelements.append(
                svg.Text(
                    text=item[0].replace('^', ''),
                    x=50 + ((int(item[1]) / maxlen) * 550) + 6,
                    y=330-item[2],
                    font_family="monospace",
                    font_size=20
                )
            )
    else:
        homolen = request.json.get("homolen")
        homostructures = request.json.get("homostructures")
        homofeatures = request.json.get("homofeatures")

        base.append(svg.Line( # SECOND LINE
            stroke_width=5,
            stroke="grey",
            x1=50,
            y1=280,
            x2=50+((int(homolen)/int(homolen)) * 550) + ((1/int(homolen)) * 550),
            y2=280
        ))
        base.append(svg.Text( # 1|1 TEXT
            text='1|1',
            x=5,
            y=285,
            fill="black",
            font_family="monospace",
            stroke_width=1,
            font_size=20
        ))
        base.append(svg.Text( # TOP AA LENGTH
            text=f'{homolen} AA',
            x=50+((int(homolen)/int(homolen)) * 550) + ((1/int(homolen)) * 550) + 10,
            y=285,
            fill="black",
            font_family="monospace",
            stroke_width=1,
            font_size=20
        ))
        for item in homostructures:
            if len(item) != 4: continue
            fontsize = 20
            if (len(item[0]) * fontsize * (3/5)) > (((int(item[2])-int(item[1]))/int(homolen))*550):
                fontsize = (((((int(item[2])-int(item[1]))/int(homolen))*550) * 0.9) / (3/5)) / len(item[0])
            homobar.append(
                svg.Rect(
                    fill=item[3],
                    x=50+((int(item[1])/int(homolen))*550),
                    y=265,
                    width=(((int(item[2])-int(item[1]))/int(homolen))*550),
                    height=30,
                )
            )
            fontcol = "black"
            if item[0] == "DEGEN": fontcol="red"
            homobar.append(
                svg.Text(
                    text=item[0],
                    x=50+((((int(item[1])+int(item[2]))/2)/int(homolen))*550)-(fontsize*(3/5)*len(item[0])/2),
                    y=285,
                    fill=fontcol,
                    font_family="monospace",
                    font_size=fontsize
                )
            )
            homofeaturestemp = sorted([x for x in homofeatures if x], key=customsortfeatures)
            homofeatureswithoverlap = []
            for i in range(len(homofeaturestemp)):
                height = 0
                if '^' in homofeaturestemp[i][0]:
                    height = (len(homofeaturestemp[i][0].split('^'))-1)*30
                homofeatureswithoverlap.append(homofeaturestemp[i]+[height])
                print(homofeatureswithoverlap)
            for item in homofeatureswithoverlap:
                homofeatureelements.append(
                    svg.Line(
                        stroke_width=3,
                        stroke="red",
                        x1=50+((int(item[1])/int(homolen)) * 550),
                        y1=265,
                        x2=50+((int(item[1])/int(homolen)) * 550),
                        y2=235-item[2]
                    )
                )
                homofeatureelements.append(
                    svg.Text(
                        text=item[0],
                        x=50 + ((int(item[1]) / int(homolen)) * 550) + 6,
                        y=250-item[2],
                        font_family="monospace",
                        font_size=20
                    )
                )

        # print(homolen)
        # print(homostructures)
        # print(homofeatures)

    canvas = svg.SVG(
        width=480*2,
        height=480,
        elements = base + topbar + bottombar + homobar + leftfeatureelements + rightfeatureelements + homofeatureelements
    )

    svg_string = str(canvas)

    with open('/home/threadripper/shared_storage/webapp/polarPipeline/static/variantFig.svg', 'w') as opened:
        opened.write(svg_string)
    
    response_data = {
        "message": "Data received successfully"
    }

    return jsonify(response_data)

@app.route('/downloadfigure')
def downloadfigure():
    try:
        # Build the path to the image file in the static folder
        image_path = f'static/variantFig.svg'

        # Use Flask's send_file function to send the image as a download
        return send_file(image_path, as_attachment=True)

    except FileNotFoundError:
        # Handle the case where the image file is not found
        return "Image not found", 404

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
        
        statsPath = os.path.join('/mnt/synology3/polar_pipeline', startTime.replace(' ', '_').replace(':', '-')+'_'+file_name, '0_nextflow/run_summary.txt')
        if os.path.isfile(statsPath):
            rows = []
            for line in open(statsPath, 'r'):
                splitline = line.split('\t')
                rows.append([splitline[0], splitline[1]])
        else:
            rows = []
        
        if rows == []:
            statsPath = os.path.join('/mnt/synology3/polar_pipeline', startTime.replace(' ', '_').replace(':', '.')+'_'+file_name, '0_nextflow/run_summary.txt')
            if os.path.isfile(statsPath):
                rows = []
                for line in open(statsPath, 'r'):
                    splitline = line.split('\t')
                    rows.append([splitline[0], splitline[1]])
            else:
                rows = []
        
        clair_model = row[7]
        bed_file = row[8].split(',')
        reference = row[9]
        gene_source = row[10]
        if gene_source == 'N/A':
            gene_source = []
            for item in bed_file:
                gene_source.append('N/A')
        else:
            gene_source = row[10].split(',')
        
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
