#!/usr/bin/python
# -*- coding: utf-8 -*-

from bottle import *
from expert_call import ExpertCallReport
from server_common import get_file_list


ec_data_path = '../data/expert_call/'
ec_rule_path = '../data/expert_call/rule/'
ec_inter_path = '../report/expert_call/inter/'
ec_output_path = '../report/expert_call/'


@route('/upload_expert_call')
@view('expert_call_upload')
def upload_expert_call():
    return dict(title="专家出诊")


@route('/expert_call')
@view('expert_call_main')
def expert_call_main():
    rule_file_num, rule_list = get_file_list(ec_rule_path, file_type="rule")
    data_file_num, data_list = get_file_list(ec_data_path, file_type="data")
    return dict(data_list=data_list, data_file_num=data_file_num,
                rule_list=rule_list, rule_file_num=rule_file_num)


@route('/expert_call', method='POST')
def expert_call_do_compute():
    rule_file = request.forms.get('rule')
    data_file = request.forms.get('data')
    period_after = request.forms.get('period_after')
    period_before = request.forms.get('period_before')
    periods = [period_after, period_before]

    if ec_rule_path is None or data_file is None:
        return "error"

    inter_file = ec_inter_path + data_file
    output_file = ec_output_path + data_file

    ExpertCallReport.pre_read_setting(rule_file_name=ec_rule_path + rule_file,
                                      data_file_name=ec_data_path + data_file,
                                      output_file_name=inter_file,
                                      periods=periods)
    data = ExpertCallReport(input_file_name=inter_file,
                            output_file_name=output_file)
    data.save_by_different_time(
        output_root=ec_output_path, output_file_name=data_file)

    return '<p><a href="/download/expert_call/result/' + data_file + '" target="view_window">下载出诊结果</a></p>' + \
        '<p><a href="/download/expert_call/result/' + data_file + '.o" target="view_window">下载应出诊次数</a></p>'
