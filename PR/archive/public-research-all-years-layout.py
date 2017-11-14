###############################
### author: steven c gonzalez
### date: 
### title: Public Research Map Book by Year
### description: 
###############################

# import modules
import arcpy, time, os, sys, glob
from datetime import date
from arcpy import env
import os, errno

def silentremove(filename):
	try:
		os.remove(filename)
	except OSError as e: # this would be "except OSError, e:" before Python 2.6
		if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
			raise # re-raise exception if a different error occurred
			
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
silentremove(mapdoccopy)
mapdoc.saveACopy(mapdoccopy)
mapdoc = arcpy.mapping.MapDocument(mapdoccopy)
mapdoc.title=title


		
listdf=arcpy.mapping.ListDataFrames(mapdoc) # list dataframes in mxd

# dataframe go backwards in years from top to bottom
# access most recent parcel and make layer
cparcel=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",listdf[0])
# should only be one layer with "parcel" in name per dataframe
# get parcel layer
cpar=cparcel[0]
# make layer from SQL statement
arcpy.MakeFeatureLayer_management (cpar, "selpar", where_clause=whereClause, workspace="#", field_info="#")
# remove output centroid if already exists

# remove centroid if already exists
for filename in glob.glob(outpath+"/centroid*"):
    silentremove(filename)
    

centroid = arcpy.FeatureToPoint_management("selpar", outpath+"/centroid.shp", point_location = "INSIDE")



# for dfelement in arcpy.mapping.ListLayoutElements(mapdoc,'DATAFRAME_ELEMENT',df.name)
for df in listdf:
    # access parcel for each df to join with centroid
    mapdoc.activeview='PAGE_LAYOUT'
    arcpy.RefreshActiveView()
    parcel=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",df)
    par=parcel[0]
    arcpy.SelectLayerByLocation_management(par,"intersect",centroid)
    df_pdf = outpath+'/'+df.name+".pdf"
    silentremove(df_pdf)
    par.showLabels = True
    df.zoomToSelectedFeatures()
    arcpy.RefreshActiveView()
    arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
    arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf)# ,data_frame=df) # export individual pdfs for each dataframe
    mapdoc.save()

# mapdoc = arcpy.mapping.MapDocument(mapdoccopy)

mapbookpath=os.path.join(outpath+'/'+mapdoc.title+".pdf")
silentremove(mapbookpath)
mapbook = arcpy.mapping.PDFDocumentCreate(mapbookpath) # create empty pdf to append individual pdfs to

pdfList = glob.glob('*.pdf')	# list pdfs in directory 
for pdf in pdfList:
    pdfpath=os.path.join(outpath+"/"+pdf)# append individual pdfs to final pdf
    mapbook.appendPages(pdfpath) # save and close final pdf

for pdf in pdfList:
    silentremove(pdf)
    
mapbook.saveAndClose()
del mapbook

for filename in glob.glob(outpath+"/centroid*"):
    silentremove(filename)

del mapdoc										# remove lock on mxd
