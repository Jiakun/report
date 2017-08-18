# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas as pd
import shlex
import os
import os.path
import re
import csv
import time
from collections import OrderedDict


class ExpertCallReport(object):
    def __init__(self, input_file_name, output_file_name):
        if output_file_name is None or input_file_name is None:
            raise Exception("File name cannot be none.")
        self.output_file_name = output_file_name
        try:
            self.content = pd.read_csv(input_file_name).drop_duplicates()

        except:
            raise Exception("Cannot read input file.")
        self.file = open(input_file_name)
        self.size = len(self.file.readlines()) - 2
        self.file.close()
        self.periods = [0, 0]

    def set_count_periods(self, dates):
        self.periods = dates

    @staticmethod
    def set_rules(rules, output_file_name):
        with open(output_file_name, "w") as output_file:
            for rule in rules:
                output_file.write(rule)

    @staticmethod
    def get_pre_defined_first_counts(input_file_name, rule_file_name, output_file_name, periods):
        data = pd.read_csv(input_file_name).drop_duplicates()
        periods[0] = time.strptime(periods[0], "%Y-%m-%d")
        periods[1] = time.strptime(periods[1], "%Y-%m-%d")

        settings = []
        with open(rule_file_name) as input_file:
            settings_reader = csv.DictReader(input_file)
            for line in settings_reader:
                settings.append(line)

        weekday_data = data.drop_duplicates(["日期", "星期"])
        weekday_counts = weekday_data.groupby(["星期"])["星期"].count()

        weekday_counts.to_csv(rule_file_name + ".weekday")

        weekday_c = {}
        weekday_maps = {"一": 0, "四": 3, "日": 6,
                        "二": 1, "五": 4,
                        "三": 2, "六": 5}
        with open(rule_file_name + ".weekday") as input_file:
            for line in input_file:
                line_s = line[:-1].split(",")
                weekday_c[weekday_maps[line_s[0][-3:]]] = int(line_s[1])

        weekday_data["日期"] = pd.to_datetime(weekday_data["日期"])
        content = []
        for setting in settings:
            ss = setting["出诊时间"].split("；")
            for single_s in ss:
                counts = 0
                if "：" in single_s:
                    dates = single_s.split("：")[0].split("-")
                    if len(dates[0]) < 4 and len(dates[1]) < 4:
                        this_weekdays = weekday_data
                    elif len(dates[0]) < 4:
                        dates[1] = pd.to_datetime(dates[1])
                        this_weekdays = \
                            weekday_data[weekday_data["日期"] <= dates[1]]
                    elif len(dates[1]) < 4:
                        dates[0] = pd.to_datetime(dates[0])
                        this_weekdays = \
                            weekday_data[weekday_data["日期"] >= dates[0]]
                    else:
                        dates = pd.to_datetime(dates)
                        this_weekdays = \
                            weekday_data[(weekday_data["日期"] >= dates[0]) &
                                         (weekday_data["日期"] <= dates[1])]

                    this_weekday_count = this_weekdays.groupby(["星期"])["日期"].count()

                    if len(single_s.split("：")[1]) < 12:
                        continue
                    weekdays = single_s.split("：")[1].split("、")
                    for weekday in weekdays:
                        if len(weekday) < 6:
                            continue
                        w_i = weekday_maps[weekday[3:6]]
                        try:
                            counts += this_weekday_count[w_i]
                            if "全天" in weekday:
                                counts += this_weekday_count[w_i]
                        except:
                            pass
                    content.append(setting["科室"] + "," + setting["姓名"] + "," + str(counts) + "\n")
                else:
                    # 空记录
                    if len(single_s) < 12:
                        continue
                    weekdays = single_s.split("、")
                    for weekday in weekdays:
                        try:
                            counts += weekday_c[weekday_maps[weekday[3:6]]]
                        except:
                            raise Exception(single_s)
                        if "全天" in weekday:
                            counts += weekday_c[weekday_maps[weekday[3:6]]]
                    content.append(setting["科室"] + "," + setting["姓名"] + "," + str(counts) + "\n")

        with open(output_file_name, "w") as output_file:
            for line in content:
                output_file.write(line)



    @staticmethod
    def pre_read_setting(rule_file_name, data_file_name, output_file_name, periods):
        periods[0] = time.strptime(periods[0], "%Y-%m-%d")
        periods[1] = time.strptime(periods[1], "%Y-%m-%d")

        settings = []
        with open(rule_file_name) as input_file:
            settings_reader = csv.DictReader(input_file)
            for line in settings_reader:
                settings.append(line)

        content = []
        with open(data_file_name) as input_file:
            data = csv.DictReader(input_file)
            for d in data:
                data_date = time.strptime(d['日期'], "%m/%d/%Y")
                if periods[0] > data_date or periods[1] < data_date:
                    continue
                for setting in settings:
                    if setting["姓名"] == d["医生"]:
                        if d["科室名称"] == "颌面外科专家门诊(综合楼三楼)":
                            d["科室名称"] = "口腔颌面外科"
                        elif "预防保健" in d["科室名称"]:
                            d["科室名称"] = "预防保健科"
                        elif d["科室名称"] == "颞下颌关节病及口面痛":
                            d["科室名称"] = "关节中心"
                        elif "科" in d["科室名称"]:
                            d["科室名称"] = d["科室名称"].split("科")[0] + "科"
                        ss = setting["出诊时间"].split("；")
                        for single_s in ss:
                            if "：" in single_s:
                                dates = single_s.split("：")[0].split("-")
                                weekdays = single_s.split("：")[1].split("、")
                                is_included_date = False
                                for weekday in weekdays:
                                    if len(weekday) < 12:
                                        continue
                                    if weekday[3:6] in d["星期"]:
                                        if "全天" in weekday or weekday[6:] in d["时段"]:
                                            is_included_date = True
                                            continue
                                if not is_included_date:
                                    continue

                                try:
                                    date_after = time.strptime(dates[0], "%Y.%m.%d") if len(dates[0]) > 4 else 0
                                    date_before = time.strptime(dates[1], "%Y.%m.%d") if len(dates[1]) > 4 else 0
                                except:
                                    raise Exception(dates)

                                if date_after == 0 and date_before == 0:
                                    content.append(d)
                                elif date_after == 0 and data_date <= date_before:
                                    content.append(d)
                                elif date_before == 0 and data_date >= date_after:
                                    content.append(d)
                                elif (data_date >= date_after) and (data_date <= date_before):
                                    content.append(d)
                            else:
                                if len(single_s) < 12:
                                    continue
                                weekdays = single_s.split("、")
                                for weekday in weekdays:
                                    if weekday[3:6] in d["星期"]:
                                        if "全天" in weekday or weekday[6:] in d["时段"]:
                                            content.append(d)

        with open(output_file_name, "w") as output_file:
            str = ""
            for key, item in content[0].items():
                str += key + ","
            str = str[:-1] + "\n"
            output_file.write(str)
            for c in content:
                str = ""
                for key, item in c.items():
                    str += item + ","
                str = str[:-1] + "\n"
                output_file.write(str)

    @staticmethod
    def save_all_results(output_root, output_file_name):
        content = OrderedDict()
        content[0] = "序号,科室名称,医生,初诊次数,初诊合计,复诊合计\n"

        is_first_line = True
        with open(output_root + output_file_name + ".fc") as input_file:
            for line in input_file:
                if is_first_line:
                    is_first_line = False
                    continue
                name = line.split(",")[2]
                dep = line.split(",")[1]
                content[dep+name] = line[:-1] + ","
        is_first_line = True
        with open(output_root + output_file_name + ".ofc") as input_file:
            for line in input_file:
                if is_first_line:
                    is_first_line = False
                    continue
                name = line.split(",")[2]
                dep = line.split(",")[1]
                content[dep + name] = line[:-1] + ","

        is_first_line = True
        with open(output_root + output_file_name + ".fs") as input_file:
            for line in input_file:
                if is_first_line:
                    is_first_line = False
                    continue
                name = line.split(",")[2]
                dep = line.split(",")[1]
                try:
                    content[dep+name] += line.replace("\n", "").split(",")[-1] + ","
                except:
                    pass

        is_first_line = True
        with open(output_root + output_file_name + ".ss") as input_file:
            for line in input_file:
                if is_first_line:
                    is_first_line = False
                    continue
                name = line.split(",")[2]
                dep = line.split(",")[1]
                try:
                    content[dep+name] += line.replace("\n", "").split(",")[-1] + "\n"
                except:
                    pass

        with open(output_root + output_file_name + ".tmp", "w") as output_file:
            for key, value in content.items():
                output_file.write(value)

        data = pd.read_csv(output_root + output_file_name + ".tmp")
        pd.options.display.max_rows = 9999
        grouped_data = data.groupby(["科室名称", "医生"])
        first_counts = grouped_data["初诊次数"].sum().reset_index()
        first_sums = grouped_data["初诊合计"].sum().reset_index()
        sub_sums = grouped_data["复诊合计"].sum().reset_index()
        all_data = first_counts
        all_data["初诊合计"] = pd.Series(first_sums["初诊合计"])
        all_data["复诊合计"] =pd.Series(sub_sums["复诊合计"])
        all_data["合计"] = all_data["初诊合计"] + all_data["复诊合计"]

        all_data.to_csv(output_root + output_file_name)
        
    def save_by_different_time(self, output_root, output_file_name):
        pd.options.display.max_rows = 9999

        orthodontics = self.content[self.content["科室名称"] == "正畸科"]
        others = self.content[self.content["科室名称"] != "正畸科"]
        others = others[others["初诊"] > 0]
        drop_dup_grouped_data = others.drop_duplicates(['科室名称', '日期', '医生', "时段"]).groupby(["科室名称", "医生", "星期", "时段"])
        first_counts = drop_dup_grouped_data['日期'].count().reset_index()
        first_counts = first_counts.groupby(["科室名称", '医生'])["日期"].sum().reset_index()
        orthodontics_drop_dup_grouped_data = orthodontics.drop_duplicates(['科室名称', '日期', '医生', "时段"]).groupby(["科室名称", "医生", "星期", "时段"])
        orthodontics_first_counts = orthodontics_drop_dup_grouped_data['日期'].count().reset_index()
        orthodontics_first_counts = orthodontics_first_counts.groupby(["科室名称", "医生"])["日期"].sum().reset_index()

        grouped_data = self.content.groupby(["科室名称", "医生", "星期", "时段"])
        first_sums = grouped_data["初诊"].sum().reset_index()
        first_sums = first_sums.groupby(["科室名称", "医生"])["初诊"].sum().reset_index()
        sub_sums = grouped_data["复诊"].sum().reset_index()
        sub_sums = sub_sums.groupby(["科室名称", "医生"])["复诊"].sum().reset_index()

        first_counts.to_csv(output_root + output_file_name + ".fc")
        orthodontics_first_counts.to_csv(output_root + output_file_name + ".ofc")
        first_sums.to_csv(output_root + output_file_name + ".fs")
        sub_sums.to_csv(output_root + output_file_name + ".ss")
        self.save_all_results(output_root, output_file_name)

    @staticmethod
    def compare_manual_file(m_input_file_name, c_input_file_name, output_file_name):
        c_content = {}
        with open(c_input_file_name) as input_file:
            c_reader = csv.DictReader(input_file)
            for line in c_reader:
                c_content[line["科室名称"] + line["医生"]] = line

        exps = []
        with open(m_input_file_name) as input_file:
            m_reader = csv.DictReader(input_file)
            for line in m_reader:
                if len(line["初诊次数"]) < 1:
                    continue
                try:
                    c_line = c_content[line["科室名称"] + line["医生"].replace("&", "")]
                except:
                    exps.append(line)
                    continue
                if line["科室名称"] == "正畸科":
                    if line["初诊次数"] == c_line["初诊次数"] and \
                                    line["合计"] == c_line["合计"]:
                        continue

                elif line["初诊次数"] == c_line["初诊次数"] and \
                    line["合计"] == c_line["合计"] and \
                    line["初诊合计"] == c_line["初诊合计"]:
                    continue
                exps.append(line)

        with open(output_file_name, "w") as output_file:
            for exp in exps:
                for key, item in exp.items():
                    output_file.write(item + ",")
                output_file.write("\n")
