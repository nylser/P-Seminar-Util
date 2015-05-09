#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import common
from dbf import ver_33 as dbf
from common import ATT, ATT_HR
import os


def split_files(path=None):
    if not path:
        box = common.AskFileBox(type='open', title='Select File to split', default='*.dbf', filetypes=[['*.dbf', 'DBF Files']])
        path = box.ask()
    for i in range(1, len(ATT)-1):
        file = os.path.join(os.path.dirname(path), ATT_HR[ATT[i]].replace("/", "_").
                                                                replace(" ", "_")+".dbf")
        shutil.copyfile(path, file)
        shutil.copyfile(''.join(path.split('.')[0])+".shp", ''.join(file.split('.')[0])+".shp")
        shutil.copyfile(''.join(path.split('.')[0])+".shx", ''.join(file.split('.')[0])+".shx")
        t = dbf.Table(file)
        t.open()
        fields = list(ATT.keys())[0:i]
        fields += list(ATT.keys())[i+1:len(ATT)]
        fields = [ATT[i] for i in fields]
        t.delete_fields(fields)
        t.close()

def add_fields(path=None):
    if not path:
        box = common.AskFileBox(type='open', title='Select File to split', default='*.dbf', filetypes=[['*.dbf', 'DBF Files']])
        path = box.ask()
    db = dbf.Table(path)
    db.open()
    for field in common.ATT_STUFF:
        print(field)
        db.add_fields(field)
    db.close()



if __name__ == "__main__":
    add_fields()
#    split_files()


