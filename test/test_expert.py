# -*- coding: utf-8 -*-

from unittest import TestCase
from code.expert import ExpertReport, MedicalServiceChargeReport


class ExpertReportTest(TestCase):
    """
    The test cases to test code in monthly.py.
    """
    def setUp(self):
        self.input_root = "../data/expert/"
        self.output_root = "../report/expert/"
        self.file_names = ["2017-5门诊医事服务费-节假日-白天.csv",
                           "2016-5门诊医事服务费-节假日-白天.csv",
                           "2017-5门诊医事服务费-工作日-白天.csv",
                           "2016-5门诊医事服务费-工作日-白天.csv",
                           "2017-5门诊C楼专家号统计.csv",
                           "2016-5门诊C楼专家号统计.csv",
                           "2016-5急诊医事服务费-节假日.csv",
                           "2016-5急诊医事服务费-工作日.csv",
                           "2017-5急诊医事服务费-节假日.csv",
                           "2017-5急诊医事服务费-工作日.csv",
                           "2017-5门诊医事服务费-工作日-夜诊.csv",
                           "2016-5门诊医事服务费-工作日-夜诊.csv"]
        self.file_name = self.file_names[11]
        input_file_name = self.input_root + self.file_name
        output_file_name = self.output_root + self.file_name
        self.data = ExpertReport(input_file_name=input_file_name,
                                 output_file_name=output_file_name)

    def test_save_by_different_expert_level(self):
        self.data.save_by_different_expert_level(
            output_root=self.output_root, output_file_name=self.file_name)

    def test_format_raw_statistic_file(self):
        self.data.format_raw_statistic_file(root_dir=self.output_root)

    def test_clinic_create(self):
        filenames = self.file_names
        self.data.clinic_create(filenames=filenames, root_dir=self.output_root)


class MedicalServiceChargeReportTest(TestCase):
    def setUp(self):
        self.input_root = "../data/medical/"
        self.output_root = "../report/medical/"
        self.file_names = ["门诊医事服务费.csv",
                           "急诊医事服务费.csv",
                           "心电监护、麻醉监护.csv",
                           "住院医事服务费.csv",
                           "经院医转科室治疗数据.csv",
                           "门诊C楼医师人次统计.csv"]
        # self.file_index = "2017-6"
        self.file_index = "2017-7"

    def test_group_data(self):
        self.input_file_name = self.file_index + self.file_names[0]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.group_data(self.output_root, self.input_file_name + ".out")

    def test_format_output(self):
        self.input_file_name = self.file_index + self.file_names[0]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.format_output(self.output_root, self.input_file_name + ".out")

    def test_xindian_group_by_dep_name(self):
        self.input_file_name = self.file_index + self.file_names[2]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.group_xindian_by_dep_name(self.output_root, self.input_file_name + ".out")

    def test_group_bingqu_by_dep(self):
        self.input_file_name = self.file_index + self.file_names[3]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.group_bingqu_by_dep(self.output_root, self.input_file_name + ".out")

    def test_group_yuanyi_by_dep_name(self):
        self.input_file_name = self.file_index + self.file_names[4]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.group_yuanyi_by_dep_name(self.output_root, self.input_file_name + ".out")

    def test_group_c_by_dep_name(self):
        self.input_file_name = self.file_index + self.file_names[5]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.group_c_by_dep_name(self.output_root, self.input_file_name + ".out")

    def test_group_emergency_by_name(self):
        self.input_file_name = self.file_index + self.file_names[1]
        self.data = MedicalServiceChargeReport(
            input_path=self.input_root,
            input_file_name=self.input_file_name)
        self.data.group_emergency_by_name(self.output_root, self.input_file_name + ".out")

    def test_merge_results(self):
        name_list_file_name = self.input_root + "2017-6人员列表.txt"
        MedicalServiceChargeReport.merge_results(
            name_list_file_name = name_list_file_name,
            root=self.output_root + self.file_index, output_file_name="医事服务费汇总表.csv")


