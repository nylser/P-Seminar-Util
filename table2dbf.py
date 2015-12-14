#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv


"""import gdata
from gdata.spreadsheet import service
import gdata.auth"""
import traceback

from common import ATT, ATT_INV, ATT_HR, ATT_CONV


def load_from_google(email, password, docid="1HAf7uZKGwMd5dvQOb7kmrTmySNT5r8aJMI_kS11ZsL0"):
    street_db = {}
    gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    gd_client.email = email
    gd_client.password = password
    gd_client.source = 'TABLE-TO-DBF'
    gd_client.ProgrammaticLogin()
    feed = gd_client.GetCellsFeed(key=docid)
    in_data = False
    start_row = 0
    current_street = ()
    last_row = 0
    last_column = 0
    for entry in feed.entry:
        # Start check
        if entry.content.text == "Straße":
            in_data = True
            start_row = int(entry.cell.row) + 1

        # Stop check
        elif in_data:
            # Check if there is a bigger jump then 1 in the data, if there is, abandon
            if int(entry.cell.row) - last_row > 1 or int(entry.cell.col) == last_column:
                in_data = False

        if in_data and int(entry.cell.row) >= start_row:
            if int(entry.cell.col) == 1:
                print("1st Column, street is %s " % entry.content.text)
                current_street = (entry.content.text, int(entry.cell.row))
                street_db[current_street[0]] = {}
            # Check if right street
            if int(entry.cell.row) == current_street[1]:
                content = entry.content.text
                field_name = ATT[int(entry.cell.col) - 1]
                if field_name in ATT_CONV:
                    content = ATT_CONV[field_name](content)
                street_db[current_street[0]][field_name] = content

        # Update last row
        last_row = int(entry.cell.row)
        last_column = int(entry.cell.col)
    return street_db


def load_street_db(csv_file):
    street_db = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != 'Straße':
                print(row)
                details = {}
                for i in range(len(ATT)):
                    if i < 1:
                        details[ATT[i]] = row[i].replace(str('\ufeff'), "")
                    else:
                        if ',' in row[i]:
                            details[ATT[i]] = float(row[i].replace(',', '.'))
                        elif len(row[i]) > 0:
                            try: details[ATT[i]] = int(row[i])
                            except ValueError:
                                print(row[i], "is not a number! Continue")
                street_db[row[0].replace(str('\ufeff'), "")] = details
    return street_db


def update_table(table, street_db):
    updates = {}
    print(street_db)
    for record in table:
        name = record.name.strip()
        if name in street_db:
            with record:
                updates[name] = []
                print("Updating %s " % name, end="")
                for attribute in ATT_INV:
                    if attribute in street_db[name]:
                        current_rec = str(record[attribute]).strip()
                        update_rec = street_db[name][attribute]
                        if current_rec != update_rec:
                            print(".", end="")
                            updates[name].append("%s:%s -> %s" %
                                                 (attribute, current_rec, update_rec))

                            record[attribute] = update_rec

                if len(updates[name]) < 1:
                    updates.pop(name)
                    print(" done! No updates.")
                else:
                    print(" done! %d updated." % len(updates[name]))
                    updates[name].append("name:%s" % name)

    return updates


def build_update_string(updates):
    update_string = ""
    for update in updates:
        changes = updates[update]
        update_string += update + ":\n"
        changed_attributes = [ATT_HR[change.split(":")[0]] for change in changes]
        change_values = [change.split(":")[1] for change in changes]
        update_string += "\t\t".join(changed_attributes) + "\n"
        update_string += "\t\t".join(change_values) + "\n"
    return update_string