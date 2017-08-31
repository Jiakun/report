#!/usr/bin/python
# -*- coding: utf-8 -*-

from bottle import *
from expert_call import ExpertCallReport
from server_expert_call import *
from server_location import *

# root = '/home/jiakun/PycharmProjects/SummaryReport/'

pro_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(pro_path)
# 定义assets路径，即静态资源路径，如css,js,及样式中用到的图片等
assets_path = '/'.join((pro_path, 'assets'))


@route('/assets/<filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif>')
def server_static(filename):
    """定义/assets/下的静态(css,js,图片)资源路径"""
    return static_file(filename, root=assets_path)


@route('/assets/<filename:re:.*\.ttf|.*\.otf|.*\.eot|.*\.woff|.*\.svg|.*\.map>')
def server_static(filename):
    """定义/assets/字体资源路径"""
    return static_file(filename, root=assets_path)


@route('/upload/<project>', method='POST')
def do_upload(project):
    upload_type = request.forms.get('type')
    upload_file = request.files.get('data')
    if project == "expert_call":
        if upload_type == "data":
            upload_file.save(ec_data_path, overwrite=True)
        elif upload_type == "rule":
            upload_file.save(ec_rule_path, overwrite=True)
        else:
            return "error"
    elif project == "location":
        if upload_type == "data":
            upload_file.save(ml_input_path, overwrite=True)
        else:
            return "error"
    redirect('/upload_' + project)


@route('/download/<project>/<download_type>/<file_name:path>')
def download_file(project, download_type, file_name):
    if project == "expert_call":
        if download_type == "data":
            return static_file(download=file_name, root=ec_data_path, filename=file_name)
        elif download_type == "rule":
            return static_file(download=file_name, root=ec_rule_path, filename=file_name)
        elif download_type == "result":
            return static_file(download=file_name, root=ec_output_path, filename=file_name)
    elif project == "location":
        if download_type == "data":
            return static_file(download=file_name, root=ml_input_path, filename=file_name)
        elif download_type == "result":
            return static_file(download=file_name, root=ml_output_path, filename=file_name)


@route('/delete/<project>/<delete_type>/<file_name:path>')
def delete_file(project, delete_type, file_name):
    if project == "expert_call":
        if delete_type == "data":
            os.remove(ec_data_path + file_name)
        elif delete_type == "rule":
            os.remove(ec_rule_path + file_name)
        elif delete_type == "result":
            os.remove(ec_output_path + file_name)
        redirect('/expert_call')
    elif project == "location":
        if delete_type == "data":
            os.remove(ml_input_path + file_name)
        redirect('/location')


@route('/')
def main():
    redirect('/expert_call')


run(host='0.0.0.0', port=8080, debug=True)
