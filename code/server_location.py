#!/usr/bin/python
# -*- coding: utf-8 -*-

from bottle import *
from monthly import MonthlyLocationReport
from server_common import get_file_list

ml_input_path = '../data/location/'
ml_output_path = '../report/location/'


@route('/upload_location')
@view('location_upload')
def upload_location():
    return dict(title="地域")


@route('/location')
@view('location_main')
def location_main():
    location_file_num, location_list = get_file_list(ml_input_path, file_type="data")
    return dict(data_list=location_list, data_file_num=location_file_num)


@route('/location', method='POST')
def location_do_compute():
    data_file = request.forms.get('data')

    if ml_input_path is None or data_file is None:
        return "error"

    inter_file = ml_input_path + data_file
    output_file = ml_output_path + data_file

    data = MonthlyLocationReport(input_file_name=inter_file,
                                 output_file_name=output_file,
                                 is_pre_formated=True)
    data.create()

    return '<p><a href="/download/location/result/' + data_file + '" target="view_window">下载统计结果</a></p>'
