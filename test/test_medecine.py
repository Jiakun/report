# -*- coding: utf-8 -*-

from unittest import TestCase
from code.medicine import MedicalServiceChargeReport


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

    def test_add_grouped_yuanyi(self):
        name_list_file_name = self.input_root + "2017-6人员列表.txt"
        input_file_name = self.output_root + self.file_index + self.file_names[4] + ".out"
        MedicalServiceChargeReport.add_grouped_yuanyi(
            input_file_name=input_file_name, list_file_name=name_list_file_name,
            output_file_name=input_file_name)
