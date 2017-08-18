# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas
import shlex
import numpy as np


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
        self.file = open(input_file_name)
        self.size = len(self.file.readlines()) - 2
        self.file.close()

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
        diagnosis_keywords_chinese = [
            "颞下颌关节强直（ICD K07.6）", "腭裂（ICD Q35.）",
            "唇裂（ICD Q36.）", "牙龈癌（ICD C03.）",
            "牙合面畸形（ICD K07.1）", "面骨骨折（ICD S02.）"]
        # K07.6: K07.603
        # K07.1
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

                if "\"" in line:
                    new_line = ""
                    temp_line_split = line.split(",")
                    i = 0
                    while i < len(temp_line_split):
                        if "\"" in temp_line_split[i]:
                            new_split = temp_line_split[i]
                            i += 1
                            while "\"" not in temp_line_split[i]:
                                new_split += " " + temp_line_split[i]
                                i += 1
                            new_line += new_split + ","
                            i += 1
                            continue
                        new_line += temp_line_split[i] + ","
                        i += 1
                    line_split = new_line.split(",")

                else:
                    line_split = line.split(",")
                try:
                    if "D11.0" in line_split[main_diagnosis_index] \
                            and "M894000/0" in line:
                        name = "腮腺混合瘤（ICD D11.0 M894000/0）"
                    elif "C01" in line_split[main_diagnosis_index] \
                            or "C02." in line_split[main_diagnosis_index]:
                        name = "舌癌（ICD C01-C02.）"
                    elif "D16.5" in line_split[main_diagnosis_index] \
                            and "成釉细胞瘤" in line:
                        name = "下颌骨成釉细胞瘤（ICD D16.5）"
                    else:
                        for i in range(0, len(diagnosis_keywords)):
                            if diagnosis_keywords[i] in \
                                    line_split[main_diagnosis_index]:
                                name = diagnosis_keywords_chinese[i]
                                break
                except:
                    raise Exception(line)
                new_file += line[:-1] + "," + name + "\n"

        with open(input_file_name + "format", "w") as output_file:
            output_file.write(new_file)

        self.keywords = ["住院天数", "术前住院日", "床位费", "药费", "手术费",
                         "治疗费", "检查费", "总费用"]
        MonthlyReport.__init__(
            self, input_file_name + "format", output_file_name)

    def create_intermediate_result(self, inter_output_file_name):
        self.content["药费"] = self.content["抗菌药物费"] + \
                             self.content["西药费"] + \
                             self.content["中成药费"] + self.content["中草药费"]
        self.content["检查费"] = self.content["一般检查费"]
        self.content["治疗费"] =\
            self.content["一般治疗费"] + self.content["护理治疗费"]
        # self.content["临床物理治疗费"]
        # self.content["核素治疗费"] + self.content["介入治疗费"]
        # self.content["康复治疗费"] + self.content["中医治疗费"]
        # self.content["特殊治疗费"] + self.content["精神治疗费"]
        grouped_icds = self.content.groupby(self.content["分类ICD"])

        data = []
        # 费用统计方式

        surgery_records = self.content[self.content["手术费"] > 0]
        surgery_grouped_icds = surgery_records.groupby(self.content["分类ICD"])

        with open(inter_output_file_name, "w") as output_file:
            output_file.write(str(grouped_icds.size()))
            for keyword in self.keywords:
                if keyword == "手术费":
                    output_file.write(str(
                        surgery_grouped_icds[keyword].mean()))
                elif keyword == "术前住院日":
                    output_file.write(str(
                        surgery_grouped_icds[keyword].mean()))
                else:
                    output_file.write(str(grouped_icds[keyword].mean()))
        output_file.close()

    def create_diagnosis(self):
        # save grouped data as intermediate results
        inter_output_file_name = \
            self.output_file_name.split("_raw")[0] + ".txt"
        self.create_intermediate_result(
            inter_output_file_name=inter_output_file_name)

        # pre-defined diagnosis types
        results = [[], [], [], [], [], [], [], [], []]
        icds = ["K07.6", "D16.5", "Q35", "Q36",
                "C03", "D11", "C01", "K07.1", "S02"]

        # read grouped data
        input_file = open(inter_output_file_name)
        lines = input_file.readlines()
        input_file.close()
        is_first_line = True
        for line in lines:
            if is_first_line:
                is_first_line = False
                continue

            if "dtype:" in line:
                continue
            value = float(line.split(" ")[-1])
            for i in range(len(icds)):
                if icds[i] in line:
                    results[i].append(value)
                    continue
        # calculate percentage of discharged patient for each diagnosis type
        for result in results:
            try:
                result.insert(1, result[0] / self.size * 100)
            except:
                pass

        # calculate avg. days in hospital and avg. days before surgery
        sum_days_in_hospital = 0
        sum_days_before_surgery = 0

        for i in range(len(results)):
            sum_days_in_hospital += results[i][0] * results[i][2]
            sum_days_before_surgery += results[i][0] * results[i][3]

        sum_discharged_patients = np.sum(results, axis=0)[0]
        avg_days_in_hospital = sum_days_in_hospital / sum_discharged_patients
        avg_days_before_surgery = sum_days_before_surgery / sum_discharged_patients
        sum_percentage_discharged_patients = sum_discharged_patients / float(self.size) * 100

        with open(self.output_file_name, "w") as output_file:
            output_file.write("疾病名称,出院病人数,占出院病人数%,")
            for keyword in self.keywords:
                output_file.write(keyword + ",")
            for i in range(len(results)):
                if i == 2:
                    # skip 单侧下颌骨
                    output_file.write("\n")
                output_file.write("\n" + icds[i] + ",")
                for j in range(len(results[i])):
                    if j == 0 or j > 3:
                        output_file.write("%.2f," % results[i][j])
                    else:
                        output_file.write("%.3f," % results[i][j])
            output_file.write("\n,%.2f,%.3f,%.3f,%.3f" % (sum_discharged_patients,
                              sum_percentage_discharged_patients,
                              avg_days_in_hospital,
                              avg_days_before_surgery))

    def pre_ward(self, input_file_name):
        try:
            self.ward_content = pandas.read_csv(input_file_name)
        except:
            raise Exception("Cannot open file! %s", input_file_name)

    def create_ward(self, month_day, output_file_name):
        # group data by discharge department
        ward_grouped_icds = self.content.groupby(self.content["出院科室"])
        # pre-defined number of beds in each ward
        ward_bed_num = [21.0, 33.0, 35.0, 32.0, 28.0, 157.0]
        wards = ["一病区", "二病区", "三病区", "四病区", "五病区"]
        # TODO: how to cauculate charges for medicine
        self.content["药费"] = \
            self.content["西药费"] + self.content["抗菌药物费"] + \
            self.content["中成药费"] + self.content["中草药费"]

        # filter of surgery
        surgery_records = self.content[self.content["主要手术ICD"] > 0]
        surgery_grouped_icds = surgery_records.groupby(self.content["出院科室"])

        # save intermediate results from raw data
        inter_output_file_name = \
            output_file_name.split("_inter.txt")[0] + "_ward.txt"
        with open(inter_output_file_name, "w") as ward_inter_output_file:
            ward_inter_output_file.write(str(
                ward_grouped_icds["出院科室"].value_counts()))
            ward_inter_output_file.write(str(
                surgery_grouped_icds["出院科室"].value_counts()))
            ward_inter_output_file.write(str(ward_grouped_icds["住院天数"].sum()))
            ward_inter_output_file.write(str(ward_grouped_icds["住院天数"].mean()))
            ward_inter_output_file.write(str(
                ward_grouped_icds["术前住院日"].mean()))
            ward_inter_output_file.write(str(ward_grouped_icds["总费用"].mean()))
            ward_inter_output_file.write(str(ward_grouped_icds["总费用"].sum()))
            ward_inter_output_file.write(str(ward_grouped_icds["药费"].sum()))

        # read from intermediate results
        is_first_line = True
        results = [[], [], [], [], [], []]
        sum = 0.0
        with open(inter_output_file_name) as ward_output_file:
            for line in ward_output_file:
                if is_first_line:
                    is_first_line = False
                    continue

                if "dtype:" in line:
                    results[-1].append(sum)
                    sum = 0.0
                    continue

                value = float(line.split(" ")[-1])
                for i in range(0, len(wards)):
                    if wards[i] in line:
                        results[i].append(value)
                        sum += value

        # caculate all charges per bed and charge of medicine per bed
        for i in range(0, len(results)):
            results[i][6] = results[i][6] / self.ward_content["实占床日"][i]
            results[i][7] = results[i][7] / self.ward_content["实占床日"][i]

        self.ward_content["现有人数"] = \
            self.ward_content["原有人数"] + self.ward_content["入院人数"]

        wards.append("合计")

        with open(output_file_name, "w") as ward_output_file:
            ward_output_file.write(
                "病区,开放床位,原有人数,入院人数,出院人数,手术人数,现有人数,住院日,实占床日,开放床日\n")
            for i in range(0, len(results)):
                ward_output_file.write(wards[i] + ",")
                ward_output_file.write(str(ward_bed_num[i]) + ",")
                ward_output_file.write(str(self.ward_content["原有人数"][i]) + ",")
                ward_output_file.write(str(self.ward_content["入院人数"][i]) + ",")
                ward_output_file.write(str(
                    results[i][0]) + "," + str(results[i][1]) + ",")
                ward_output_file.write(str(
                    self.ward_content["现有人数"][i] - results[i][0]) + ",")
                ward_output_file.write(str(results[i][2]) + ",")
                ward_output_file.write(str(self.ward_content["实占床日"][i]) + ",")
                ward_output_file.write(str(
                    ward_bed_num[i] * month_day) + "\n")

            ward_output_file.write(
                "病区,病床周转次数,病床使用率%,平均住院日(天),术前平均住院日,人均住院费(元),"
                "每床日收费(元),每床日药费(元)\n")
            for i in range(0, len(results)):
                ward_output_file.write(wards[i] + ",")
                turnover_of_bed = results[i][0] / ward_bed_num[i]
                usage_rate_of_bed = 100.0 * self.ward_content["实占床日"][i] / \
                                    self.ward_content["开放床日"][i]
                if i < len(results) - 1:
                    ward_output_file.write(
                        "%.1f,%.1f,%.1f,%.1f,%d,%.2f,%.2f\n" %
                        (turnover_of_bed, usage_rate_of_bed,
                        results[i][3], results[i][4], results[i][5],
                        results[i][6], results[i][7]))
                else:
                    ward_output_file.write(
                        "%.1f,%.1f," %
                        (turnover_of_bed, usage_rate_of_bed))
                    len_each_result = len(results[0])
                    for i_t in range(3, len_each_result - 2):
                        sum = 0.0
                        for j in range(len(results) - 1):
                            sum += results[j][0] * results[j][i_t]
                        if i_t == len_each_result - 3:
                            ward_output_file.write("%d," % (sum / results[i][0]))
                        else:
                            ward_output_file.write("%.1f," % (sum / results[i][0]))
                    ward_output_file.write("%.2f,%.2f" % (results[i][6], results[i][7]))


class MonthlyLocationReport(MonthlyReport):
    def __init__(self, input_file_name, output_file_name,
                 is_pre_formated=False):
        self.location_keywords = [
            "北京", "天津", "上海", "重庆", "广东", "山东", "浙江",
            "江苏", "陕西", "河南", "福建", "四川", "湖南", "广西",
            "河北", "山西", "云南", "安徽", "黑龙江", "湖北", "吉林",
            "甘肃", "江西", "辽宁", "内蒙", "新疆", "海南", "贵州",
            "宁夏", "青海", "西藏", "香港", "澳门", "台湾",
            "其他来源不明", "其他外籍"]

        self.input_file_name = input_file_name
        self.output_file_name = output_file_name

        self.content = None
        if is_pre_formated is False:
            self.format_input_file_name = input_file_name + "format"
            self.pre_format(output_file_name=self.format_input_file_name)
            MonthlyReport.__init__(self, self.format_input_file_name,
                                   self.output_file_name)
        else:
            MonthlyReport.__init__(
                self, self.input_file_name, self.output_file_name)

    def pre_format(self, output_file_name):
        new_content = "项目,人次,诊疗费,省市\n"
        beijing_districts = ["海淀", "朝阳", "丰台", "东城", "西城", "石景山",
                             "顺义", "怀柔", "密云", "延庆", "昌平", "平谷",
                             "门头沟", "房山", "通州", "大兴"]
        with open(self.input_file_name) as input_file:
            for line in input_file:
                is_found = False
                for keyword in self.location_keywords:
                    if keyword in line:
                        line_format =\
                            line.strip().replace("\n", "").replace("\r", "")
                        new_content += line_format + "," + keyword + "\n"
                        is_found = True
                        break
                if is_found is True:
                    continue
                for keyword in beijing_districts:
                    if keyword in line:
                        new_content += line.replace("\n", "") + ",北京" + "\n"
                        is_found = True
                        break
                if is_found is True:
                    continue
                new_content += line.replace("\n", "") + ",Unknown\n"

        with open(output_file_name, "w") as output_file:
            output_file.write(new_content)
        output_file.close()

    def create_intermediate_result(self, output_file_name):
        grouped_locations = self.content.groupby(self.content["省市"])
        sum_data = grouped_locations.sum().reset_index()
        sum_data.to_csv(output_file_name)

    def output_format(self, input_file_name, output_file_name):
        data = [""] * 36
        all_others = [0, 0.0]
        input_file = open(input_file_name)
        lines = input_file.readlines()
        lines[-1] += "\n"
        for line in lines:
            line_split = line.replace("\n", "").split(",")
            location = line_split[1]
            if location in self.location_keywords:
                location_index = self.location_keywords.index(location)
                if location_index == 34:
                    people_count = int(line_split[2])
                    fee_count = float(line_split[3])
                    all_others[0] += people_count
                    all_others[1] += fee_count
                elif location_index == 35:
                    people_count = int(line_split[2])
                    fee_count = float(line_split[3])
                    all_others[0] += people_count
                    all_others[1] += fee_count
                    data[location_index] = ",".join(line_split[1:]) + "\n"
                else:
                    data[location_index] = ",".join(line_split[1:]) + "\n"
            else:
                pass
                # raise Exception("Cannot find such item in location list!")
        input_file.close()

        for i in range(0, len(data)):
            if i == 34:
                data[i] = "其他," + str(all_others[0]) + "," +\
                          str(all_others[1]) + "\n"
            if data[i] == "":
                data[i] = self.location_keywords[i] + ",0,0\n"

        with open(output_file_name, "w") as f:
            for item in data:
                f.write(item)
        f.close()

    def create(self):
        inter_output_file_name = \
            self.output_file_name.split("_format")[0] + ".txt"
        self.create_intermediate_result(
            output_file_name=inter_output_file_name)
        self.output_format(input_file_name=inter_output_file_name,
                           output_file_name=self.output_file_name)
