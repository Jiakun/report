#!/usr/bin/python
# -*- coding: utf-8 -*-

from bottle import *
import os
from expert_call import ExpertCallReport


data_path = '../data/expert_call/'
rule_path = '../data/expert_call/rule/'
inter_path = '../report/expert_call/inter/'
output_path = '../report/expert_call/'

# root = '/home/jiakun/PycharmProjects/SummaryReport/'


def listdir(path, type):
    file_list = []
    file_num = 0
    files = os.listdir(path)  # 列出目录下的所有文件和目录
    for line in files:
        if type == "data":
            if line.split(".")[-1] == "csv":
                file_path = os.path.join(path, line)
                file_list.append(file_path)
                file_num += 1
        elif type == "rule":
            file_path = os.path.join(path, line)
            file_list.append(file_path)
            file_num += 1

    return file_num, file_list


@route('/upload')
def upload():
    return '''
        <html>
            <head>
            </head>
            <body>
                <p>请上传 .csv 格式文件</p>
                <form action"/upload" method="post" enctype="multipart/form-data">
                    <label><input type="radio" name="type" value="data" />数据</label>
                    <label><input type="radio" name="type" value="rule" />规则</label>
                    <input type="file" name="data" />
                    <input type="submit" value="Upload" />
                </form>
            </body>
        </html>
    '''


@route('/upload', method='POST')
def do_upload():
    upload_type = request.forms.get('type')
    upload_file = request.files.get('data')
    if upload_type == "data":
        upload_file.save(data_path, overwrite=True)
    elif upload_type == "rule":
        upload_file.save(rule_path, overwrite=True)
    else:
        return "error"
    return "ok"


@route('/download_rule/<file_name:path>')
def download_rule(file_name):
    return static_file(download=file_name, root=rule_path, filename=file_name)


@route('/download_data/<file_name:path>')
def download_data(file_name):
    return static_file(download=file_name, root=data_path, filename=file_name)


@route('/download_result/<file_name:path>')
def download_result(file_name):
    return static_file(download=file_name, root=output_path, filename=file_name)


def get_rule_list():
    html_str = ""
    file_num, file_list = listdir(rule_path, type="rule")
    html_str += "<p>文件数：" + str(file_num) + "</p> <ol>"

    for file_path in file_list:
        file_name = file_path.split("/")[-1]
        html_str += "<li>" + \
                    "<label><input type=\"radio\" name=\"rule\" value=\"" + file_name + "\" />" +\
                    file_name + "</label>" + \
                    "<button type=\"button\" onclick=\"window.open('/download_data/" + file_name + "')\">下载 </button>" + \
                    "</li>"

    html_str += "</ol>"
    return html_str


def get_data_list():
    html_str = ""
    file_num, file_list = listdir(data_path, type="data")
    html_str += "<p>文件数：" + str(file_num) + "</p> <ol>"

    for file_path in file_list:
        file_name = file_path.split("/")[-1]
        html_str += "<li>" + \
                    "<label><input type=\"radio\" name=\"data\" value=\"" + file_name + "\" />" +\
                    file_name + "</label>" + \
                    "<button type=\"button\" onclick=\"window.open('/download_data/" + file_name + "')\">下载 </button>" + \
                    "</li>"
    html_str += "</ol>"
    return html_str


@route('/')
def main():
    html_str = '''
        <html>
            <head>
            </head>
            <body>
                <form action"/" method="post">
        '''
    html_str += get_data_list()
    html_str += get_rule_list()
    html_str += '''
                    <input type="submit" value="Select" />
                </form>
            </body>
        </html>
    '''
    return html_str


@route('/', method='POST')
def do_compute():
    rule_file = request.forms.get('rule')
    data_file = request.forms.get('data')
    if rule_path is None or data_file is None:
        return "error"

    inter_file = inter_path + data_file
    output_file = output_path + data_file

    ExpertCallReport.pre_read_setting(rule_file_name=rule_path + rule_file,
                                      data_file_name=data_path + data_file,
                                      output_file_name=inter_file)
    data = ExpertCallReport(input_file_name=inter_file,
                            output_file_name=output_file)
    data.save_by_different_time(
        output_root=output_path, output_file_name=data_file)

    return '<a href="/download_result"' + data_file + '>下载计算结果</a>'


run(host='0.0.0.0', port=8080, debug=True)
