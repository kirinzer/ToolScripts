#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import sys
import math
import os
import subprocess
import re

# 该脚本用于检查分支和 podspec 中 version 是否匹配
# 在静默模式下自动校正，非静默模式输出 log
__author__ = "kirinzer"

class Cache:
    versionInBranch = ""
    quietMode = 0 # 默认关闭，输出 log

# 读取 git branch 信息
def readBrachInfo():
    print("try to read repo's branch info:")
    cmd = "git branch | sed -n '/\* /s///p'"
    result = os.system(cmd)
    
    if result is not 0:
        # failed
        return ""
    else:
        output = subprocess.getoutput(cmd)
        return output

# 过滤 branch 中的 / 后面的部分，按照规范应该是一串数字
def filterAlphabet(branchName):
    strs = branchName.split("/")
    target = strs[-1]
    return target

# 读取工程中的 podspec 文件，如果有多个也一并读取，将 version 对应的值存入一个数组
def readPodspecFiles(files):
    for filePath in files:
        _readFile(filePath)

def _readFile(filePath):
    file = open(filePath, "r", encoding = "utf-8")
    fileData = ""
    for line in file: # read line one by one
        if "version = " in line:
            podspecVersion = getPodspecVersion(line)
            if podspecVersion != Cache.versionInBranch:
                # 处理静默模式
                if Cache.versionInBranch is not None and Cache.quietMode == 1: # 打开时修改不匹配的文件
                    # replace version
                    line = line.replace(podspecVersion ,Cache.versionInBranch)
                    fileData += line
                    continue # skip append line in current loop
                else:
                    print("version not match: "+filePath)
                    return # 中断后续处理
        fileData += line

    # rewrite file
    if Cache.quietMode == 1:
        rewritePodspec(filePath ,fileData)

def getPodspecVersion(line):
    strs = line.split("\"")
    return strs[1]

def rewritePodspec(filePath, fileData):
    with open(filePath,"w",encoding="utf-8") as f:
        f.write(fileData)

def checkBranchAndVersion(path):
    branchName = readBrachInfo()
    res = filterAlphabet(branchName)
    
    Cache.versionInBranch = res

    readPodspecFiles(path)

# 调用检查分支和版本的方法 入参需要检查的组件的根目录 podspec 所在以及是否静默模式
# quiet mode 打开时，不会中断和输出提示，会直接静默修改不合规的文件
# quiet mode 关闭时，会输出不合规的提示，不会修改文件
def doAction():
    params = []
    for arg in sys.argv[1:]: # arg[0] is fileName so skip
        params.append(arg)
    if len(params) == 0:
        print("not input paths!!")
        exit()
    else:
        # 如果有设置静默模式参数
        if params[-1] == "yes":
            Cache.quietMode = 1
            params.pop()
        else:
            Cache.quietMode = 0
            print("quiet mode closed")

        # 处理多个文件路径参数
        checkBranchAndVersion(params)

doAction()