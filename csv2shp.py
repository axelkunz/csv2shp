#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" csv2shp.py: appends plz counts to shapefile """

__author__ = "Axel Kunz"
__email__ = "axel.kunz@hs-mainz.com"
__status__ = "Development"


import os
import csv
from collections import Counter
import arcpy


# will get overwritten when used as arcgis tool
file_path = r"C:\Users\axel.kunz\Desktop\daten\overall.txt"
shape_path = r"C:\Users\axel.kunz\Desktop\daten\plz_brd-XX.shp"
shp_plz_field = "leitregion"
output_path = r"C:\Users\axel.kunz\Desktop\daten2\output.shp"


class ShapefileExistsException(Exception):
    pass


class CouldNotCopyShapeException(Exception):
    pass


def get_count_all(file_path):
    """ return list of plz, shorten them o the first
        two digits
    """
    result_list = []
    with open(file_path, "rb") as f:
        for items in csv.reader(f, delimiter="\t"):

            result_list.append(items[6][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def get_count_female(file_path):
    """ return list of plz, shorten them o the first
        two digits
    """
    result_list = []
    with open(file_path, "rb") as f:
        for items in csv.reader(f, delimiter="\t"):

            # gender specific
            gender = items[1]
            if gender != "weiblich": gender = "maennlich"

            if gender == "weiblich":
                result_list.append(items[6][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def get_count_male(file_path):
    """ return list of plz, shorten them o the first
        two digits
    """
    result_list = []
    with open(file_path, "rb") as f:
        for items in csv.reader(f, delimiter="\t"):

            # gender specific
            gender = items[1]
            if gender != "weiblich": gender = "maennlich"

            if gender == "maennlich":
                result_list.append(items[6][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def get_count_insti(file_path, insti_name):
    """ return list of plz, shorten them o the first
        two digits
    """
    result_list = []
    with open(file_path, "rb") as f:
        for items in csv.reader(f, delimiter="\t"):

            # gender specific
            insti = items[3]
            #print insti.encode("utf-8")
            if insti == insti_name:
                result_list.append(items[6][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def update_shape(data, output_path, new_field_name):
    plz_field_name = shp_plz_field
    cursor = arcpy.UpdateCursor(output_path)   # TODO: specify fields
    for row in cursor:  # loop shapefile
        shp_plz_value = row.getValue(plz_field_name)
        #print str(row.getValue(plz_field_name))
        add_value = 0
        if str(row.getValue(plz_field_name)) in data.keys():
            #print int(row.getValue("plz"))
            add_value = int(data[row.getValue(plz_field_name)])

        #print shp_plz_value, plz_list_count.shp_plz_value
        #print plz_int
        row.setValue(new_field_name, add_value)
        cursor.updateRow(row)

    del cursor


def get_unique_institutes():
    """ return list of males and females
    """
    result_list = []
    with open(file_path, "rb") as f:
        for items in csv.reader(f, delimiter="\t"):
            institute = items[3]
            if institute not in result_list:
                result_list.append(institute)
    return result_list


def clean_up():
    print("Cleaning up ...")
    try:
        arcpy.Delete_management(output_path)
        arcpy.Delete_management(output_txt)
    except:
        pass

if __name__ == "__main__":
    print("processing...")
    arcpy.AddMessage("processing...")
    # make script compatible as arcmap tool
    if arcpy.GetParameterAsText(0):  # input csv is set
        file_path = arcpy.GetParameterAsText(0)
    if arcpy.GetParameterAsText(1):  # input shape is set
        shape_path = arcpy.GetParameterAsText(1)
    if arcpy.GetParameterAsText(2):  # output shape is set
        print "arcGIS tool!"
        output_path = arcpy.GetParameterAsText(2)

    # get output path to save txt into it
    print "before output path"
    output_dir = os.path.dirname(output_path)
    print "after output path"
    output_txt = os.path.join(output_dir, "legend.txt")

    try:
        # copy shapefile to output location
        if arcpy.Exists(output_path):
            raise ShapefileExistsException("%s already exists!" % output_path)

        try:
            arcpy.CopyFeatures_management(shape_path, output_path)
        except:
            arcpy.AddError("failed to copy shapefile")
            raise CouldNotCopyShapeException("failed to copy shapefile")

        # get all
        count = get_count_all(file_path)
        try:
            arcpy.AddField_management(output_path, "count", "LONG", 9)
        except:
            print("couldnt create field")

        update_shape(count, output_path, "count")

        # female
        count_female = get_count_female(file_path)
        try:
            arcpy.AddField_management(output_path, "count_f", "LONG", 9)
        except:
            print("couldnt create field")
        update_shape(count_female, output_path, "count_f")

        # male
        count_male = get_count_male(file_path)
        try:
            arcpy.AddField_management(output_path, "count_m", "LONG", 9)
        except:
            print("couldnt create field")
        update_shape(count_male, output_path, "count_m")

        # institutions
        csv_file = open(output_txt, "wb")
        csv_writer = csv.writer(csv_file, delimiter=",")

        insti_count_list = []

        for i, insti in enumerate(get_unique_institutes()):
            count_insti = get_count_insti(file_path, insti)
            try:
                arcpy.AddField_management(in_table=output_path,
                                          field_name="insti_{}".format(i),
                                          field_type="LONG",
                                          field_precision=9,
                                          field_alias=insti)  # only works for gdbs
            except:
                print("couldnt create field")

            update_shape(count_insti, output_path, "insti_{}".format(i))
            csv_writer.writerow([i, "insti_{}".format(i), insti])

        csv_file.close()

        print("completed successfully!")
        arcpy.AddWarning("completed successfully!")
    except:
        print("something went wrong! cleaning up ...")
        arcpy.AddError("something went wrong! cleaning up ...")
        clean_up()

