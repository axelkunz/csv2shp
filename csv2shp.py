# -*- coding: utf-8 -*-
import csv
from collections import Counter
import arcpy

file_path = r"C:\Users\axel.kunz\Desktop\daten\overall.txt"
shape_path = r"C:\Users\axel.kunz\Desktop\daten\plz_brd-XX.shp"
output_path = ""
output_txt = r"C:\Users\axel.kunz\Desktop\daten\legend.txt"
shp_plz_field = "leitregion"

## TODO: save as new shape

# id, geschlecht, alter, hochschule, hochschultyp, abschluss, heimat-plz, momentanter-wohnsitz
def get_count_all(file_path, index):
    """ return list of plz, shorten them o the first
        two digits
    """
    result_list = []
    with open(file_path, "rb") as f:
        for items in csv.reader(f, delimiter="\t"):

            result_list.append(items[index][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def get_count_female(file_path, index):
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
                result_list.append(items[index][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def get_count_male(file_path, index):
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
                result_list.append(items[index][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def get_count_insti(file_path, index, insti_name):
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
                result_list.append(items[index][0:2])   # append only first two digits of plz

    return Counter(result_list)  # count items


def update_shape(data, shape_path, new_field_name):
    plz_field_name = shp_plz_field
    cursor = arcpy.UpdateCursor(shape_path)   # TODO: specify fields
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


# all
count = get_count_all(file_path, 6)
update_shape(count, shape_path, "count")

# female
count_female = get_count_female(file_path, 6)
#arcpy.AddField_management(shape_path, "count_f", "LONG", 9)
update_shape(count_female, shape_path, "count_f")

# male
count_male = get_count_male(file_path, 6)
#arcpy.AddField_management(shape_path, "count_m", "LONG", 9)
update_shape(count_male, shape_path, "count_m")

# institutions
csv_file = open(output_txt, "wb")
csv_writer = csv.writer(csv_file, delimiter=",")

insti_count_list = []

for i, insti in enumerate(get_unique_institutes()):
    count_insti = get_count_insti(file_path, 6, insti)
    try:
        arcpy.AddField_management(in_table=shape_path,
                                  field_name="insti_{}".format(i),
                                  field_type="LONG",
                                  field_precision=9,
                                  field_alias=insti)  # only works for gdbs
    except:
        print "failed to add field"
        print(arcpy.GetMessages())

    update_shape(count_insti, shape_path, "insti_{}".format(i))
    csv_writer.writerow([i, "insti_{}".format(i), insti])

csv_file.close()

for field in arcpy.ListFields(shape_path):
    print field.aliasName

print "done!"
