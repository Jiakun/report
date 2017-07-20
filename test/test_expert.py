# -*- coding: utf-8 -*-

from unittest import TestCase
from code.expert import ExpertReport


class ExpertReportTest(TestCase):
    """
    The test cases to test code in monthly.py.
    """
    def setUp(self):
        self.input_root = "../data/expert/"
        self.output_root = "../report/expert/"
        self.file_names = ["2017-5门诊医事服务费-节假日-白天.csv",
                           "2017-5门诊医事服务费-工作日-夜诊.csv",
                           "2017-5门诊医事服务费-工作日-白天.csv",
                           "2017-5门诊C楼专家号统计.csv",
                           "2017-5急诊医事服务费-节假日.csv",
                           "2017-5急诊医事服务费-工作日.csv",
                           "2016-5门诊医事服务费-节假日-白天.csv",
                           "2016-5门诊医事服务费-工作日-夜诊.csv",
                           "2016-5门诊医事服务费-工作日-白天.csv",
                           "2016-5门诊C楼专家号统计.csv",
                           "2016-5急诊医事服务费-节假日.csv",
                           "2016-5急诊医事服务费-工作日.csv"]
        self.file_name = self.file_names[6]
        input_file_name = self.input_root + self.file_name
        output_file_name = self.output_root + self.file_name
        self.data = ExpertReport(input_file_name=input_file_name,
                                 output_file_name=output_file_name)

    def test_save_by_different_expert_level(self):
        self.data.save_by_different_expert_level(
            output_root=self.output_root, output_file_name=self.file_name)

    def test_format_raw_statistic_file(self):
        self.data.format_raw_statistic_file(root_dir=self.output_root)
