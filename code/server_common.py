#!/usr/bin/python
# -*- coding: utf-8 -*-


import os


def listdir(path, file_type):
    file_list = []
    file_num = 0
    files = os.listdir(path)  # 列出目录下的所有文件和目录
    for line in files:
        if file_type == "data":
            if line.split(".")[-1] == "csv":
                file_path = os.path.join(path, line)
                file_list.append(file_path)
                file_num += 1
        elif file_type == "rule":
            file_path = os.path.join(path, line)
            file_list.append(file_path)
            file_num += 1

    return file_num, file_list


def get_file_list(file_path, file_type):
    file_name_list = []
    file_num, file_list = listdir(file_path, file_type=file_type)
    for file_path in file_list:
        file_name = file_path.split("/")[-1]
        file_name_list.append(file_name)
    return file_num, file_name_list
