################################################
# Author       : Steven C. Gonzalez
# Title        : GIS Technician, Graduate Student
# Organization : Bexar Appraisal District
# Date         : August 22, 2017
# Contact      : stevenconnorg@gmail.com
################################################

# Description: 


###########################################
################## TO-DO ##################
# 1 - Ensure script hub server (BCAD 55) 
# (where this script will be located) has
# ArcGIS 10.5 installed (with installed 
# Python 2.7 and arcpy module). 
# 2 - Establish Database Connection in 
# ArcCatalog with the maint10 database in
# BCAD56 server.

###########################################




################################################
# IMPORT LIBRARIES (USE PIP INSTALL IF NOT INSTALLED ALREADY)
################################################
import arcpy
import os
import shutil
import zipfile
from arcpy import env



################################################
# CREATE OUTPUT DIRECTORY IN ROOT AS "PARCEL_[DATE]"
################################################
## define directories
# root directory
# root = "\\\\bcad60\\users\\Parcel" 			# output location on bcad60
root = "C:\\Users\\sgonzalez\\Desktop"

# workspace parameters
date = time.strftime("%Y_%m_%d")
md = time.strftime("_%m_%d")

newpath = os.path.join(root, 'Parcel_'+date)	# define output directory path as root + Parcel_[year]_[month]_[day]
outDir = newpath

if not os.path.exists(outDir):
    os.makedirs(outDir)
	
	

################################################
# DEFINE INPUT PARAMETERS
################################################
# input parameters of parcel fabric location in sde database
# follows: Database Connections/Connection to [server name]/[feature dataset name]/[feature name]
# input features will be a string to the parcel fabric layer, currently in : 
# 'Database Connections/Connection to BCAD56.sde/maint10.GDO.ParcelEditing/maint10.GDO.ParcelFabric_Parcels'

# database connection
bcad56="Database Connections/Connection to BCAD56.sde"

# name of feature dataset in which input feature is located (or empty string)
parcel_editing_dataset="maint10.GDO.ParcelEditing"

# name of input feature class
parcel_fabric_feature="maint10.GDO.ParcelFabric_Parcels"

# input features as string of database connection, feature dataset, and features class names
parcelGeom=bcad56+"/"+parcel_editing_dataset+"/"+parcel_fabric_feature

# assign feature class as input features
inFeatures = parcelGeom

# define output shapefile name
layerName = "Parcels"

# assign parcel geometry join field
inField = "AccountID"

# set SQL join table location/name in bcad56

# joinTable = bcad56+"/MAINT10.GDO.VW015_GET_GIS_COSA_WEEKLY_UPDATE_DATA"
jtableName="maint10.dbo.GIS_publicdata"
joinTable = bcad56+"/"+jtableName

## set SQL table join field
# joinField = "prop_id"
joinField = "PropID" # SQL table join field for pid

# SQL snippet to filter input feature class (or empty string)
SQL = "SystemEndDate IS NULL" # SQL statement to filter parcels

# type of SQL join to perform (full or inside)
join_type = "KEEP_ALL" # (FULL) OR "KEEP_COMMON" (INSIDE)

# set email parameters
sender = "sgonzalez@bcad.org" # Email sender addrses
receiver = "sgonzalez@bcad.org" # Email receiver address
smtp = "BCAD27.bcad.local" # Simple Mail Transer Protocol Server

 ###  ###  ###  ###  ###  ###  ###  ###  ###  ### 
####           RUN AFTER THIS LINE            ####
 ###  ###  ###  ###  ###  ###  ###  ###  ###  ###



################################################
# ARCPY LAYER TO SHAPEFILE CONVERSION
################################################


# if using arcpy (join table must be registered in geodatabase)

# Set environment settings

env.workspace = outDir # set env.workspace inside directory
env.qualifiedFieldNames = False # set as false so it doesn't append the table name to the field names (and keeps native field name)

envTime=time.strftime ('%I:%M_%S %p')
envMessage=(" : Environment Settings established in '"+env.workspace+"'")

# Make a feature layer from the input feature class from sde connection
layTime=time.strftime ('%I:%M_%S %p')
layMessage=(" : Creating Layer of Features in '"+inFeatures+"' where '"+SQL+"'")
arcpy.MakeFeatureLayer_management (inFeatures,  layerName,where_clause=SQL)


# Joine the feature layer to the SQL table using join fields, table, and join_type established above
joinTime=time.strftime ('%I:%M_%S %p')
joinMessage=(" : Joining attributes from '"+joinTable+"' to '"+inFeatures+"' with join_type :'"+join_type+"'")
arcpy.AddJoin_management(layerName, inField, joinTable, joinField, join_type="KEEP_ALL")

# Copy the layer to a  permanent shapefile
shpTime=time.strftime ('%I:%M_%S %p')
shpMessage=(" : Writing output shapefile '"+layerName+"' to '"+outDir+"'")
arcpy.FeatureClassToShapefile_conversion(Input_Features=layerName, Output_Folder = outDir)

# Write out results to logfile
file = open (outDir+"/Parcel"+date+"log.txt", "w")
file.write (printDate+' '+startTime+' : Starting Application Parcel Update \n')
file.write (envTime + envMessage)
file.write (layTime + layMessage)
file.write (joinTime + joinMessage)
file.write (shpTime + shpMessage)
file.write (zipTime + zipMessage)
file.write (delTime + delMessage)
file.write (stopTime+ ' : '+layerName+' successfully joined with '+jtableName+' and exported to '+outDir+'.zip')
file.close()


# create a zip directory of output shapefile and friends

zipTime=time.strftime ('%I:%M_%S %p')
zipMessage=(" : Creating Zip directory of '"+outDir+"'")
zf=zipfile.ZipFile(outDir+".zip",mode='w')
zipf.close()



# send email if output parcel update exists
import smtplib
from email.mime.text import MIMEText

fp = open(outDir+"/Parcel"+date+"log.txt", 'w')
msg = MIMEText (fp.read())
fp.close()

msg ['Subject'] = 'COSA Parcel Update Log'
msg ['From'] = sender
msg ['To'] = receiver

s = smtplib.SMTP(smtp)
s.sendmail(me, you, msg.as_string())
s.quit()


# remove output directory (retaining only the zipfile)
delTime=time.strftime ('%I:%M_%S %p')
delMessage=(" : Removing '"+outDir+"'")

shutil.rmtree(outDir)

stopTime=time.strftime ('%I:%M_%S %p')

