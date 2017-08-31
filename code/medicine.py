# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas as pd
import shlex
import os
import os.path
import re
import csv
from collections import OrderedDict

import openpyxl
import re


class MedicalServiceChargeReport(object):
    # 医事服务费各科室计算报表
    def __init__(self, input_path, input_file_name):
        try:
            self.content = pd.read_csv(input_path + input_file_name)
        except:
            raise Exception("Cannot read input file. %s" %input_path + input_file_name)
        self.file = open(input_path + input_file_name)
        self.size = len(self.file.readlines()) - 2
        self.file.close()
        pd.set_option('display.max_rows', None)

    @staticmethod
    def get_type_dict(reg_type, dict, is_add_old_reg):
        # types = ["知名专家", "主任医师", "副主任医师", "主治医师", "普通"]
        if "副" in reg_type:
            dict[2].append(reg_type)
        elif "治" in reg_type and "洁" not in reg_type:
            dict[3].append(reg_type)
        elif "主" in reg_type:
            dict[1].append(reg_type)
        elif "知" in reg_type or "特需" in reg_type or "特色" in reg_type:
            if not is_add_old_reg and "特色" in reg_type:
                return "Exception"
            else:
                dict[0].append(reg_type)
        elif "普通" in reg_type or "高资" in reg_type \
                or "指导" in reg_type or "实名" in reg_type \
                or "离休统筹医保号" in reg_type or "病区" in reg_type \
                or "预防口腔 专业号" or "":
            dict[4].append(reg_type)
        else:
            return "Exception"

    def group_data(self, output_root, output_file_name):
        type_dict = [[], [], [], [], []]
        types = ["知名专家", "主任医师", "副主任医师", "主治医师", "普通", "特需"]

        for data in self.content["号种"]:
            self.get_type_dict(data, type_dict, is_add_old_reg=False)

        self.content["职称"] = self.content["号种"]

        for i in range(len(type_dict)):
            set_type = list(set(type_dict[i]))
            self.content["职称"] = \
                self.content["职称"].replace(set_type, [types[i]] * len(set_type))

        self.content["核算科室"] = self.content["核算科室"].replace("颞下颌关节病及口面痛", "放射科")
        grouped_data = self.content.groupby(
            ["核算科室", "职称", "挂号医师", "是否工作日", "是否夜诊", "号种", "单价"])
        sum_data = grouped_data["数量"].sum().reset_index()
        sum_data_sort = sum_data.sort(
            ["核算科室", "职称", "挂号医师"], ascending=False).reset_index(drop=True)
        sum_data_sort.to_csv(output_root + "inter/" + output_file_name)

    def group_xindian_by_dep_name(self, output_root, output_file_name):
        pd.options.display.max_rows = 999
        grouped_data = self.content.groupby(["费用名称", "核算科室", "挂号医师"])
        sum_data = grouped_data["数量"].sum().reset_index()
        sum_data.to_csv(output_root + output_file_name)

    def group_bingqu_by_dep(self, output_root, output_file_name):
        pd.options.display.max_rows = 999
        grouped_data = self.content.groupby(["核算科室"])
        sum_data = grouped_data["数量"].sum().reset_index()
        sum_data.to_csv(output_root + output_file_name)

    def group_c_by_dep_name(self, output_root, output_file_name):
        pd.options.display.max_rows = 999
        grouped_data = self.content.groupby(["科别", "医事服务费类型", "医师姓名"])
        sum_data = grouped_data["人次"].sum().reset_index()
        expert_data = sum_data[sum_data["医事服务费类型"] != "普通号"]
        expert_data.to_csv(output_root + output_file_name + ".exp")
        putonghao_data = sum_data[sum_data["医事服务费类型"] == "普通号"]
        grouped_data_putonghao = \
            putonghao_data.groupby(["科别"])["人次"].sum().reset_index()
        grouped_data_putonghao.to_csv(output_root + output_file_name + ".norm")

    def group_yuanyi_by_dep_name(self, output_root, output_file_name):
        pd.options.display.max_rows = 999
        filtered_data = self.content[(self.content["科室名称"] != "放射科") &
                                     (self.content["科室名称"] != "门诊药房") &
                                     (self.content["科室名称"] != "病理科") &
                                     (self.content["科室名称"] != "检验科") &
                                     (self.content["科室名称"] != "注射室") &
                                     (self.content["科室名称"] != "院医室")]
        filtered_data = filtered_data.replace(
            ["综合治疗二科修复专业","综合治疗二科口腔综合", "综合治疗二科牙体牙髓", "综合治疗二科牙周专业"],
            "综合治疗二科")
        filtered_data = filtered_data.replace(
            ["综合治疗科口腔综合", "综合治疗科牙体牙髓病", "综合治疗科牙周病专业"], "综合治疗科")
        filtered_data = filtered_data.replace(
            ["特诊科修复专业", "特诊科牙体牙髓病专业", "特诊科颌面外科专业"], "特诊科")
        filtered_data = filtered_data.replace(
            "颌面外科专家门诊(综合楼三楼)", "激光整形美容室")
        filtered_data = filtered_data.replace(
            ["预防保健牙体牙髓专业"], "预防保健")
        filtered_data = filtered_data.replace(
            "修复科", "修复")

        grouped_data = filtered_data.groupby(["科室名称", "医生姓名"])
        sum_data = grouped_data["金额"].count().reset_index()
        sum_data.rename(columns={'金额': '数量'}, inplace = True)
        sum_data.to_csv(output_root + output_file_name)

    @staticmethod
    def add_grouped_yuanyi(input_file_name, list_file_name, output_file_name):
        name_list = {}
        dep_name = ""
        with open (list_file_name) as input_file:
            for line in input_file:
                line = line.replace("\n", "")
                if "_" in line:
                    dep_name = line
                else:
                    name_list[line] = dep_name

        content = ["索引,院医转科室,数量,医生姓名,所属科室\n"]
        with open(input_file_name) as input_file:
            datareader = csv.DictReader(input_file)
            for line in datareader:
                try:
                    dep_name = name_list[line["医生姓名"]]
                except:
                    dep_name = ""
                new_line = ""
                for key, item in line.items():
                    new_line += item + ","
                content.append(new_line + dep_name + "\n")
        with open(output_file_name, "w") as output_file:
            for line in content:
                output_file.write(line)

    def group_emergency_by_name(self, output_root, output_file_name):
        pd.options.display.max_rows = 999
        grouped_data = self.content.groupby(["挂号医师", "是否工作日"])
        sum_data = grouped_data["数量"].sum().reset_index()
        sum_data.to_csv(output_root + output_file_name)

    @staticmethod
    def merge_results(name_list_file_name, root, output_file_name):
        # 读入人员列表
        is_first_line = True
        dep = ""
        deps = []
        name_lists = OrderedDict()
        with open(name_list_file_name) as name_list_file:
            for line in name_list_file:
                if is_first_line or "_" in line:
                    dep = line[1:-1]
                    name_lists[dep] = OrderedDict()
                    name_lists[dep]["普通"] = []
                    deps.append(dep)
                    is_first_line = False
                else:
                    name_lists[dep][line[:-1]] = []

        # 读入门诊统计数据
        # 科室,职级,姓名,计数
        # 颌面外科门诊,知名专家,翟新利,209, 0, 11, 0
        input_main_file = open(root + "门诊医事服务费.csv.out")
        main_lines = input_main_file.readlines()

        is_first_line = True
        this_name = ""
        for line in main_lines:
            if is_first_line:
                is_first_line = False
                continue
            line_split = line[:-1].split(",")
            this_dep = line_split[0]
            this_name = line_split[2]
            for dep in deps:
                if this_dep == "口腔颌面外科专家门诊":
                    this_dep = "颌面外科专家门诊"
                    break
                elif "预防科" in this_dep or "_预防保健科" in this_dep:
                    this_dep = "预防保健"
                    break
                elif this_dep.replace("_", "") in dep:
                    this_dep = this_dep.replace("_", "")
                    break
            try:
                if name_lists[this_dep].has_key(this_name):
                    name_lists[this_dep][this_name] = line_split[1:]
            except:
                raise Exception(this_dep)
        c_exps = []
        # ,科别,医事服务费类型,医师姓名,人次
        input_c_exp_file = open(root + "门诊C楼医师人次统计.csv.out.exp")
        c_exp_lines = input_c_exp_file.readlines()
        # ,科别,人次
        input_c_norm_file = open(root + "门诊C楼医师人次统计.csv.out.norm")
        c_norm_lines = input_c_norm_file.readlines()
        is_first_line = True
        for c_exp_line in c_exp_lines:
            if is_first_line:
                is_first_line = False
                continue
            line_split = c_exp_line[:-1].split(",")
            this_dep = line_split[1].replace("C楼", "")
            if this_dep == "综合二科":
                this_dep = "综合治疗二科"
            try:
                this_name = line_split[3]
            except:
                raise Exception(c_exp_line)
            # raise Exception(line_split[4])

            if name_lists[this_dep].has_key(this_name):
                if len(name_lists[this_dep][this_name]) > 2:
                    name_lists[this_dep][this_name + "*"] = [
                        name_lists[this_dep][this_name][0],
                        name_lists[this_dep][this_name][1],
                        line_split[4]]
                else:
                    name_lists[this_dep][this_name + "*"] = ["0", "0", line_split[4]]
            elif name_lists[this_dep].has_key(this_name + "*"):
                name_lists[this_dep][this_name + "*"] = ["0", "0", line_split[4]]
            else:
                c_exps.append(c_exp_line)

            # ,科别,人次
            is_first_line = True
            for c_norm_line in c_norm_lines:
                if is_first_line:
                    is_first_line = False
                    continue
                line_split = c_norm_line[:-1].split(",")
                this_dep = line_split[1].replace("C楼", "")
                if this_dep == "综合二科":
                    this_dep = "综合治疗二科"
                try:
                    name_lists[this_dep]["普通*"] = ["0", "0", line_split[2]]
                except:
                    raise Exception(c_norm_line)

        emergency_exceptions = []
        # ,挂号医师,是否工作日,数量
        with open(root + "急诊医事服务费.csv.out") as emergency_input_file:
            datareader = csv.DictReader(emergency_input_file)
            for emergency_line in datareader:
                this_dep = "急诊科"
                this_name = emergency_line["挂号医师"]
                e_index = 2
                if emergency_line["是否工作日"] == "节假日":
                    e_index = 4

                if name_lists[this_dep].has_key(this_name):
                    if len(name_lists[this_dep][this_name]) > 2:
                        name_lists[this_dep][this_name][e_index] = \
                            str(int(name_lists[this_dep][this_name][e_index])
                                + int(emergency_line["数量"]))
                    else:
                        if e_index == 2:
                            name_lists[this_dep][this_name] = \
                                ['0', '0', emergency_line["数量"], '0', '0']
                        else:
                            name_lists[this_dep][this_name] = \
                                ['0', '0', '0', '0', emergency_line["数量"]]
                elif this_dep in deps:
                    if len(name_lists[this_dep]["普通"]) > 2:
                        name_lists[this_dep]["普通"][e_index] = \
                            str(int(name_lists[this_dep]["普通"][e_index]) + int(emergency_line["数量"]))
                    else:
                        if e_index == 2:
                            name_lists[this_dep]["普通"] = \
                                ['0', '0', emergency_line["数量"], '0', '0']
                        else:
                            name_lists[this_dep][this_name] = \
                                ['0', '0', '0', '0', emergency_line["数量"]]
                else:
                    raise Exception("emergency")

        yuanyi_exceptions = []
        # ,转科室,数量,医师姓名,科室
        with open(root + "经院医转科室治疗数据.csv.out") as yuanyi_input_file:
            datareader = csv.DictReader(yuanyi_input_file)
            for yuanyi_line in datareader:
                if len(yuanyi_line["所属科室"]) ==  0:
                    str1 = ""
                    for key, item in yuanyi_line.items():
                        str1 += str(item) + ","
                    yuanyi_exceptions.append(str1[:-1] + "\n")
                    continue

                this_name = yuanyi_line["医生姓名"]
                this_dep = yuanyi_line["所属科室"].replace("_", "")
                if this_dep == "口腔颌面外科专家门诊":
                    this_dep = "颌面外科专家门诊"

                if this_dep not in deps:
                    raise Exception(yuanyi_line["所属科室"])
                if name_lists[this_dep].has_key(this_name):
                    if len(name_lists[this_dep][this_name]) > 2:
                        name_lists[this_dep][this_name][2] = \
                            str(int(name_lists[this_dep][this_name][2]) + int(yuanyi_line["数量"]))
                    else:
                        name_lists[this_dep][this_name] = \
                            ['0', '0', yuanyi_line["数量"]]
                elif this_dep in deps:
                    if len(name_lists[this_dep]["普通"]) > 2:
                        name_lists[this_dep]["普通"][2] = \
                            str(int(name_lists[this_dep]["普通"][2]) + int(yuanyi_line["数量"]))
                    else:
                        raise Exception("yuanyi_normal")
                else:
                    str1 = ""
                    for key, item in yuanyi_line.items():
                        str1 += str(key) + ":" + str(item) + "\n"
                    # yuanyi_exceptions.append(str1)
                    raise Exception(str1)

        with open(root + "c楼.exp", "w") as output_file:
            for line in c_exps:
                output_file.write(line)

        with open(root + "院医.exp", "w") as output_file:
            for line in yuanyi_exceptions:
                output_file.write(line)

        with open(root + output_file_name, "w") as output_file:
            for dep, names in name_lists.items():
                for name, counts in names.items():
                    # raise Exception(name)
                    output_file.write(dep + "," + name)
                    for count in counts:
                        if count.replace(" ", "") == "0":
                            output_file.write(",")
                        else:
                            output_file.write("," + count)
                    output_file.write("\n")

    def format_output(self, output_root, output_file_name, is_add_old_reg=False):
        inter_output_file_name = output_root + "inter/" + output_file_name
        title_types = ["知名专家", "主任医师", "副主任医师", "主治医师", "普通"]
        exceptions = []
        content = []
        this_item = None

        with open(inter_output_file_name) as input_file:
            datareader = csv.DictReader(input_file)
            pre_name = ""
            pre_title_type = ""
            pre_dep = ""
            type_content = [[], [], [], [], []]
            old_reg_content = []

            is_first_line = True
            for line in datareader:
                if is_first_line:
                    is_first_line = False

                    pre_name = line["挂号医师"]
                    pre_title_type = line["职称"]
                    pre_dep = line["核算科室"]

                    this_item = MedicalServiceChargeItem(
                        name=pre_name, title_type=pre_title_type,
                        dep=pre_dep, is_add_old_reg=False)

                if line["职称"] == "普通":
                    line["挂号医师"] = "普通"

                line["挂号医师"] = line["挂号医师"].replace("ZHY", "")

                if int(line["单价"]) < 50 or (not is_add_old_reg and "特色" in line["职称"]):
                    old_reg_content.append(line)
                    continue

                # 新建条目
                if pre_name != line["挂号医师"] or pre_title_type != line["职称"]:
                    # 未知号种
                    if line["职称"] not in title_types:
                        exceptions.append(line[""] + "\n")
                        continue
                    type_content[title_types.index(pre_title_type)].append(
                        this_item.get_count())

                    pre_name = line["挂号医师"]
                    pre_title_type = line["职称"]
                    pre_price = line["单价"]

                    if pre_dep != line["核算科室"]:
                        pre_dep = line["核算科室"]
                        content.append(type_content)
                        type_content = [[], [], [], [], []]

                    this_item = MedicalServiceChargeItem(
                        name=pre_name, title_type=pre_title_type,
                        dep=pre_dep, is_add_old_reg=False)

                # 新增数据
                data = this_item.add_data(line=line)
                # 若为旧号
                if data is not None:
                    old_reg_content.append(line)

        try:
            type_content[title_types.index(pre_title_type)].append(
                this_item.get_count())
        except:
            raise Exception(pre_title_type)

        content.append(type_content)

        with open(output_root + output_file_name, "w") as output_file:
            for type_content in content:
                for type in type_content:
                    for line in type:
                        output_file.write(line)

        with open(output_root + output_file_name + ".exp", "w") as output_file:
            for line in exceptions:
                output_file.write(line)
        with open(output_root + output_file_name + ".old", "w") as output_file:
            for line in old_reg_content:
                str_line = ""
                for (k, v) in line.items():
                    str_line += str(v) + ","
                output_file.write(str_line[:-1] + "\n")


NIGHT_DEPS = ["_儿科", "_综合治疗二科"]
SPECIAL_DEP = "_综合治疗科"
FACTOR_DICTS = {
    "主治医师": {
        "工作日": 0.3,
        "工作日特需": 0,
        "节假日": 0.4,
        "节假日特需": 0
    },
    "副主任医师": {
        "工作日": 0.42,
        "工作日特需": 0.6,
        "节假日": 0.5,
        "节假日特需": 0.8
    },
    "主任医师": {
        "工作日": 0.44,
        "工作日特需": 0.6,
        "节假日": 0.5,
        "节假日特需": 0.8
    },
    "知名专家": {
        "工作日": 0.75,
        "工作日特需": 0.6,
        "节假日": 0.8,
        "节假日特需": 0.8
    },
    "普通": {
        "工作日": 0.2,
        "工作日特需": 0,
        "节假日": 0.4,
        "节假日特需": 0
    }

}

FACTOR_SPECIALS = [
    {"工作日": 0.55, "节假日": 0.6, "节假日特需": 0.8, "工作日特需": 0.6},
    {"工作日": 0.45, "节假日": 0.5, "节假日特需": 0.8, "工作日特需": 0.6},
]


class MedicalServiceChargeItem(object):
    def __init__(self, name, dep, title_type, is_add_old_reg):
        self.name = name
        self.dep = dep
        self.title_type = title_type
        if self.dep in NIGHT_DEPS:
            self.is_night_dep = True
        else:
            self.is_night_dep = False

        if self.dep == SPECIAL_DEP:
            self.counts = [0, 0, 0, 0, 0 ,0, 0]
            self.prices = [0, 0, 0, 0, 0, 0, 0]
        elif self.is_night_dep:
            self.counts = [0, 0, 0, 0, 0]
            self.prices = [0, 0, 0, 0, 0]
        else:
            self.counts = [0, 0, 0, 0]
            self.prices = [0, 0, 0, 0]
        self.is_add_old_reg = is_add_old_reg

    def add_data(self, line):
        line["数量"] = int(line["数量"])
        line["单价"] = int(line["单价"])
        if self.dep == SPECIAL_DEP:
            # 门诊,特需,门诊复诊,夜诊
            # 门诊,特需,门诊复诊
            if line["是否夜诊"] == "夜诊号":
                if self.prices[3] != 0 and self.prices[3] != line["单价"]:
                    return -1
                self.counts[3] += line["数量"]
                self.prices[3] = line["单价"]
            else:
                if line["是否工作日"] == "工作日":
                    i = 0
                else:
                    i = 4
                if "复诊" in line["号种"]:
                    if self.prices[2 + i] != 0 and self.prices[2 + i] != line["单价"]:
                        return -1
                    self.counts[2 + i] += line["数量"]
                    self.prices[2 + i] = line["单价"]
                elif "特需" in line["号种"] or "特色" in line["号种"]:
                    if self.is_add_old_reg or "特需" in line["号种"]:
                        if self.prices[1 + i] != 0 and self.prices[1 + i] != line["单价"]:
                            raise Exception(line)
                        self.counts[1 + i] += line["数量"]
                        self.prices[1 + i] = line["单价"]
                    else:
                        return -1
                else:
                    if self.prices[0 + i] != 0 and self.prices[0 + i] != line["单价"]:
                        return -1
                    self.counts[0 + i] += line["数量"]
                    self.prices[0 + i] = line["单价"]
        elif self.is_night_dep:
            # 工作日：门诊,门诊复诊,夜诊
            # 节假日：门诊,门诊复诊
            if line["是否夜诊"] == "夜诊号":
                if self.prices[2] != 0 and self.prices[2] != line["单价"]:
                    return -1
                self.counts[2] += line["数量"]
                self.prices[2] = line["单价"]
            else:
                if line["是否工作日"] == "工作日":
                    i = 0
                else:
                    i = 3
                if "复诊" in line["号种"]:
                    if self.prices[1 + i] != 0 and self.prices[1 + i] != line["单价"]:
                        return -1
                    self.counts[1 + i] += line["数量"]
                    self.prices[1 + i] = line["单价"]
                else:
                    if self.prices[0 + i] != 0 and self.prices[0 + i] != line["单价"]:
                        return -1
                    self.counts[0 + i] += line["数量"]
                    self.prices[0 + i] = line["单价"]
        else:
            # 工作日：门诊,门诊复诊
            # 节假日：门诊,门诊复诊
            if line["是否工作日"] == "工作日":
                i = 0
            else:
                i = 2
            if "复诊" in line["号种"]:
                if self.prices[1 + i] != 0 and self.prices[1 + i] != line["单价"]:
                    return -1
                self.counts[1 + i] += line["数量"]
                self.prices[1 + i] = line["单价"]
            else:
                if self.prices[0 + i] != 0 and self.prices[0 + i] != line["单价"]:
                    return -1
                self.counts[0 + i] += line["数量"]
                self.prices[0 + i] = line["单价"]
            return

    def get_count(self, counts=None):
        if counts is None:
            counts = self.counts
        str_counts = str(counts).replace("[", "").replace("]", "")
        title = self.dep + "," + self.title_type + "," + self.name + ","
        return title + str_counts + "\n"

    def get_sum(self, counts=None):
        if counts is None:
            counts = self.counts
        if self.dep == SPECIAL_DEP:
            # 门诊,特需,门诊复诊,夜诊
            # 门诊,特需,门诊复诊
            counts.insert(4, sum(counts[0:4]))
            counts.append(sum(counts[5:]))
            counts.append(sum(counts[0:4]) + counts[-1])
        elif self.is_night_dep:
            # 工作日：门诊,门诊复诊,夜诊,小计
            # 节假日：门诊,门诊复诊,小计
            counts.insert(3, sum(counts[0:3]))
            counts.append(counts[4] + counts[5])
            counts.append(sum(counts[0:3]) + counts[-1])
        else:
            # 工作日：门诊,门诊复诊,小计
            # 节假日：门诊,门诊复诊,小计
            counts.insert(2, counts[0] + counts[1])
            counts.append(counts[3] + counts[4])
            counts.append(sum(counts[0:2]) + counts[-1])

        str_counts = str(counts).replace("[", "").replace("]", "")
        title = self.dep + "," + self.title_type + "," + self.name + ","
        return title + str_counts + "\n"

    def get_item(self, counts=None, prices=None):
        # factor_list = []
        factor_sums = []
        sums = []
        # 新记录
        if counts is None:
            counts = self.counts
        if prices is None:
            prices = self.prices
        new_item_str = self.dep + "," + self.title_type + "," + self.name + ","

        if self.dep == SPECIAL_DEP:
            # 门诊,特需,门诊复诊,夜诊
            # 门诊,特需,门诊复诊

            for i in range(len(counts)):
                sums.append(counts[i] * prices[i])

            counts.insert(4, sum(counts[0:4]))
            counts.append(sum(counts[5:]))
            counts.append(sum(counts[0:4]) + counts[-1])
            sums.insert(4, sum(sums[0:4]))
            sums.append(sum(sums[5:]))
            sums.append(sum(sums[0:4]) + sums[-1])
            factor_sums.insert(4, sum(factor_sums[0:4]))
            factor_sums.append(sum(factor_sums[5:]))
            factor_sums.append(int(round(sum(factor_sums[0:4]) + factor_sums[-1], 0)))
            prices = ["", "", "", "", "", ""]

        elif self.is_night_dep:
            # 工作日：门诊,门诊复诊,夜诊,小计
            # 节假日：门诊,门诊复诊,小计

            for i in range(len(counts)):
                sums.append(counts[i] * prices[i])

            counts.insert(3, sum(counts[0:3]))
            counts.append(counts[4] + counts[5])
            counts.append(sum(counts[0:3]) + counts[-1])
            sums.insert(3, sum(sums[0:3]))
            sums.append(sums[4] + sums[5])
            sums.append(sum(sums[0:3]) + sums[-1])
            factor_sums.insert(3, sum(factor_sums[0:3]))
            factor_sums.append(factor_sums[4] + factor_sums[5])
            factor_sums.append(int(round(sum(factor_sums[0:3]) + factor_sums[-1], 0)))
            prices = ["", "", "", "", ""]
        else:
            # 工作日：门诊,门诊复诊,小计
            # 节假日：门诊,门诊复诊,小计

            for i in range(len(counts)):
                sums.append(counts[i] * prices[i])

            counts.insert(2, counts[0] + counts[1])
            counts.append(counts[3] + counts[4])
            counts.append(sum(counts[0:2]) + counts[-1])
            sums.insert(2, sums[0] + sums[1])
            sums.append(sums[3] + sums[4])
            sums.append(sum(sums[0:2]) + sums[-1])
            factor_sums.insert(2, factor_sums[0] + factor_sums[1])
            factor_sums.append(factor_sums[3] + factor_sums[4])
            factor_sums.append(int(round(sum(factor_sums[0:2]) + factor_sums[-1], 0)))
            prices = ["", "", "", ""]

        str_counts = str(counts).replace("[", "").replace("]", "")
        str_prices = str(prices).replace("[", "").replace("]", "").replace("\'", "")
        str_sums = str(sums).replace("[", "").replace("]", "")
        str_factor_sums = str(factor_sums).replace("[", "").replace("]", "")
        new_item_str += str_counts + "," + str_factor_sums + str_prices + "," + str_sums + "," + "\n"
        return new_item_str


class MedicineExcelReport(object):
    def init(self, input_file_name, output_file_name):
        self.input_file = openpyxl.load_workbook(input_file_name)
        self.output_file_name = output_file_name

    def write_data(self):
        sheet_name_list = []
        data = []

        this_sheet = self.input_file.get_sheet_by_name(sheet_name_list[0])
        for rows in this_sheet['A1':'A9']:  # 把日期数据写入新表
            for cell in rows:
                cell.value = data
                print(cell.coordinate, cell.value)

        return self.input_file
