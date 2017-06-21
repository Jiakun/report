# -*- coding: utf-8 -*-

from unittest import TestCase
from code.monthly import MonthlyReport, MonthlySingleDiseaseReport


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
        input_file_name = "../data/2017.01_01.csv"
        output_file_name = "../report/test_monthly_report.txt"
        self.data = MonthlySingleDiseaseReport(
            input_file_name=input_file_name,
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

    def test_create(self):
        output_file_name = "../report/test_diagnosis_report.txt"
        with open(output_file_name, "w") as output_object:
            output_object.write(str(self.data.create()))
        output_object.close()
