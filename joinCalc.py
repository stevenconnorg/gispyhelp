import arcpy, traceback, os, sys
from arcpy import env
env.overwriteOutput = True

#join table
joinFc =arcpy.GetParameterAsText(0)
#join key field
joinIdFld =arcpy.GetParameterAsText(1)
#join value field to be transferred
joinValFld=arcpy.GetParameterAsText(2)


#feature class to update
pointFc =arcpy.GetParameterAsText(3)
#update fc key field
IdFld =arcpy.GetParameterAsText(4)
#update field
updateFld =arcpy.GetParameterAsText(5)
whereClause=arcpy.GetParameterAsText(6)
checkedLeftstrip = arcpy.GetParameterAsText(7)


#join key field
sourceRPSUID =arcpy.GetParameterAsText(8)


#join key field
updateRPSUID =arcpy.GetParameterAsText(9)


RPSUID =arcpy.GetParameterAsText(10)

tbl = "in_memory\\tbl"
if arcpy.Exists(tbl):
	arcpy.Delete_management(tbl)
arcpy.TableSelect_analysis(joinFc,tbl,where_clause='"'+joinValFld+'"'+whereClause + " and '"+ sourceRPSUID+"' = '"+RPSUID+"'")

if arcpy.Exists(tbl):
	arcpy.AddMessage( "table exists")
else:
	arcpy.AddMessage( "table doesn't exist")

for fld in arcpy.ListFields(tbl):
	arcpy.AddMessage(fld.name)
arcpy.AddMessage( len(arcpy.ListFields(tbl)))

if checkedLeftstrip:
	with arcpy.da.UpdateCursor(pointFc,[IdFld]) as cursor:
		for row in cursor:
			row=[i.lstrip('0') for i in row]
			cursor.updateRow(row)
			
#create dictionary
#Key: join field
#Value: field with value to be transferred
valueDi = dict ([(key, val) for key, val in
                 arcpy.da.SearchCursor
                 (joinFc, [joinIdFld, joinValFld])])

#update feature class
with arcpy.da.UpdateCursor (pointFc, [updateFld, IdFld]) as cursor:
    for update, key in cursor:
        #skip if key value is not in dictionary
        if not key in valueDi:
            continue
        #create row tuple
        row = (valueDi [key], key)

        #update row
        cursor.updateRow (row)

del cursor
