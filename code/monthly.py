# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas
import shlex


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
        diagnosis_keywords_chinese = ["颞下颌关节强直（ICD K07.6）",
                                      "腭裂（ICD Q35.）",
                                      "唇裂（ICD Q36.）",
                                      "牙龈癌（ICD C03.）",
                                      "牙合面畸形（ICD K07.1）",
                                      "面骨骨折（ICD S02.）"]
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
        MonthlyReport.__init__(self, input_file_name + "format", output_file_name)

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
        with open(inter_output_file_name, "w") as output_file:
            output_file.write(str(grouped_icds.size()))
            for keyword in self.keywords:
                print keyword
                output_file.write(str(grouped_icds[keyword].mean()))
        output_file.close()

    def create(self):
        inter_output_file_name = \
            self.output_file_name.split("_raw")[0] + ".txt"
        self.create_intermediate_result(
            inter_output_file_name=inter_output_file_name)
        results = [[], [], [], [], [], [], [], [], [], []]

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
            if "K07.6" in line:
                results[0].append(value)
            elif "D16.5" in line:
                results[1].append(value)
            elif "Q35" in line:
                results[3].append(value)
            elif "Q36" in line:
                results[4].append(value)
            elif "C03" in line:
                results[5].append(value)
            elif "D11" in line:
                results[6].append(value)
            elif "C01" in line:
                results[7].append(value)
            elif "K07.1" in line:
                results[8].append(value)
            elif "S02" in line:
                results[9].append(value)

        for result in results:
            try:
                result.insert(1, result[0] / self.size * 100)
            except:
                pass

        with open(self.output_file_name, "w") as output_file:
            output_file.write("出院病人数,")
            for keyword in self.keywords:
                output_file.write(keyword + ",")
            for result in results:
                output_file.write("\n")
                for value in result:
                    output_file.write("%.1f," % value)
            output_file.write(str(self.size))


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
                        new_content += \
                            line.strip().replace("\n", "").replace("\r", "") + \
                            "," + keyword + "\n"
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
        with open(output_file_name, "w") as output_file:
            output_file.write(str(grouped_locations.sum()))
        output_file.close()

    def output_format(self, input_file_name, output_file_name):
        data = [""] * 36
        all_others = [0, 0.0]
        input_file = open(input_file_name)
        lines = input_file.readlines()
        lines[-1] += "\n"
        for line in lines:
            new_line = ','.join(line.split())
            location = new_line.split(",")[0]
            if location in self.location_keywords:
                location_index = self.location_keywords.index(location)
                if location_index == 34:
                    people_count = int(new_line.split(",")[1])
                    fee_count = float(new_line.split(",")[2])
                    all_others[0] += people_count
                    all_others[1] += fee_count
                elif location_index == 35:
                    people_count = int(new_line.split(",")[1])
                    fee_count = float(new_line.split(",")[2])
                    all_others[0] += people_count
                    all_others[1] += fee_count
                    data[location_index] = line
                else:
                    data[location_index] = line
            else:
                pass
                # raise Exception("Cannot find such item in location list!")
        input_file.close()

        for i in range(0, len(data)):
            if i == 34:
                data[i] = "其他\t" + str(all_others[0]) + "\t" +\
                          str(all_others[1]) + "\n"
            if data[i] == "":
                data[i] = self.location_keywords[i] + "\t0\t0\n"

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
