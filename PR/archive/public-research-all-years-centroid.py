###############################
### author: steven c gonzalez
### date: 
### title: Public Research Map Book by Year
### description: 
###############################

# import modules
import arcpy, time, os, sys
from datetime import date
from arcpy import env

# define input pararmeters
today = date.today()
printDate = today.strftime('%m-%d-%Y')
startTime = time.strftime('%I:%M:%S-%p')

# define output locations
# wd = os.path.dirname(os.path.realpath(__file__)) #### script location directory to write log files to
wd= r"C:\Users\sgonzalez\Desktop\PR"
# env.workspace=wd
mxdName = "Public_Research_Dataframes_by_Year" 
mapdoc = arcpy.mapping.MapDocument(wd+"/mxd/"+mxdName+".mxd")
# mapdoc = arcpy.mapping.MapDocument("CURRENT")

whereClause="AccountID = 1197599"# select title as PID numbers input in whereClause
# whereClause='"AccountID" = ' + "'1197599'"# select title as PID numbers input in whereClause
# whereClause= "\"AccountID\" = \'1197599\'"
title="testing document" 			 # set title string of Account ID(s) selected

outpath=wd+"/output/"+printDate+"/"+title
if not os.path.exists(outpath):
    os.makedirs(outpath)		# create an empty directory to store outputs
mapdoccopy=outpath+"/"+title+".mxd"
mapdoc.saveACopy(mapdoccopy)
mapdoc = arcpy.mapping.MapDocument(mapdoccopy)
mapdoc.title = title

listdf=arcpy.mapping.ListDataFrames(mapdoc) # list dataframes in mxd

# dataframe go backwards in years from top to bottom
# access most recent parcel and make layer
cparcel=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",listdf[0])
# should only be one layer with "parcel" in name per dataframe
# get parcel layer
cpar=cparcel[0]
# make layer from SQL statement
arcpy.MakeFeatureLayer_management (cpar, "selpar", where_clause=whereClause, workspace="#", field_info="#")
# arcpy.SelectLayerByAttribute_management("selpar","NEW_SELECTION",whereClause)

# remove output centroid if already exists
import os, errno

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

silentremove(outpath+"/centroid.shp")
silentremove(outpath+"/centroid.shp.xml")

centroid = arcpy.FeatureToPoint_management("selpar", outpath+"/centroid.shp", point_location = "INSIDE")


for df in listdf:
    dfpar=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",df)
    dfpar=dfpar[0]
    dfpar.showLabels = True
    arcpy.RefreshActiveView()
    arcpy.SelectLayerByLocation_management(dfpar,"intersect",centroid)
    df.zoomToSelectedFeatures()
    df_pdf = outpath+'/'+df.name+".pdf"
    arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
    arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf,data_frame=df) # export individual pdfs for each dataframe
    mapdoc.save()
    del mapdoc

import glob
mapbookpath=os.path.join(outpath+'/'+mapdoc.title+".pdf")
if not os.path.exists(mapbookpath):
    mapbook = arcpy.mapping.PDFDocumentCreate(mapbookpath) 	# create empty pdf to append individual pdfs to
pdfList = glob.glob('*.pdf')	# list pdfs in directory 
for pdf in pdfList:
    pdfpath=os.path.join(outpath+"/"+pdf)# append individual pdfs to final pdf
    mapbook.appendPages(pdf)
    mapbook.saveAndClose() # save and close final pdf
    silentremove(pdfpath)

        										# remove lock on mxd
