import os
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
            if file.endswith('_match.csv'):
                param = file.split('_')
                sdk = param[-2]
                count = param[-4]
                depth = param[-6]
                model = param[-8]
                data.append({'date': dir, 'model': model, 'depth': depth, 'count': count, 'sdk': sdk})
    reverse_data = reversed(data)
    #print(directories)
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
        if file.endswith('log.txt'):
            log = file

    param = line.split('_')
    sdk = param[-2]
    count = param[-4]
    depth = param[-6]
    model = param[-8]

    match_df = pd.read_csv(os.path.join('report', id, match_file))
    mismatch_df = pd.read_csv(os.path.join('report', id, mismatch_file))

    # Парсим лог файл
    log_file = open(os.path.join('report', id, log), encoding='UTF-8').readlines()
    err = log_file[-2].split(':')[-1]

    return render_template('single_report.html', **locals())

if __name__ == '__main__':
    app.run(host='192.168.65.156', port=8000)