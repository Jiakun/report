# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas


class MonthlyReport(object):
    """
    Common attributes for Report
    """
    def __init__(self, input_file_name, output_file_name):
        if output_file_name is None or input_file_name is None:
            raise Exception("File name cannot be none.")
        self.output_file_name = output_file_name
        try:
            self.content = pandas.read_csv(input_file_name)
        except:
            raise Exception("Cannot read input file.")

    def _get_head(self):
        return self.content.head()

    def _get_diagnosis_icd_counts(self):
        grouped_icds = self.content.groupby(self.content["分类ICD"])
        return grouped_icds.size()

    @abstractmethod
    def create(self):
        pass


class MonthlySingleDiseaseReport(MonthlyReport):
    def __init__(self, input_file_name, output_file_name):
        diagnosis_keywords = ["K07.603", "Q35.", "Q36.", "C03.",
                              "K07.1", "S02."]
        # K07.603 and K07.1 统计方式?
        new_file = ""
        with open(input_file_name) as original_file:
            first_line = True
            main_diagnosis_index = 0
            for line in original_file:
                if first_line is True:
                    first_line = False
                    new_file = line[:-1] + ",分类ICD\n"
                    line_split = line.split(",")
                    for i in range(0, len(line_split)):
                        if line_split[i] == "主要诊断ICD":
                            main_diagnosis_index = i
                            break
                    continue

                name = ""
                line_split = line.split(",")
                if "D11.0" in line_split[main_diagnosis_index] \
                        and "M894000/0" in line:
                    name = "D11.0 M894000/0"
                elif "C01" in line_split[main_diagnosis_index] \
                        or "C02." in line_split[main_diagnosis_index]:
                    name = "C01-C02."
                elif "D16.5" in line_split[main_diagnosis_index] \
                        and "成釉细胞瘤" in line:
                    name = "D16.5"
                else:
                    for keyword in diagnosis_keywords:
                        if keyword in line_split[main_diagnosis_index]:
                            name = keyword
                            break
                new_file += line[:-1] + "," + name + "\n"

        with open(input_file_name + "new", "w") as output_file:
            output_file.write(new_file)

        MonthlyReport.__init__(self, input_file_name + "new", output_file_name)

    def create(self):
        self.content["药费"] = self.content["抗菌药物费"] + \
                             self.content["西药费"] + \
                             self.content["中成药费"] + self.content["中草药费"]
        grouped_icds = self.content.groupby(self.content["分类ICD"])
        data = []
        keywords = ["住院天数", "术前住院日", "床位费", "手术费", "药费", "总费用"]
        # 费用统计方式
        with open (self.output_file_name, "w") as output_file:
            for keyword in keywords:
                output_file.write(str(grouped_icds[keyword].mean()))
        output_file.close()


