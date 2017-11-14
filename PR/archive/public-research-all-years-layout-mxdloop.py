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
from os.path import basename

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
wd = os.path.dirname(os.path.realpath(__file__)) #### script location directory to write log files to
# wd= r"C:\Users\sgonzalez\Desktop\PR"

accountIDS = ("1260353" , "1197599")
whereClause="AccountID = 1260353"# select title as PID numbers input in whereClause

s = " OR AccountID = "
seq = accountIDS # This is sequence of strings.
whereClause =  "AccountID = "+s.join( seq )

# whereClause='"AccountID" = ' + "'1197599'"# select title as PID numbers input in whereClause
# whereClause= "\"AccountID\" = \'1197599\'"
title="1260353" 			 # set title string of Account ID(s) selected

outpath=wd+"/output/"+printDate+"/"+title

if not os.path.exists(outpath):
    os.makedirs(outpath)		# create an empty directory to store outputs

mxdout = glob.glob(outpath+'/*.mxd')
for mxd in mxdout:
    silentremove(mxd)

mxdList = glob.glob(wd+'/mxd/*.mxd')

##  get centroid of most recent selected parcel(s) ##


# remove centroid if already exists
for centroidfile in glob.glob(outpath+"/centroid*"):
    silentremove(centroidfile)

# access most recent mxd (last because they are in alphabetical order)
mxdrecent = arcpy.mapping.MapDocument(mxdList[-1])

# get dataframe in mxd
# dataframe go backwards in years from top to bottom
# access most recent parcel and make layer
# should only be one layer with "parcel" in name per dataframe
# get parcel layer
dfrecent = arcpy.mapping.ListDataFrames(mxdrecent)[0]

# get parcel layer in df
cpar=arcpy.mapping.ListLayers(mxdrecent,"*Parcel*",dfrecent)[0]

# make layer from parcel SQL statement
arcpy.SelectLayerByAttribute_management(cpar, "CLEAR_SELECTION")
arcpy.MakeFeatureLayer_management (cpar, "selpar", where_clause=whereClause, workspace="#", field_info="#")

# remove output centroid if already exists
centroid = arcpy.FeatureToPoint_management("selpar", outpath+"/centroid.shp", point_location = "INSIDE")


for mxd in mxdList:
        mapdoc = arcpy.mapping.MapDocument(mxd)
        mxdname=basename(mxd)
        mapdoccopy=outpath+"/"+mxdname
        silentremove(mapdoccopy)
        mapdoc.saveACopy(mapdoccopy)
        mapdoc = arcpy.mapping.MapDocument(mapdoccopy)
        mapdoc.title=mxdname
        mapdoc.save()
        for df in arcpy.mapping.ListDataFrames(mapdoc):
            mapdoc.activeview='PAGE_LAYOUT'
            arcpy.RefreshActiveView()
            par=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",df)[0]
            arcpy.SelectLayerByLocation_management(par,"intersect",outpath+"/centroid.shp")
            par.showLabels = True
            df.zoomToSelectedFeatures()
            arcpy.RefreshActiveView()
            df_pdf = outpath+'/'+df.name+".pdf"
            silentremove(df_pdf)
            arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
            arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf)# ,data_frame=df) # export individual pdfs for each dataframe
            mapdoc.save()
# mapdoc = arcpy.mapping.MapDocument(mapdoccopy)

mapbookpath=os.path.join(outpath+'/'+title+".pdf")
silentremove(mapbookpath)
mapbook = arcpy.mapping.PDFDocumentCreate(mapbookpath) # create empty pdf to append individual pdfs to

pdfList = glob.glob('*.pdf')	# list pdfs in directory 
for pdf in pdfList:
    pdfpath=os.path.join(outpath+"/"+pdf)# append individual pdfs to final pdf
    mapbook.appendPages(pdfpath) # save and close final pdf

mapbook.saveAndClose()
del mapbook
del centroid

for centroidfile in glob.glob(outpath+"/centroid*"):
    silentremove(centroidfile)


for pdf in pdfList:
    silentremove(pdf)

mxdList = glob.glob('*.mxd')

for mxd in mxdList:
    silentremove(mxd)