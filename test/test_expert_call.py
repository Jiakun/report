# -*- coding: utf-8 -*-

from unittest import TestCase
from code.expert_call import ExpertCallReport


class ExpertCallReportTest(TestCase):
    """
    The test cases to test code in monthly.py.
    """
    def setUp(self):
        self.input_root = "../data/expert_call/"
        self.output_root = "../report/expert_call/"
        self.file_names = ["2017.2季度.csv"]
        self.file_name = self.file_names[0]
        input_file_name = self.input_root + self.file_name
        self.rule_file_name = self.input_root + "rule/" + self.file_name + ".cfg"
        output_file_name = self.output_root + self.file_name
        inter_output_file_name = self.output_root + "inter/" + self.file_name
        ExpertCallReport.pre_read_setting(rule_file_name=self.rule_file_name,
                                          data_file_name=input_file_name,
                                          output_file_name=inter_output_file_name,
                                          periods=["2017-4-1", "2017-6-30"])
        self.data = ExpertCallReport(input_file_name=inter_output_file_name,
                                     output_file_name=output_file_name)

    def test_pre_read_setting(self):
        self.data.pre_read_setting(rule_file_name="../data/expert_call/rule/2017.2季度.csv.cfg",
                                   data_file_name="../data/expert_call/2017.2季度.csv",
                                   output_file_name="../report/expert_call/inter/2017.2季度.csv",
                                   periods=["2017-4-1", "2017-6-30"])

    def test_save_by_different_time(self):
        self.data.save_by_different_time(
            output_root=self.output_root, output_file_name=self.file_name)

    def test_compare_manual_file(self):
        ExpertCallReport.compare_manual_file(
            m_input_file_name="../data/expert_call/2017.2季度_手工.csv",
            c_input_file_name="../report/expert_call/2017.2季度.csv",
            output_file_name="../report/expert_call/2017.2季度_c.csv"
        )

    def test_get_pre_defined_first_counts(self):
        self.data.get_pre_defined_first_counts(
            input_file_name=self.input_root + self.file_name,
            rule_file_name=self.rule_file_name,
            periods=["2017-4-1", "2017-6-30"],
            output_file_name=self.output_root + self.file_name + ".o")
