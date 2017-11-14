###############################
### author: steven c gonzalez
### date: 
### title: Public Research Map Book by Year
### description: 
###############################

## import modules
import arcpy, time, os, sys, glob
from datetime import date
from arcpy import env
import os, errno
from os.path import basename

## define function to remove files silently
def silentremove(filename):
	try:
		os.remove(filename)
	except OSError as e: # this would be "except OSError, e:" before Python 2.6
		if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
			raise # re-raise exception if a different error occurred

## define input pararmeters

# date
today = date.today()
printDate = today.strftime('%m-%d-%Y')
startTime = time.strftime('%I:%M:%S-%p')

# account ID SQL statement
accountIDS = arcpy.GetParameter(0)
tuple(accountIDS.split(","))
s = " OR AccountID = "
seq = tuple(accountIDS.split(",")) # This is sequence of strings.
whereClause =  "AccountID = "+s.join( seq )


title= arcpy.GetParameterAsText(1) 			 # set title string
outDirName= arcpy.GetParameterAsText(2) 			 # set title string
ischecked = arcpy.GetParameterAsText(3) # include aerials?

# define output locations
wd = os.path.dirname(os.path.realpath(__file__)) #### script location directory to write log files to
# wd= r"C:\Users\sgonzalez\Desktop\PR"
outpath=wd+"/output/"+printDate+"/"+outDirName

print "Creating output directory "+outpath
if not os.path.exists(outpath):
	os.makedirs(outpath)		# create an empty directory to store outputs

mxdout = glob.glob(outpath+'/*.mxd')
for mxd in mxdout:
	silentremove(mxd)

mxdList = glob.glob(wd+'/mxd/*.mxd')

##  get centroid of most recent selected parcel(s) ##


# remove merged and buffered polygons if already exists
for mergeFile in glob.glob(outpath+"/mrg*"):
	silentremove(mergeFile)

for buffFile in glob.glob(outpath+"/bffr*"):
	silentremove(buffFile)

for lyrFile in glob.glob(outpath+"/*.lyr"):
	silentremove(lyrFile)
	
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
arcpy.Delete_management("selpar")
arcpy.SelectLayerByAttribute_management(cpar, "CLEAR_SELECTION")
arcpy.MakeFeatureLayer_management (cpar, "selpar", where_clause=whereClause, workspace="#", field_info="#")

# remove output buffer if already exists
merge = arcpy.Merge_management("selpar", outpath+"/mrg.shp")
buff = arcpy.Buffer_analysis(merge, outpath+"/bffr.shp", "-5 Feet", "FULL", dissolve_option="ALL")



mapbookpath=os.path.join(outpath+'/'+title+".pdf")
silentremove(mapbookpath)
global mapbook
mapbook = arcpy.mapping.PDFDocumentCreate(mapbookpath)

for mxd in mxdList:
		mapdoc = arcpy.mapping.MapDocument(mxd)
		mxdname=basename(mxd)
		mapdoccopy=outpath+"/"+mxdname
		mapdoc.saveACopy(mapdoccopy)
		mapdoc = arcpy.mapping.MapDocument(mapdoccopy)
		mapdoc.title=mxdname
		mapdoc.save()
		for df in arcpy.mapping.ListDataFrames(mapdoc):
			global mapbook
			mapdoc.activeview='PAGE_LAYOUT'
			arcpy.RefreshActiveView()
			par=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",df)[0]
			arcpy.SelectLayerByLocation_management(par,"intersect",outpath+"/bffr.shp")
			par.showLabels = True
			df.zoomToSelectedFeatures()
			arcpy.RefreshActiveView()
			df_pdf = outpath+'/'+df.name+".pdf"
			silentremove(df_pdf)
			if str(ischecked) == 'true':
				par.transparency = 50
				aerialDir = r"\\bcad90\doqq\Bexar_Aerial_Mosaics\layers"
				in_mosaicdataset_name = aerialDir+"/bexarMosaics_"+df.name+".lyr"
				aeriallyr = arcpy.mapping.Layer(in_mosaicdataset_name)
				arcpy.mapping.AddLayer(df,aeriallyr,"BOTTOM")
				arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
				arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf)# ,data_frame=df) # export individual pdfs for each dataframe
			else:
				par.transparency = 0
				arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
				arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf)# ,data_frame=df) # export individual pdfs for each dataframe
			mapbook.appendPages(df_pdf)
			silentremove(df_pdf)

mapbook.saveAndClose()
mapdoc.save()
del mapdoc
del mapbook


# pdfList = glob.glob(outpath+'/*.pdf')	# list pdfs in directory 
# create empty pdf to append individual pdfs to
#for pdf in pdfList[::-1]:
	#pdfname=basename(pdf)
	#pdfpath=os.path.join(outpath+"/"+pdfname)# append individual pdfs to final pdf
	#mapbook.appendPages(pdfpath) # save and close final pdf
	#mapbook.saveAndClose()
			
for mergeFile in glob.glob(outpath+"/mrg*"):
    silentremove(mergeFile)

for buffFile in glob.glob(outpath+"/bffr*"):
    silentremove(buffFile)

#for pdf in pdfList:
    #silentremove(pdf)

mxdoutList = glob.glob(outpath+'/*.mxd')

for mxd in mxdoutList:
	silentremove(mxd)

