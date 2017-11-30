###############################
# author: steven c gonzalez
# date: 11/17/2017
# title: Public Research Map Book by Year
# description: Select Certified Bexar Appraisal District taxable parcels by
# 'AccountID' and print .pdf maps for each certified year. This module uses
# the most recent mxd (today, Public_Research_2017.mxd) to select desired
# parcels by 'AccountID' and zoom to them. The tool merged the selected
# parcels, created a negative 5' buffer, and iteratively zooms to the parcels
# that intersect that geometry in the list of mxd's located in the mxd dir.

# YEARLY UPDATES:
# Once certified parcels are created each year, copy the most recent mxd,
# rename it with the newly certified year, and change the data source for the
# document's layers to point to Public Certified datasets.
# These are current located at \\bcad90\gis\GIS_DATA\GIS_Public_Data
# inside GDBs inside respective folders.

# Developed on:
# 'ipython_path': 'C:\\Python27\\ArcGIS10.5\\lib\\site-packages\\IPython',
# 'ipython_version': '5.5.0',
# 'os_name': 'nt',
# 'platform': 'Windows-7-6.1.7601-SP1',
# 'sys_executable': 'C:\\Python27\\ArcGIS10.5\\python.exe',
# 'sys_platform': 'win32',
# 'sys_version': '2.7.12 (v2.7.12:d33e0cf91556, Jun 27 2016, 15:19:22) [MSC v.1500 32 bit (Intel)]'}

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

## get date info
today = date.today()
printDate = today.strftime('%m-%d-%Y')
startTime = time.strftime('%I:%M:%S-%p')

## set script tool parameters
accountIDS =  arcpy.GetParameter(0)       # get Account IDs, comma-separated
title=  arcpy.GetParameterAsText(1) 	    # output pdf title character string
outDirName=  arcpy.GetParameterAsText(2)  # output directory to house pdf(s)
ischecked = arcpy.GetParameterAsText(3)    # would you like to include aerials?
tolerance = arcpy.GetParameterAsText(4)    # negative buffer tolerance in feet

## get SQL statement from Account ID csv string
s = " OR AccountID = "       # SQL stuff to insert
seq = tuple(accountIDS.split(",")) # make tuple, sep by comma, to sequence through
whereClause =  "AccountID = "+s.join( seq ) # join SQL stuff to tuple iteratively to get statement

## define output locations
wd = os.path.dirname(os.path.realpath(__file__)) # get script's current location directory to write log files to
env.workspace = wd
# wd= "\\\\bcad90\\GIS_DATA/Special_Projects/Public Research" # for testing
outpath=wd+"/output/"+printDate+"/"+outDirName


if not os.path.exists(outpath):

	os.makedirs(outpath)		# create an empty directory to store outputs
arcpy.AddMessage("Output directory "+ outpath+" created!")

arcpy.AddMessage("Removing previous Map Documents in Output Directory")

mxdout = glob.glob(outpath+'/*.mxd')
for mxd in mxdout:
	silentremove(mxd)

mxdInDir = os.path.join(wd+r'\mxd')
mxdList = glob.glob(mxdInDir+'\*.mxd')


## remove merged and buffered polygons if already exists
arcpy.AddMessage("Cleaning Output Directory of previously merged polygons")
for mergeFile in glob.glob(outpath+"/mrg*"):
	silentremove(mergeFile)

arcpy.AddMessage("Cleaning Output Directory of previously buffered, merged polygons")
for buffFile in glob.glob(outpath+"/bffr*"):
	silentremove(buffFile)

arcpy.AddMessage("Cleaning Output Directory of previously created layer files")
for lyrFile in glob.glob(outpath+"/*.lyr"):
	silentremove(lyrFile)

## access most recent mxd (last because they are in alphabetical order as Public_Research_2009.mxd -> Public_Research_2017.mxd)
arcpy.AddMessage("Accessing map document at "+ mxdList[-1]+ " to select parcels from.")
mxdrecent = arcpy.mapping.MapDocument(mxdList[-1])
mxdrecentName=basename(mxdList[-1])


# get dataframe in mxd
# dataframe go backwards in years from top to bottom
# so access most recent parcel and make layer
# should only be one layer with "parcel" in name per dataframe

## get parcel layer
dfrecent = arcpy.mapping.ListDataFrames(mxdrecent)[0] # only one df, but first df selected
arcpy.AddMessage("Accessed dataframe '"+ dfrecent.name + "' in " + mxdrecentName + " to select parcel layer from.")

## get parcel layer in df as 'cpar' ('current' parcel)
cpar=arcpy.mapping.ListLayers(mxdrecent,"*Parcel*",dfrecent)[0] # first layer with "Parcel"
arcpy.AddMessage("Accessed "+ cpar.name + " layer to select parcels where " + whereClause)

## make layer from parcel SQL statement
if arcpy.Exists("selpar"):
    arcpy.Delete_management("selpar")
arcpy.AddMessage("About to create new  selection from "+ cpar.name + " layer to select where " + whereClause)

## create clear selected of current parcels, just in case
arcpy.SelectLayerByAttribute_management(cpar, "CLEAR_SELECTION")

## make feature layer of recently certified parcels where AccountIDS = {input AccountIDS}
arcpy.MakeFeatureLayer_management (cpar, "selpar", where_clause=whereClause, workspace="#", field_info="#")
result = arcpy.GetCount_management("selpar") # count number of features in selected parcel layer
count = int(result.getOutput(0)) # get output of result
arcpy.AddMessage("{0} parcel(s) selected ".format(count)) # print number of parcels selected

## if the number of selected features by account id in recent mxd = 0, stop program.
if count == 0:
    arcpy.AddError("No parcels found with desired Account IDs in "+mxdList[-1]+ " where " + whereClause +". Exiting program. Check mxd data source.")
    sys.exit() # quit program if no parcels found by AccountID

## merge selected parcels into one geometry
arcpy.AddMessage("Merging selected parcels into one geometry")
merge = arcpy.Merge_management("selpar", outpath+"/mrg.shp")

## buffer merged, selected parcels by -5 (to avoid selected parcels whose border may
## go into another property line due to topological errors
arcpy.AddMessage("Buffering merged parcels by "+"-"+tolerance+" Feet"+" to perform subsequent spatial joins.")
buff = arcpy.Buffer_analysis(merge, outpath+"/bffr.shp", "-"+tolerance+" Feet", "FULL", dissolve_option="ALL")

## set mapbook path to outpath + {input-title}. pdf
mapbookpath=os.path.join(outpath+'/'+title+".pdf")
arcpy.AddMessage("Overwriting "+ mapbookpath + "if exists.")
silentremove(mapbookpath) # delete mapbook if already exists to overwrite

## Reverse mxd order to print from recent mxd to past mxds 

## loop through mxds and dataframe to export individual maps
try:
	global mapbook
	mapbook = arcpy.mapping.PDFDocumentCreate(mapbookpath)
	arcpy.AddMessage("Creating final mapbook PDF at "+ mapbookpath)
	for mxd in mxdList:
			mapdoc = arcpy.mapping.MapDocument(mxd)
			mxdname=basename(mxd) # get mxd name
			arcpy.AddMessage("Working on "+ mxdname)
			mapdoccopy=outpath+"/"+mxdname
			mapdoc.saveACopy(mapdoccopy) # copy template mxd to output directory
			mapdoc = arcpy.mapping.MapDocument(mapdoccopy)
			mapdoc.title=mxdname # set mapdoc title to match input mxdname
			mapdoc.save() # save mapdoc
			for df in arcpy.mapping.ListDataFrames(mapdoc):
				global mapbook # call global variable inside loop
				mapdoc.activeview='PAGE_LAYOUT' # set mapdoc view to layout view
				arcpy.RefreshActiveView() # refresh dataframe view
				par=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",df)[0] # get parcel layer from dataframe
				arcpy.SelectLayerByLocation_management(par,"intersect",outpath+"/bffr.shp") # select parcels in mxd that intersect recently certified parcels selected
				arcpy.AddMessage("Selecting parcels in " + mxdname+ " that intersect selected parcels in "+mxdList[-1])
				par.showLabels = True # turn on PID labels
				df.zoomToSelectedFeatures() # zoom to selected parcels that intersect merged buffer
				arcpy.RefreshActiveView() # refresh dataframe view
				df_pdf = outpath+'/'+df.name+".pdf" # create pdf file name in outpath with dataframe name (which should be year)
				arcpy.AddMessage("Overwriting "+df_pdf+" if already existed")
				silentremove(df_pdf) # delete intermediate pdf if already exists
                ## if 'Include Aerials?" = true (checked), do this
				if str(ischecked) == 'true':
					aerialDir = r"\\bcad90\doqq\Bexar_Aerial_Mosaics" # Directory with Bexar County aerial mosaics
					aerialGDB = aerialDir+r"\Bexar_Aerial_Mosaics.gdb" # gdb inside aerial directory with aerial mosaics
					arcpy.env.workspace = aerialGDB # set env.workspace to aerial gdb
					in_mosaicdataset_name = r"\bexarMosaics_"+df.name # input mosaic dataset name as bexarMosaics_[year], following naming convention in gdb
					in_mosaicLayer = in_mosaicdataset_name+"_layer"
					silentremove(in_mosaicLayer)       # remove input mosaic layer if exists
					if arcpy.Exists(aerialGDB+in_mosaicdataset_name):
						par.transparency = 75 # if adding imagery, set parcel transparency to 80.
						arcpy.MakeMosaicLayer_management(aerialGDB+in_mosaicdataset_name,in_mosaicdataset_name+"_layer")
						layer = arcpy.mapping.Layer(in_mosaicdataset_name+"_layer")        # make mosaic dataset layer a mapping layer
						arcpy.AddMessage("Adding " + df.name + " aerial imagery to "+ mxdname)
						arcpy.mapping.AddLayer(df,layer,"BOTTOM")		# add aerial imagery to bottom of dataframe
						layers = arcpy.mapping.ListLayers(df)  
						for l in layers:  
							if l.isGroupLayer and l.name == layer.name:  
								glayers = arcpy.mapping.ListLayers(l)  
								for gl in glayers:  
									if gl.name == "Footprint":  
										gl.transparency = 100
										break
						silentremove(in_mosaicLayer) # delete mosaic layer created
						del in_mosaicLayer # remove lock on mosaic layer
						del layer # remove lock on layer
					else:
						par.transparency = 0 # set parcel transparency to 0 if no imagery found
						arcpy.AddMessage("No imagery found for " + df.name + " in "+ mxdname)
					arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
					arcpy.AddMessage("Exporting map layout from " + mxdname + " to "+ df_pdf)
					arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf)# ,data_frame=df) # export individual pdfs for each dataframe
					arcpy.AddMessage("Appending map page to mapbook")
					mapbook.appendPages(df_pdf) # append individual year map export to mapbook
					arcpy.AddMessage("Saving " + mxdname)
					mapdoc.save()
					arcpy.AddMessage("Cleaning " +outpath+ " of " + df_pdf)
					silentremove(df_pdf) # delete intermediate pdf doc. comment out if you want a pdf for each individual mxd/year
					arcpy.AddMessage("Removing lock on mosaic dataset layer")
                ## if 'Include Aerials?" = false (unchecked), do this
				else:
					par.transparency = 0
					arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
					arcpy.AddMessage("Exporting map layout from " + mxdname + " to "+ df_pdf)
					arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf)# ,data_frame=df) # export individual pdfs for each dataframe
					arcpy.AddMessage("Appending map page to mapbook")
					mapbook.appendPages(df_pdf) # append individual year map export to mapbook
					arcpy.AddMessage("Saving " + mxdname)
					mapdoc.save()
					arcpy.AddMessage("Cleaning " +outpath+ " of " + df_pdf)
					silentremove(df_pdf) # delete intermediate pdf doc. comment out if you want a pdf for each individual mxd/year
					arcpy.AddMessage("Removing lock on mosaic dataset layer")
			arcpy.AddMessage("Removing lock on " + mxdname)
			del mapdoc # remove lock on mapdoc template copy
	
    ## delete intermediate data saved to file
	arcpy.AddMessage("Cleaning " +outpath+ " of intermediate data")
	for mergeFile in glob.glob(outpath+"/mrg*"):
		silentremove(mergeFile)

	for buffFile in glob.glob(outpath+"/bffr*"):
		silentremove(buffFile)

	arcpy.AddMessage("Cleaning " +outpath+ " of intermediate map document copies")
	mxdoutList = glob.glob(outpath+'/*.mxd')
	for mxd in mxdoutList:
		silentremove(mxd)

	arcpy.AddMessage("Saving and closing mapbook at "+ mapbookpath)
	mapbook.saveAndClose()
	del mapbook

	arcpy.AddMessage("Map Export Complete! :) Output located at "+mapbookpath)

except:
    arcpy.AddMessage(arcpy.GetMessages())
    print "Create Public Information Map Request failed :("

