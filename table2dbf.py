#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import gdata
from gdata.spreadsheet import service
import gdata.auth
from pprint import pprint
from dbf import ver_33 as dbf
import easygui as g
import common
from common import ATT, ATT_INV, ATT_HR, ATT_CONV
from split_dbf import split_files
import sys
import os
import traceback

def load_from_google(email, password):
    street_db = {}
    gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    gd_client.email = email
    gd_client.password = password
    gd_client.source = 'TABLE-TO-DBF'
    gd_client.ProgrammaticLogin()
    feed = gd_client.GetCellsFeed(key="1HAf7uZKGwMd5dvQOb7kmrTmySNT5r8aJMI_kS11ZsL0")
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
    pprint(street_db)
    return street_db


def ask_login(values=('', '')):
    fieldNames = ["Google-Email", "Password"]
    title = "Google-Login"
    values = g.multpasswordbox("Login", title, fieldNames, values)
    while True:
        if values is None:
            break
        errmsg = ""
        for i in range(len(fieldNames)):

            if values[i].strip() == "":
                errmsg += '"%s" is a required field.\n\n' % fieldNames[i]
        if errmsg == "":
            break
        else:
            values = g.multpasswordbox(errmsg, title, fieldNames, values)
    return values


def ask_dbf(last_dir='.'):
    title = "Select DBF File"
    result = None
    while not result:
        result = g.fileopenbox(title=title, default=last_dir + "/*.dbf")
        if not result:
            if not g.ynbox(title="No file selected!", msg="Do you want to try again?"):
                sys.exit(0)

    return result


def load_street_db(csv_file):
    street_db = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            details = {}
            for i in range(len(ATT)):
                if i < 1:
                    details[ATT[i]] = row[i].replace(str('\ufeff'), "")
                else:
                    details[ATT[i]] = row[i]
            street_db[row[0].replace(str('\ufeff'), "")] = details
    return street_db


def update_table(table, street_db):
    updates = {}
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


if __name__ == "__main__":
    common.load_config()
    config = common.get_config()
    if "auth" in config:
        if "last_email" in config["auth"] and "last_password" in config["auth"]:
            values = [config["auth"]["last_email"], config["auth"]["last_password"]]
            user_data = ask_login(values)
        else:
            user_data = ask_login()
    else:
        user_data = ask_login()
    print("Loading from google-document")
    try:
        street_db = load_from_google(user_data[0], user_data[1])
    except Exception as e:
        traceback.print_exc()
        load_json = not g.ynbox(msg="Couldn't authenticate with google!",
                                choices=("[<F1>]OK, restart and try again", "[<F2>]Load streetdb from json"),
                                image=None,
                                default_choice='[<F1>]OK, restart and try again',
                                cancel_choice='[<F2>]Load streetdb from json')
        if load_json:
            try:
                street_db = common.load_json()
            except:
                g.msgbox(msg="Unable to load from JSON, exit!")
                sys.exit(1)
        else:
            sys.exit(1)
    else:
        if "auth" not in config:
            config["auth"] = {}
        config["auth"]["last_email"] = user_data[0]
        config["auth"]["last_password"] = user_data[1]
        common.save_config()
    if "DEFAULT" not in config:
        config["DEFAULT"] = {}
    box = common.AskFileBox(type='open', default=config["DEFAULT"].get("last_dbf_directory", ".") + "/*.dbf",
                            title="Open DBF File", filetypes=[["*.dbf", "DBF File"]])
    dbf_file = box.ask()
    config["DEFAULT"]["last_dbf_directory"] = os.path.dirname(dbf_file)
    common.save_config()
    print("Opening DBF (%s)..." % dbf_file)
    try:
        table = dbf.Table(dbf_file)
    except dbf.DbfError as e:
        g.msgbox(msg="Invalid DBF File!")
        sys.exit(1)

    table.open()
    updates_done = update_table(table, street_db)
    table.close()
    split_files(dbf_file)
    if updates_done:
        g.textbox(msg="Done! Updated the following streets: ", title="Success", text=build_update_string(updates_done),
                  modify=False)
    dump_to_json = not g.ynbox(msg="All streets are up to date! \n(Table2DBF (c) 2015 Korbinian Stein)",
                               choices=("[<F1>]OK", "[<F2>]Dump streetdb to json"),
                               image=None,
                               default_choice='[<F1>]OK', cancel_choice='[<F2>]Dump streetdb to json')
    if dump_to_json:
        common.dump_json(street_db)
