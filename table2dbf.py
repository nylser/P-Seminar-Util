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
import sys

attributes_inv = {'name': 0,
              'lautstaerk': 1,
              'geruch': 2,
              'verschmutz': 3,
              'beleuchtun': 4,
              'qualitaet': 5,
              'haue_gaert': 6,
              'gruenflaec': 7,
              'dschnitt': 8}

attributes = {v: k for k, v in attributes_inv.items()}


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
    current_street = ""
    for i, entry in enumerate(feed.entry):
        if entry.content.text == "Straße":
            in_data = True
            start_row = int(entry.cell.row)+1
        elif entry.content.text == "0" and in_data:
            in_data = False
        elif in_data and int(entry.cell.row) >= start_row:
            if int(entry.cell.col) == 1:
                print("1st Column, street is %s " % entry.content.text)
                current_street = entry.content.text
                street_db[current_street] = {}

            street_db[current_street][attributes[int(entry.cell.col)-1]] = entry.content.text
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
    title = "Select DBF File to update"
    result = None
    while not result:
        result = g.fileopenbox(title=title, default=last_dir+"/*.dbf")
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
            for i in range(len(attributes)):
                if i < 1:
                    details[attributes[i]] = row[i].replace(str('\ufeff'), "")
                else:
                    details[attributes[i]] = row[i]
            street_db[row[0].replace(str('\ufeff'), "")] = details
    return street_db


def update_table(table, street_db):
    updates = {}
    for record in table:
        name = record.name.strip()
        if name in street_db:
            with record:
                updates[name] = []
                print("Updating %s... " % name)
                for attribute in attributes_inv:
                    current_rec = str(record[attribute]).strip()
                    update_rec = street_db[name][attribute]
                    if current_rec != update_rec:
                        updates[name].append("%s:\t%s -> %s" %
                                             (attribute, current_rec, update_rec))
                        record[attribute] = update_rec
                if len(updates[name]) < 1:
                    updates.pop(name)
    return updates


def build_update_string(updates):
    update_string = ""
    for update in updates_done:
        changes = updates_done[update]
        update_string += update+":\n"
        for change in changes:
            update_string += "\t%s\n" % change
    return update_string

if __name__ == "__main__":
    #print("Loading %s..." % csv_file)
    #street_db = load_street_db(csv_file)
    config = common.load_config()
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
    except:
        g.msgbox("Couldn't authenticate with google!", ok_button="Restart and try again.")
        sys.exit(1)
    else:
        if "auth" not in config:
            config["auth"] = {}
        config["auth"]["last_email"] = user_data[0]
        config["auth"]["last_password"] = user_data[1]
        common.save_config(config)
    if "DEFAULT" not in config:
        config["DEFAULT"] = {}
    dbf_file = ask_dbf(config["DEFAULT"].get("last_dbf_directory", "."))

    print("Opening DBF (%s)..." % dbf_file)
    table = dbf.Table(dbf_file)
    table.open()
    updates_done = update_table(table, street_db)
    table.close()
    common.save_config(config)
    if updates_done:
        g.textbox(msg="Done! Updated the following streets: ", title="Success", text=build_update_string(updates_done))
    else:
        g.msgbox(msg="Done! All streets are up to date!")