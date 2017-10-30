###############################
### author: steven c gonzalez
### date: 10/11/2017
### title: calculate areage and sq footage for taxable parcels and write table to gdb
### description: 
### script location:
###############################


# Import arcpy module
import arcpy
import time
import os
from datetime import date
from arcpy import env
import sys

# env.workspace="Database Connections\\Connection to BCAD56.sde"

# Date and Time
today = date.today()
printDate = today.strftime('%mm_%dd_%Y')
startTime = time.strftime('%I:%M:%S-%p')

# Defin Local VariablesLocal variables:
dir_path = r"H:\\sgonzalez\\My Documents\\AppParcelUpdate\\steven\\" #### change this to script location, to write log files 
maint10 = "Database Connections\\Connection to BCAD56.sde"   #### output database path or Connection String e.g.: "Database Connections\\Connection to BCAD56.sde"
parcelPub = maint10+"\\maint10.GDO.ParcelPublishing\\"       #### output feature class, or empty string ""
Parcels = maint10+"\\maint10.GDO.ParcelEditing\\maint10.GDO.ParcelFabric_Parcels" #### path to input parcel features
sqlStatement = "SystemEndDate IS NULL AND AccountID <> 0 AND AccountID IS NOT NULL AND AccountID <> '' AND AccountID > 0 AND Shape.area > 0" #### sql statement to filter out non-taxable parcels
sqft_field = "Sq_ft"  #### output table square foot field name
ac_field = "Acres"    #### output table acreage field name
# testing outtable to local drive, change out path for realbelow
##################################################
outPath = "H:\\sgonzalez\\My Documents\\ArcGIS\\Default.gdb\\" # testing outPath
# outPath = parcelPub # real outPath inside ParcelPublishing feature class in database
##################################################
outName = "Parcel_Area"+"_"+printDate #### outout table name as Parcel_Area_[date]
stageName= "stageParcel"              #### stage parcel name
outTable= outPath+outName
outStage= outPath+stageName

me = "sgonzalez@bcad.org" # email sender
you = "sgonzalez@bcad.org" # email receiver

###### ###### ###### ###### ###### ###### 
#### RUN AFTER DEFINING INPUTS ABOVE #### 
###### ###### ###### ###### ###### ######

# Process: Delete final table if  exists
dfp_time=time.strftime ('%I:%M_%S %p')
dfp_message=(" Deleting features previous Parcel Area table and staging table \n")

arcpy.Delete_management(outTable)

# Process: Delete delete stageParcel(i.e.: outpath + stageName)
arcpy.Delete_management(outStage)
    
# Process: Make Table View of Selected Parcels
sp_time=time.strftime ('%I:%M_%S %p')
sp_message=(" Selecting features from maint10 ParcelFabric Parcels \n")
stageParcel = arcpy.TableToTable_conversion(Parcels, outPath, stageName, where_clause = sqlStatement)

# Check field names 
# field_names = [f.name for f in arcpy.ListFields(stageParcel)]

# Process: Add square footage field
arcpy.AddField_management(stageParcel, sqft_field, "FLOAT")

# Process: Add Acres field
arcpy.AddField_management(stageParcel, ac_field, "FLOAT")

# Process: Calculate square footage field
arcpy.CalculateField_management(stageParcel, ac_field, expression = "round(!Shape_area! / 43560,4)", expression_type ="PYTHON")

# Process: Calculate Acres field
cf_sqft=time.strftime ('%I:%M_%S %p')
cf_message=(" Calculating Shape Area into Sq_Ft Field \n")
arcpy.CalculateField_management(stageParcel, sqft_field, expression ="round(!Shape_area!,4)", expression_type = "PYTHON")

# check field names
# field_names = [f.name for f in arcpy.ListFields(stageParcel)]

# Process: Delete unwanted fields.. if you can use a key to identify the fields to remove, then it's solved
# define fields 
fields = arcpy.ListFields(stageParcel) 

# manually enter field names to keep here, include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["OBJECTID","OID","AccountID","Name",ac_field,sqft_field]

# field names not in keepFields are dropped
dropFields = [x.name for x in fields if x.name not in keepFields]

# OR manually specify
# dropFields = ["XXXXXXX", "XXXXXXX", "XXXXXXX"]

# delete fields
df_time=time.strftime ('%I:%M_%S %p')
df_message=(" Calculating Shape Area into Sq_Ft Field \n")
outParcels = arcpy.DeleteField_management(stageParcel, dropFields)

# delete stageParcel
arcpy.DeleteField_management(stageParcel, dropFields)

# check that it dropped unwanted fields
# field_names = [f.name for f in arcpy.ListFields(outParcels)]

arcpy.TableToTable_conversion(outParcels, outPath, outName)

# delete stage parcel from output directory
arcpy.Delete_management(stageParcel)

    
# Write out results to logfile
file = open (dir_path+"AppParcelUpdate_"+printDate+".txt", "w")
file.write (printDate+' '+startTime+' Starting Application Parcel Update \n')
file.write (dfp_time + dfp_message)
file.write (sp_time + sp_message)
file.write (ap_time + ap_message)
file.write (dp_time + dp_message)
file.write (cf_sqft + cf_message)
file.write (cf_acres + cf_message1)
file.write (df_time + df_message)
file.write (stopTime+ ' Application Parcel Update Completed!')
file.close()

# email log file stuff
import smtplib

from email.mime.text import MIMEText

fp = open(dir_path+"AppParcelUpdate_"+printDate+".txt", 'rb')
msg = MIMEText (fp.read())
fp.close()


msg ['Subject'] = 'AppParcelUpdate Log'
msg ['From'] = me
msg ['To'] = you

s = smtplib.SMTP('BCAD27.bcad.local')
s.sendmail(me, you, msg.as_string())
s.quit()


