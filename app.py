import os, yaml
import pandas as pd
from flask import Flask
from flask import render_template

app = Flask(__name__, static_folder='report/')

@app.route('/')
def main():
    data = []
    directories = os.listdir(os.path.join('report'))
    for dir in directories:
        sub_directories = os.listdir(os.path.join('report', dir))
        for file in sub_directories:
            if file.endswith('params.yml'):
                params = {}
                try:
                    params = yaml.load(open(os.path.join('report', dir, file), 'r'), Loader=yaml.SafeLoader)
                    result = yaml.load(open(os.path.join('report', dir, 'result.yml'), 'r'), Loader=yaml.SafeLoader)
                except:
                    result = {}

                params.update({'date': dir, 'result': result})

                data.append(params)
    reverse_data = reversed(data)
    return render_template('list_reports.html', directories=reverse_data)

@app.route('/report/<id>')
def single_report(id):
    files_report = os.listdir(os.path.join('report', id))
    for file in files_report:
        if file.endswith('_match.csv'):
            match_file = file
        if file.endswith('_mismatch.csv'):
            mismatch_file = file
        if file.endswith('_line.png'):
            line = file
        if file.endswith('params.yml'):
            params = file
        if file.endswith('result.yml'):
            result = file

    match_df = pd.read_csv(os.path.join('report', id, match_file))
    mismatch_df = pd.read_csv(os.path.join('report', id, mismatch_file))

    params_dict = {}
    try:
        params_dict = yaml.load(open(os.path.join('report', id, params), 'r'), Loader=yaml.SafeLoader)
        result_dict = yaml.load(open(os.path.join('report', id, result), 'r'), Loader=yaml.SafeLoader)
    except:
        result_dict = {}

    params_dict.update({'date': id, 'result': result_dict})

    return render_template('single_report.html', **locals())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)