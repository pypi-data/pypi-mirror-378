import csv
import os

# csv
def Get_csv2List(path):
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [data for data in reader]
    return data

# text
def Get_text2list(path,delimiter):
    with open(path, 'r') as f:
        return f.read().split(delimiter)

# directory
def Get_dirList(path):
    return sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])

# file
def Get_fileList(path):
    return sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (not f.startswith("."))])

def Get_filepathList(path):
    return sorted([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (not f.startswith("."))])

def Get_uniqueList(targetList):
    return sorted(filter(lambda a: a != '',list(set(targetList))))

def Get_keysFromValue(d, val):
    return [k for k, v in d.items() if v == val]
