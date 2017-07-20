# -*- coding: utf-8 -*-

from abc import abstractmethod
import pandas
import shlex
import os
import os.path
import re


class ExpertReport(object):
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

    def save_by_different_expert_level(self, output_root, output_file_name):
        pandas.options.display.max_rows = 999
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
