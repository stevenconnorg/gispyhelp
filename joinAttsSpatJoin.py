# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 12:59:28 2018

@author: stevenconnorg
"""
# for use in an ArcMap Toolbox	
	
# alternative tool to using join with field calculator to update records	
# updates a target feature class using a join with a source table	
# requires two join fields	
# and a target field and update field	
	
# params #	
# 1 Transfer from : source table	
# 2 Using Join Field : source join field	
# 3 Source Field: source field	
# 4 Destination Feature: target feature layer to update	
# 5 Destination Join Field: target feature layer join field	
# 6 Destination Field: target field to update	
# 7 Where Clause: how to filter source table features? (default: IS NOT NULL)	
# 8 Remove Leading Zeros: remove leading zeros from target ID field?	
# 9 source join key field 2
# 10 update join key field 2

import arcpy, os
from arcpy import env
env.overwriteOutput = True


# source feature
siteA = arcpy.GetParameterAsText(0)
# source RPSUID field
sourceRPSUID = arcpy.GetParameterAsText(1)

# target feature
targetFeat = arcpy.GetParameterAsText(2)

# target feature RPSUID field
targetRPSUID = arcpy.GetParameterAsText(3)
targetFieldWildcard = arcpy.GetParameterAsText(4)


fields = [sourceRPSUID]

def unique_values(table , field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({str(row[0]) for row in cursor})

RPSUID = unique_values(siteA,sourceRPSUID)

arcpy.Dissolve_management (siteA, siteA, sourceRPSUID,multi_part="SINGLE_PART")


for fds in arcpy.ListDatasets():
	for fc in arcpy.ListFeatureClasses(fds)
		for fld in arcpy.ListFields(fc,targetFieldWildcard)

RPSUIDs = unique_values(siteA,sourceRPSUID)

searchFields = ['SHAPE@',sourceRPSUID]
for RPSUID in RPSUIDs:
	with arcpy.da.SearchCursor(siteA, searchFields) as cursor:
		for row in cursor:
			arcpy.SelectLayerByLocation_management (siteA,"NEW_SELECTION", sourceRPSUID+"="+RPSUID)
			print row
			arcpy.SelectLayerByLocation_management (targetFeat,overlap_type="HAVE_THEIR_CENTER_IN", select_features=row)
			with arcpy.da.UpdateCursor(targetFeat, targetRPSUID) as cursor2:
				for row2 in cursor2:
					row2[0] = row[1]
					cursor2.updateRow(row2)
					print row2[0]
					print row[1]
					del row2
			del row
          
          
cursor = arcpy.SearchCursor(fc)
row = cursor.next()
while row:
    print(row.getValue(field))
    row = cursor.next()


for fc in arcpy.ListFeatureClasses():
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            Latitude = row[0]
            Longitude = row[1]
            Name = row[2]
            Address = row[3]
            City = row[4]
            State = row[5]
            PopulateGPX()
            
            
