# -*- coding: utf-8 -*-

from unittest import TestCase
from code.monthly import MonthlyReport, MonthlySingleDiseaseReport, \
    MonthlyLocationReport


class MonthlyReportTest(TestCase):
    """
    The test cases to test code in monthly.py.
    """
    def setUp(self):
        input_file_name = "../data/2017.01_01.csv"
        output_file_name = "../report/test_monthly_report.txt"
        self.data = MonthlyReport(input_file_name=input_file_name,
                                  output_file_name=output_file_name)

    def test_get_head(self):
        output_file_name = "../report/test_head.txt"
        with open(output_file_name, "w") as output_object:
            output_object.write(str(self.data._get_head()))
        output_object.close()

    def test_get_diagnosis_icd_counts(self):
        output_file_name = "../report/test_diagnosis_counts.txt"
        with open(output_file_name, "w") as output_object:
            output_object.write(str(self.data._get_diagnosis_icd_counts()))
        output_object.close()


class MonthlySingleDiseaseReportTest(TestCase):
    """
    The test cases to test code in monthly.py.
    """
    def setUp(self):
        # self.input_file_name = "../data/2017.01_01.csv"
        # self.output_file_name = "../report/test_monthly_report.txt"
        self.input_file_name = "../data/2017.5_entity.csv"
        self.output_file_name = "../report/2017.5_diagnosis_report.txt"

        # self.input_file_name = "../data/2017.06.csv"
        # self.output_file_name = "../report/2017.6_diagnosis_report.txt"
        self.data = MonthlySingleDiseaseReport(
            input_file_name=self.input_file_name,
            output_file_name=self.output_file_name)

    def test_get_head(self):
        output_file_name = "../report/test_head.txt"
        with open(output_file_name, "w") as output_object:
            output_object.write(str(self.data._get_head()))
        output_object.close()

    def test_get_diagnosis_icd_counts(self):
        output_file_name = "../report/test_diagnosis_counts.txt"
        with open(output_file_name, "w") as output_object:
            output_object.write(str(self.data._get_diagnosis_icd_counts()))
        output_object.close()

    def test_create_diagnosis(self):
        with open(self.output_file_name, "w") as output_object:
            output_object.write(str(self.data.create_diagnosis()))
        output_object.close()

    def test_create_ward(self):
        self.data.pre_ward("../data/2017.06_day.csv")
        self.data.create_ward(30.0, "../report/test_wards.csv")


class MonthlyLocationReportTest(TestCase):
    """
    The test cases to test code in monthly.py.
    """
    def setUp(self):
        pass

    def test_pre_format(self):
        input_file_name = "../data/2017.3_location.csv"
        self.data = MonthlyLocationReport(
            input_file_name=input_file_name,
            output_file_name="")

    def test_create_intermediate_result(self):
        input_file_name = "../data/2017.3_location.csvformat"
        output_file_name = "../report/2017.3_monthly_location.txt"
        self.data = MonthlyLocationReport(
            input_file_name=input_file_name,
            output_file_name="", is_pre_formated=True)
        self.data.create_intermediate_result(output_file_name=output_file_name)

    def test_output_format(self):
        input_file_name = "../report/2017.3_monthly_location.txt"
        output_file_name = "../report/2017.3_monthly_location_format.txt"
        self.data = MonthlyLocationReport(
            input_file_name="",
            output_file_name="", is_pre_formated=True)
        self.data.output_format(input_file_name, output_file_name)

    def test_create(self):
        # input_file_name = "../data/2017.3_location.csv"
        # output_file_name = "../report/2017.3_location_format.txt"

        # input_file_name = "../data/2017.5_location.csv"
        # output_file_name = "../report/2017.5_location_format.txt"

        input_file_name = "../data/2017年6月份门诊部按地域挂号收费查询统计.csv"
        output_file_name = "../report/2017年6月份门诊部按地域挂号收费查询统计_format.txt"

        self.data = MonthlyLocationReport(
            input_file_name=input_file_name,
            output_file_name=output_file_name, is_pre_formated=False)
        self.data.create()
