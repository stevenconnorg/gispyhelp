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

for df in listdf:
        parcel=arcpy.mapping.ListLayers(mapdoc,"*Parcel*",df)
        par=parcel[0]
        # need to add field to get AccountID from ListFields to build whereClause...
        # whereClause = rep {AccountID field name} = {input pids}, OR
        # arcpy.ListFields(parcel[0],"*Account*",field_type="Double")
        try:
            arcpy.SelectLayerByAttribute_management(par,"NEW_SELECTION",whereClause)
            # arcpy.Select_analysis(par,outpath+"/"+title+".shp",whereClause)
            df.zoomToSelectedFeatures()
            #for lyr in arcpy.mapping.ListLayers(mapdoc,"",df):
            #	arcpy.mapping.AddLayer(df,lyr,"AUTO_ARRANGE") 	# add each layer in df to map document
            df_pdf = outpath+'/'+df.name+".pdf"
            arcpy.mapping.PDFDocumentCreate(df_pdf) 		# create empty pdfs for each dataframe
            arcpy.mapping.ExportToPDF(mapdoc,out_pdf=df_pdf,data_frame=df) # export individual pdfs for each dataframe
                    # pdfpath=os.path.join(outpath+'/'+mapdoc.title+".pdf") 
                    # if not os.path.exists(pdfpath):
                    # 	arcpy.mapping.PDFDocumentCreate(pdfpath) 	# create empty pdf to append individual pdfs to
                    # pdfDir=os.path.basename(pdfpath) 				# get directory of output pdf
                    # pdfList = glob(path.join(pdfDir,"*.{}.pdf")) 	# list pdfs in directory 
                    # for pdf in pdfList: 							# append individual pdfs to final pdf
                    # 	pdfpath.appendpages(pdf)
                    # 	del(pdf)
                    # pdfpath.saveAndClose() # save and close final pdf
        except: arcpy.GetMessages()
del mapdoc										# remove lock on mxd
