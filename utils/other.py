import csv

def wrapQuotes(x): return f'"{x}"'
def csvToList(x): return x.split(",")

def listToCsv(x):
    y = ""
    for item in x: y += f'"{item}",'
    return y[:-1]

def removeAll(list,*terms):
    return [x for x in list if x not in terms]
