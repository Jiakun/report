#!/usr/bin/python
# -*- coding: utf-8 -*-

from bottle import *
from expert import MedicalServiceChargeReport
from server_common import get_file_list

med_input_path = '../data/medical/'
med_output_path = '../report/medical/'


@route('/upload_medicine')
@view('medicine_upload')
def upload_medicine():
    return dict(title="医事服务费")


@route('/medicine')
@view('medicine_main')
def medicine_main():
    med_file_num, med_list = get_file_list(med_input_path, file_type="data")
    return dict(data_list=med_list, data_file_num=med_file_num)


@route('/medicine', method='POST')
def medicine_do_compute():
    data_file = request.forms.get('data')

    if med_input_path is None or data_file is None:
        return "error"

    input_file = med_input_path + data_file
    output_file = med_output_path + data_file

    data = MedicalServiceChargeReport(
        input_path=med_input_path,
        input_file_name=data_file)
    data.group_data(med_output_path, data_file + ".out")
    data.format_output(med_output_path, data_file + ".out")

    return '<p><a href="/download/medicine/result/' + data_file + '" target="view_window">下载统计结果</a></p>'
