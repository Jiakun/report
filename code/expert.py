# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas as pd
import shlex
import os
import os.path
import re
import csv
from collections import OrderedDict


class ExpertReport(object):
    def __init__(self, input_file_name, output_file_name):
        if output_file_name is None or input_file_name is None:
            raise Exception("File name cannot be none.")
        self.output_file_name = output_file_name
        try:
            self.content = pd.read_csv(input_file_name)
        except:
            raise Exception("Cannot read input file.")
        self.file = open(input_file_name)
        self.size = len(self.file.readlines()) - 2
        self.file.close()

    def save_by_different_expert_level(self, output_root, output_file_name):
        pd.options.display.max_rows = 999
        grouped_data = self.content.groupby(["科室", "号种"])
        with open(output_root + "inter/" + output_file_name, "w") as output_file:
            output_file.write(str(grouped_data["数量"].sum()))

        head_root = output_root + "head/" + output_file_name
        with open(head_root + "科室", "w") as output_file:
            output_file.write(str(self.content.groupby(["科室"])["数量"].sum()))
        with open(head_root + "号种", "w") as output_file:
            output_file.write(str(self.content.groupby(["号种"])["数量"].sum()))

            # output_file.write(str(self.content["数量"].sum()))

    def sum_registration_type(self, reg_type):
        if "夜诊" in reg_type:
            return 5
        if "副" in reg_type:
            return 2
        elif "治" in reg_type and "洁" not in reg_type:
            return 3
        elif "主" in reg_type:
            return 1
        elif "知" in reg_type or "特需" in reg_type or "特色" in reg_type:
            return 0
        elif "普通" in reg_type or "高资" in reg_type \
                or "指导" in reg_type or "统筹医保实名" in reg_type:
            return 4
        else:
            return 5
            # raise Exception(reg_type)

    def format_raw_statistic_file(self, root_dir):
        # registration_types = ["知名专家", "主任医师", "副主任医师", "主治医师", "普通"]

        for parent, dirnames, filenames in os.walk(root_dir + "inter/"):
            content = []
            for filename in filenames:
                with open(root_dir + "inter/" + filename) as input_file:
                    content = input_file.readlines()
                with open(root_dir + "format/" + filename, "w") as output_file:
                    for line in content:
                        output_file.write(','.join(line.split()) + "\n")

    def clinic_create(self, root_dir, filenames):
            for filename in filenames:
                dep_types = []
                dep_counts = []
                is_first_line = True
                with open(root_dir + "head/" + filename + "科室") as dep_input_file:
                    content = dep_input_file.readlines()
                    for line in content:
                        if is_first_line:
                            is_first_line = False
                            continue
                        if "dtype:" in line:
                            continue
                        dep_types.append(line.split(" "[0]))

                is_first_line = True
                with open(root_dir + "format/" + filename) as input_file:
                    counts = [0, 0, 0, 0, 0, 0]
                    dep_type = ""
                    for line in input_file:
                        if is_first_line:
                            is_first_line = False
                            continue

                        if "dtype:" in line:
                            continue

                        line_split = line.split(",")

                        is_new_dep = False

                        if len(line_split) > 2:
                            dep_keys = ["科", "保健", "颞下颌关节病及口面痛",
                                        "激光整形美容室", "院医室"]
                            for key in dep_keys:
                                if key in line:
                                    is_new_dep = True
                            if is_new_dep:
                                dep_counts.append(
                                    dep_type + "," +
                                    str(counts).replace("[", "").replace("]", ""))
                                counts = [0, 0, 0, 0, 0, 0]
                                dep_type = line_split[0]
                                reg_type = "".join(line_split[1:-1])
                                count = int(line_split[-1])
                                is_new_dep = False
                            else:
                                reg_type = "".join(line_split[0:-1])
                                count = int(line_split[-1])
                        else:
                            reg_type = line_split[0]
                            count = int(line_split[1])

                        counts[self.sum_registration_type(reg_type)] += count
                    dep_counts.append(
                        dep_type + "," +
                        str(counts).replace("[", "").replace("]", ""))
                with open(root_dir + filename, "w") as output_file:
                    output_file.write("科室,知名专家,主任医师,副主任医师,主治医师,普通,其他\n")
                    for counts in dep_counts[1:]:
                        output_file.write(counts + "\n")


class MedicalServiceChargeReport(object):
    # 医事服务费各科室计算报表
    def __init__(self, input_path, input_file_name):
        try:
            self.content = pd.read_csv(input_path + input_file_name)
        except:
            raise Exception("Cannot read input file.")
        self.file = open(input_path + input_file_name)
        self.size = len(self.file.readlines()) - 2
        self.file.close()
        pd.set_option('display.max_rows', None)
        self.special_names = [[], []]
        self.get_special_charge_factor(input_path + "special_factors.csv")

    def get_special_charge_factor(self, input_file_name):
        with open(input_file_name) as input_file:
            for line in input_file:
                line_split = line.split(",")
                self.special_names[int(line_split[0])].append(line_split[1].replace("\n", ""))
        # raise Exception(self.special_names[0][0])

    def pre_format_day(self, input_file_name):
        try:
            weekday = True
            day = True
            with open(input_file_name) as input_file:
                for line in input_file:
                    if "工作日," in line:
                        weekday = "工作日"
                    elif "节假日," in line:
                        weekday = "节假日"
                    if "白天号," in line:
                        day = "白天号"
                    elif "夜诊号," in line:
                        day = "夜诊号"
        except:
            raise Exception("Cannot work on this file.")

    def get_type_dict(self, reg_type, dict, is_add_old_reg):
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
                or "离休统筹医保号" in reg_type or "病区" in reg_type:
            dict[4].append(reg_type)
        else:
            return "Exception"

    def group_data(self, output_root, output_file_name):
        type_dict = [[], [], [], [], []]
        types = ["知名专家", "主任医师", "副主任医师", "主治医师", "普通", "特需"]

        self.content["职称"] = self.content["号种"]

        for data in self.content["号种"]:
            self.get_type_dict(reg_type=data, dict=type_dict, is_add_old_reg=False)

        for i in range(len(type_dict)):
            set_type = list(set(type_dict[i]))
            self.content["职称"] = \
                self.content["职称"].replace(set_type, [types[i]] * len(set_type))

        # self.content["挂号医师"] = self.content["挂号医师"].replace(r"[\u4e00-\u9fa5]*ZHY", r"[\u4e00-\u9fa5]*")

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
        grouped_data = self.content.groupby(["科室名称", "医生姓名"])
        sum_data = grouped_data["金额"].count().reset_index()
        sum_data.to_csv(output_root + output_file_name)

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
                elif this_dep == "_预防保健科":
                    this_dep = "预防保健"
                    break
                elif this_dep.replace("_", "") in dep:
                    this_dep = this_dep.replace("_", "")
                    break
            try:
                if name_lists[this_dep].has_key(this_name):
                    name_lists[this_dep][this_name] = line_split[1:]
            except:
                raise Exception(this_name)

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

        yuanyi_exceptions = []
        is_first_line = True
        # ,科室,医师姓名,职工姓名（数量）
        yuanyi_input_file = open(root + "经院医转科室治疗数据.csv.out")
        yuanyi_lines = yuanyi_input_file.readlines()
        for yuanyi_line in yuanyi_lines:
            if is_first_line:
                is_first_line = False
                continue
            line_split = yuanyi_line[:-1].split(",")
            this_dep = line_split[1]
            this_name = line_split[2]
            for dep in deps:
                if this_dep == "颌面外科专家门诊(综合楼三楼)":
                    this_dep = "激光整形美容室"
                elif this_dep == "口腔颌面外科专家门诊":
                    this_dep = "颌面外科专家门诊"
                    break
                elif this_dep == "_预防保健科":
                    this_dep = "预防保健"
                    break
                elif this_dep.replace("_", "") in dep:
                    this_dep = this_dep.replace("_", "")
                    break
                elif this_dep.replace("科", "") in dep:
                    this_dep = this_dep.replace("科", "")
                elif dep in this_dep.replace("_", ""):
                    this_dep = dep.replace("_", "")
            try:
                if name_lists[this_dep].has_key(this_name):
                    if len(name_lists[this_dep][this_name]) > 2:
                        name_lists[this_dep][this_name][2] = \
                            str(int(name_lists[this_dep][this_name][2]) + int(line_split[3]))
                    else:
                        name_lists[this_dep][this_name] = ["0", "0", line_split[3]]
                elif this_dep in deps:
                    if len(name_lists[this_dep]["普通"]) > 2:
                        name_lists[this_dep]["普通"][2] = \
                            str(int(name_lists[this_dep]["普通"][2]) + int(line_split[3]))
                    else:
                        name_lists[this_dep]["普通"] = ["0", "0", line_split[3]]
            except:
                yuanyi_exceptions.append(yuanyi_line)

        free_maps = {
            "特诊": "特诊科",
            "口外": "颌面外科门诊",
            "牙周": "牙周科",
            "急诊": "急诊科",
            "种植": "种植科"
        }

        free_exceptions = []
        is_first_line = True
        # 科室,专家姓名,专家号数
        free_input_file = open(root + "医务处免费人次统计.csv")
        free_lines = free_input_file.readlines()
        for free_line in free_lines:
            if is_first_line:
                is_first_line = False
                continue
            line_split = free_line.split(",")
            this_name = line_split[1]
            try:
                this_dep = free_maps[line_split[0]]
                if len(name_lists[this_dep][this_name]) > 2:
                    name_lists[this_dep][this_name][2] = \
                        str(int(name_lists[this_dep][this_name][2]) + int(line_split[2]))
                else:
                    name_lists[this_dep][this_name] = ["0", "0", line_split[3]]
            except:
                free_exceptions.append(free_line)

        with open(root + "c楼.exp", "w") as output_file:
            for line in c_exps:
                output_file.write(line)

        with open(root + "免费.exp", "w") as output_file:
            for line in free_exceptions:
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
                        if count == "0":
                            output_file.write(",")
                        else:
                            output_file.write("," + count)
                    output_file.write("\n")

    def format_output(self, output_root, output_file_name, is_only_count=True, is_add_old_reg=False):
        inter_output_file_name = output_root + "inter/" + output_file_name
        title_types = ["知名专家", "主任医师", "副主任医师", "主治医师", "普通"]
        exceptions = []
        content = []
        this_item = None
        if is_only_count:
            content.append(["科室,职级,姓名,计数\n"])

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

                    if is_only_count:
                        type_content[title_types.index(pre_title_type)].append(
                            this_item.get_count())
                    else:
                        type_content[title_types.index(pre_title_type)].append(
                            this_item.get_item(special_names=self.special_names))

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

        if is_only_count:
            type_content[title_types.index(pre_title_type)].append(
                this_item.get_count())
        else:
            type_content[title_types.index(pre_title_type)].append(
                this_item.get_item(special_names=self.special_names))
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
                    raise Exception(line)
                self.counts[3] += line["数量"]
                self.prices[3] = line["单价"]
            else:
                if line["是否工作日"] == "工作日":
                    i = 0
                else:
                    i = 4
                if "复诊" in line["号种"]:
                    if self.prices[2 + i] != 0 and self.prices[2 + i] != line["单价"]:
                        raise Exception(line)
                    self.counts[2 + i] += line["数量"]
                    self.prices[2 + i] = line["单价"]
                elif "特需" in line["号种"] or "特色" in line["号种"]:
                    if self.is_add_old_reg or "特需" in line["号种"]:
                        if self.prices[1 + i] != 0 and self.prices[1 + i] != line["单价"]:
                            raise Exception(line)
                        self.counts[1 + i] += line["数量"]
                        self.prices[1 + i] = line["单价"]
                    else:
                        raise Exception(line)
                else:
                    if self.prices[0 + i] != 0 and self.prices[0 + i] != line["单价"]:
                        raise Exception(line)
                    self.counts[0 + i] += line["数量"]
                    self.prices[0 + i] = line["单价"]
        elif self.is_night_dep:
            # 工作日：门诊,门诊复诊,夜诊
            # 节假日：门诊,门诊复诊
            if line["是否夜诊"] == "夜诊号":
                if self.prices[2] != 0 and self.prices[2] != line["单价"]:
                    raise Exception(line)
                self.counts[2] += line["数量"]
                self.prices[2] = line["单价"]
            else:
                if line["是否工作日"] == "工作日":
                    i = 0
                else:
                    i = 3
                if "复诊" in line["号种"]:
                    if self.prices[1 + i] != 0 and self.prices[1 + i] != line["单价"]:
                        raise Exception(line)
                    self.counts[1 + i] += line["数量"]
                    self.prices[1 + i] = line["单价"]
                else:
                    if self.prices[0 + i] != 0 and self.prices[0 + i] != line["单价"]:
                        raise Exception(line)
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
                    raise Exception(line)
                self.counts[1 + i] += line["数量"]
                self.prices[1 + i] = line["单价"]
            else:
                if self.prices[0 + i] != 0 and self.prices[0 + i] != line["单价"]:
                    raise Exception(line)
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

    def get_item(self, counts=None, prices=None, special_names=[[], []]):
        # factor_list = []
        factor_sums = []
        sums = []
        # 新记录
        if counts is None:
            counts = self.counts
        if prices is None:
            prices = self.prices
        new_item_str = self.dep + "," + self.title_type + "," + self.name + ","

        if self.name in special_names[0]:
            dicts = FACTOR_SPECIALS[0]
        elif self.name in special_names[1]:
            dicts = FACTOR_SPECIALS[1]
        else:
            dicts = FACTOR_DICTS[self.title_type]

        if self.dep == SPECIAL_DEP:
            # 门诊,特需,门诊复诊,夜诊
            # 门诊,特需,门诊复诊

            factor_list = [
                dicts["工作日"],
                dicts["工作日特需"],
                dicts["工作日"],
                dicts["节假日"],
                dicts["节假日"],
                dicts["节假日特需"],
                dicts["节假日"]
                ]
            for i in range(len(counts)):
                sums.append(counts[i] * prices[i])
                factor_sums.append(round(sums[i] * factor_list[i], 1))

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
            factor_list_show = factor_list
        elif self.is_night_dep:
            # 工作日：门诊,门诊复诊,夜诊,小计
            # 节假日：门诊,门诊复诊,小计

            factor_list = [
                dicts["工作日"],
                dicts["工作日"],
                dicts["节假日"],
                dicts["节假日"],
                dicts["节假日"]
                ]
            for i in range(len(counts)):
                sums.append(counts[i] * prices[i])
                factor_sums.append(round(sums[i] * factor_list[i]))

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
            factor_list_show = factor_list
        else:
            # 工作日：门诊,门诊复诊,小计
            # 节假日：门诊,门诊复诊,小计

            factor_list = [
                dicts["工作日"],
                dicts["工作日"],
                dicts["节假日"],
                dicts["节假日"]
            ]

            for i in range(len(counts)):
                sums.append(counts[i] * prices[i])
                factor_sums.append(round(sums[i] * factor_list[i], 1))

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
            factor_list_show = [dicts["工作日"],
                                dicts["节假日"]]

        str_counts = str(counts).replace("[", "").replace("]", "")
        str_prices = str(prices).replace("[", "").replace("]", "").replace("\'", "")
        str_sums = str(sums).replace("[", "").replace("]", "")
        str_factor_sums = str(factor_sums).replace("[", "").replace("]", "")
        str_factor_list = str(factor_list_show).replace("[", "").replace("]", "")
        new_item_str += str_counts + "," + str_factor_sums + str_prices + "," + str_sums + "," + str_factor_list + "\n"
        return new_item_str
