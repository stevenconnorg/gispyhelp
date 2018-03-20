#-------------------------------------------------------------------------------
# Name:        GIS Viewer Attribution Evaluation
# Version:     V_1.2.12
# Purpose:     Produce report for installtion geodatabase detailing data attribution
#
# Author:      Marie Cline Delgado
#
# Created:     2018/01/26
# Last Update: 2018/03/13
# Description: Evaluate installation geodatabases for minimum attribution required
#              by AFCEC GIS viewer for best display of data.
#-------------------------------------------------------------------------------

# Import modules
import arcpy, time, os, sys, Tkinter, tkFileDialog, getpass, collections, xlwt
from datetime import datetime
from operator import itemgetter

# Start time
time = datetime.now()
print(time)

# Get username
#username = getpass.getuser()

# Main folder directory variable
mainDir = "C:\\Users\\stevenconnorg\\Documents\\knight-federal-solutions\\ViewerAttribution"
os.chdir(mainDir)


### for gdb in directory of geodatabases.... 
installationGDBS = os.path.join(mainDir,"gdbs")
installationgdbList = []


for subdir, dirs, files in os.walk(installationGDBS):
    for subdir in dirs:
        subdirPath = os.path.join(installationGDBS,subdir)
        installationgdbList.append(subdirPath)
        installationName = os.path.splitext(os.path.basename(subdir))[0]


installGDB=installationgdbList[0]


compGDB = mainDir+"/Viewer_minimum.gdb"

## or get comparison database as parameter 

# compGDB = sys.argv[1] 

def listFcsInGDB():
    ''' set your arcpy.env.workspace to viewer minimum attribution gdb before calling '''
    for fds in arcpy.ListDatasets("*","Feature") :
        for fc in arcpy.ListFeatureClasses('','',fds):
            minFields = (fld.name for fld in arcpy.ListFields(fc) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
            reqDomains = (fld.domain for fld in arcpy.ListFields(fc) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
            for f, d in zip(minFields, reqDomains):
                yield os.path.join(fds, fc, f, d) # add arcpy.env.workspace at beginning of join if want to keep the viewer workspace in the file path
        
def compareGDBs(compGDB,installGDB):
    try:
        # Set workspace to viewer minimum attribution geodatabase or full database attribution database
        arcpy.env.workspace = installGDB
        vwrDataList = list(listFcsInGDB(compGDB))
        print("Minimum attribution stored")
    
    
        # Change workspace to installation geodatabase for evaluation
        arcpy.env.workspace = installGDB
    
        ''' GET FULL LIST OF FEATURE CLASSES IN COMPARISON GDB ''' 
        compFCs = []                        
        for dirpath, dirnames, filenames in arcpy.da.Walk(compGDB, datatype="FeatureClass", type="Any"):
            for filename in filenames:
                compFCs.append(filename) # append comparison feature class name to list
        
        
        for data in vwrDataList:
            theFDS = data.rsplit("\\", 3)[0]
            theFC = data.rsplit("\\", 3)[1]
            theFLD = data.rsplit("\\", 3)[2] 
            theDMN = data.rsplit("\\", 3)[3]       
            
            
            ''' CREATE TABLE TO APPEND ERRORS FOR EACH FEATURE DATASET '''
            
            errorTableName = theFDS+"_FDS_Errors"
            errorTableFieldList = ['FDS','FDS_MISSING','FDS_NONSDS',
                                   'FC','FC_MISSING','FC_NONSDS',
                                   'FIELD','FIELD_MISSING','FIELD_NONSDS',
                                   'DOMAIN','DOMAIN_MISSING','EMPTY_FC',
                                   'NULL_FC_COUNT','TBD_FC_COUNT','OTHER_FC_COUNT',
                                   'NULL_VALUE_COUNTS','TBD_VALUE_COUNTS','OTHER_VALUE_COUNTS','TOTAL_INTD_COUNTS',
                                   'POP_VALS_COUNT','POP_VALS'
                                   ]
     
            errorTable = os.path.join(installGDB,errorTableName)
            
            
            if arcpy.Exists(errorTable): 
                arcpy.Delete_management(errorTable)
            else:
                arcpy.CreateTable_management(installGDB,errorTableName)

                # Name of Feature Class
                arcpy.AddField_management(errorTable, "FDS", "TEXT", 50)
                # Name of Feature Class
                arcpy.AddField_management(errorTable, "FDS_MISSING", "TEXT", 1)
                # is feature class missing? True/False
                arcpy.AddField_management(errorTable, "FDS_NONSDS", "TEXT", 1) 
                
                # Name of Feature Class
                arcpy.AddField_management(errorTable, "FC", "TEXT", 50)
                # is feature class missing? True/False
                arcpy.AddField_management(errorTable, "FC_MISSING", "TEXT", 1)   
                
                # is feature class missing? True/False
                arcpy.AddField_management(errorTable, "FC_NONSDS", "TEXT", 1)                                 
                # Name of Field
                arcpy.AddField_management(errorTable, "FIELD", "TEXT", 50) 
                
                 # is field missing? True/False
                arcpy.AddField_management(errorTable, "FIELD_MISSING", "TEXT", 1)   
                
                # is field missing? True/False
                arcpy.AddField_management(errorTable, "FIELD_NONSDS", "TEXT", 1)   
                
                # Name of required domain in field
                arcpy.AddField_management(errorTable, "DOMAIN", "TEXT", 50)        
                
                 # is this domain missing? True/False
                arcpy.AddField_management(errorTable, "DOMAIN_MISSING", "TEXT", 1)  
                
                # Name of required domain in field
                arcpy.AddField_management(errorTable, "DOMAIN", "TEXT", 50)          
                
                # is feature class empty? True/False
                arcpy.AddField_management(errorTable, "EMPTY_FC", "TEXT", 1)         
                
                # How many NULL values per field?
                arcpy.AddField_management(errorTable, "NULL_FC_COUNT", "LONG", 50)      
                
                # How many TBD values per field?
                arcpy.AddField_management(errorTable, "TBD_FC_COUNT", "LONG", 50)      
                
                # How many OTHER values per field?
                arcpy.AddField_management(errorTable, "OTHER_FC_COUNT", "LONG", 50)     
                
                # break out of individual values and counts for Null, None, NA, etc...
                arcpy.AddField_management(errorTable, "NULL_VALUE_COUNTS", "TEXT", 500)   
                
                # break out of individual values and counts for Null, None, NA, etc...
                arcpy.AddField_management(errorTable, "TBD_VALUE_COUNTS", "TEXT", 500)     
                
                # break out of individual values and counts for Null, None, NA, etc...
                arcpy.AddField_management(errorTable, "OTHER_VALUE_COUNTS", "TEXT", 500)   
                
                # total number of indeterminant values (NULLS + Others + TBD)
                arcpy.AddField_management(errorTable, "TOTAL_INTD_COUNT", "TEXT", 500)   
                
                # Total Number of populated values (not null, tbd, or other)
                arcpy.AddField_management(errorTable, "POP_VALS_COUNT", "LONG",50)    
                
                # Total Number of populated values (not null, tbd, or other)
                arcpy.AddField_management(errorTable, "POP_VALS", "LONG",50000)

            # Create insert cursor for FDS error table
            rows = arcpy.InsertCursor(errorTable)
    
            row = rows.newRow()
            
           # CHECK FOR EXISTANCE OF REQUIRED FEATURE DATASET 
            if arcpy.Exists(os.path.join(installGDB,theFDS)):
                # if feature dataset exists... set FDS Missing Field to FALSE
                row.setValue("FDS", theFDS)
                row.setValue("FDS_MISSING", "F")
                
               # CHECK FOR EXISTANCE OF REQUIRED FEATURE CLASS in FEATURE DATASET
                if arcpy.Exists(os.path.join(installGDB,theFDS,theFC)):
                    row.setValue("FC", theFC)
                    row.setValue("FC_MISSING", "F")
                    
                    # CHECK FOR EXISTANCE OF REQUIRED FIELD in FEATURE CLASS
                    def findField(fc, fi):
                        fieldnames = [field.name for field in arcpy.ListFields(fc)]
                        if fi in fieldnames:
                            return True
                        else:
                            return False
                        
                    # IF required field exists....
                    if findField(os.path.join(installGDB,theFDS,theFC),theFLD):        
                        row.setValue("FIELD", theFLD)
                        row.setValue("FIELD_MISSING", "F")
                        instFCFields = [(str(afld.name).upper(), afld) for afld in arcpy.ListFields(os.path.join(installGDB,theFDS,theFC))]
                        domains = arcpy.da.ListDomains()
                         
                         
                        idx = map(itemgetter(0), instFCFields).index(theFLD.upper())
                        
                        #CREATE SEARCH CURSOR ON FDS, FC, AND FIELDS TO BUILD LIST OF VALUES AND COUNTS
                        with arcpy.da.SearchCursor(os.path.join(installGDB,theFDS,theFC), theFLD) as cur:
                            
                            nullValues = [None, "None", "none", "NONE", "", " ", "NA", "N/A", "n/a","NULL","<NULL>"]
                            otherValues = [ "Other", "other", "OTHER"]
                            tbdValues = ["tbd","TBD","To be determined"]
                            NoneType = type(None)
                            
                            
                            ## GET TOTAL COUNT OF VALUES
                            countValues = collections.Counter(row[0] for row in cur)
                            sumValues = sum(collections.Counter(countValues).values())
  
                            
                            # GET TOTAL COUNT OF 'NULL' VALUES for each NULL VALUE 'CODE'
                            countNulls = list((n[0], n[1]) for n in countValues.items() if n[0] in nullValues)
                            sumNulls = sum(n[1] for n in countNulls)
                            
                            # GET TOTAL COUNT OF 'TBD' VALUES for each NULL VALUE 'CODE'
                            countTBD = list((n[0], n[1]) for n in countValues.items() if n[0] in tbdValues)
                            sumTBD = sum(n[1] for n in countTBD)
                            
                            # GET TOTAL COUNT OF 'OTHER' VALUES for each NULL VALUE 'CODE'
                            countOthers = list((n[0], n[1]) for n in countValues.items() if n[0] in otherValues)
                            sumOther = sum(n[1] for n in countOthers)
                            
                            sumIndt = sumNulls + sumTBD + sumOther
                            sumDetr = sumValues - sumIndt
                            
                            domainName = map(itemgetter(1), instFCFields)[idx].domain
                            domainVals = []
                            domainRng = []
                            for domain in domains:
                                    if domain.name == domainName:
                                        if domain.domainType == 'CodedValue':
                                            domainVals = [val for val, desc in domain.codedValues.items()]
                                        elif domain.domainType == 'Range':
                                            domainRng = range(int(domain.range[0]), int((domain.range[1]+1)))
                                            
                                            
                            #populate counts of populated values, nulls, tbds, and others
                            
                            row.setValue("POP_VALS_COUNT",sumValues)
                            row.setValue("NULL_FC_COUNT",sumNulls)
                            row.setValue("TBD_FC_COUNT",sumTBD)
                            row.setValue("OTHER_FC_COUNT",sumOther)             
                            row.setValue("TOTAL_INTD_COUNT", sumIndt)
                            row.setValue("TOTAL_DET_COUNT", sumDetr)

                            # populate individual value counts for NULL
                            row.setValue("NULL_VALUE_COUNTS", str(countNulls).strip('[]'))
                            row.setValue("TBD_VALUE_COUNTS", str(countTBD).strip('[]'))
                            row.setValue("OTHER_VALUE_COUNTS", str(countOthers).strip('[]'))
                            row.setValue("POP_VALS", str(sumValues).strip('[]'))

                                                        
                            if len(countValues) == 0:
                                
                                row.setValue("EMPTY_FC", "T")
                            # POPULATED WITH VARIATION OF VALUES
                            else:
                                row.setValue("EMPTY_FC", "F")

# =============================================================================
#                                 for v in sorted(countValues.items(), key=lambda x:x[1]):
#                                     
#                                     # OPEN TEXT FIELDS; NO DOMAIN CONSTRAINT
#                                     if domainVals == [] and domainRng == []:
#                                         row.setValue("POP_VALS_COUNT", 0)
#                                         row.setValue("POP_VALS_COUNT", 0)
#                                         populatedValuesSheet.write(popRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style2)
#                                         populatedValuesSheet.write(popRow, 1, v[1], style2)
#                                         popRow+=1
# 
#                                     # CORRECTLY POPULATED CODED VALUES WITHIN A DOMAIN CONSTRAINED FIELD
#                                     elif domainVals != [] and str(v[0]) in domainVals and popRow < 65500:
#                                         populatedValuesSheet.write(popRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style2)
#                                         populatedValuesSheet.write(popRow, 1, v[1], style2)
#                                         popRow+=1
#                                     elif domainVals != [] and str(v[0]) in domainVals and popRow >= 65500:
#                                         populatedValuesSheetCont.write(newPopRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style2)
#                                         populatedValuesSheetCont.write(newPopRow, 1, v[1], style2)
#                                         newPopRow+=1
#                                         popRow+=1
#                                         
#                                     # CORRECTLY POPULATED RANGE VALUES WITHIN A DOMAIN CONSTRAINED FIELD
#                                     elif domainRng != [] and v[0] in domainRng and popRow < 65500:
#                                         populatedValuesSheet.write(popRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style2)
#                                         populatedValuesSheet.write(popRow, 1, v[1], style2)
#                                         popRow+=1
#                                     elif domainRng != [] and v[0] in domainRng and popRow >= 65500:
#                                         populatedValuesSheetCont.write(newPopRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style2)
#                                         populatedValuesSheetCont.write(newPopRow, 1, v[1], style2)
#                                         newPopRow+=1
#                                         popRow+=1
#                                     else:
#                                         # INCORRECTLY POPULATED VALUES WITHIN DOMAIN CONSTRAINED FIELDS
#                                         if popRow < 65500:
#                                             populatedValuesSheet.write(popRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style3)
#                                             populatedValuesSheet.write(popRow, 1, v[1], style3)
#                                             popRow+=1
#                                         elif popRow >= 65500:
#                                             populatedValuesSheetCont.write(newPopRow, 0, v[0] if not isinstance(v[0], NoneType) else 'Null', style3)
#                                             populatedValuesSheetCont.write(newPopRow, 1, v[1], style3)
#                                             newPopRow+=1
#                                             popRow+=1
# =============================================================================

                    # required FIELD does not exist 
                    else:
                        for fc in compFCs:
                            for field in arcpy.ListFields(os.path.join(compGDB,theFDS,fc)):
                                row.setValue("FDS", theFDS)
                                row.setValue("FDS_MISSING", "F")
                                row.setValue("FC", fc)
                                row.setValue("FC_MISSING", "F")
                                row.setValue("FIELD", field.name)
                                row.setValue("FIELD_MISSING", "T")
                                row.setValue("POP_VALS_COUNT",0)
                                row.setValue("NULL_FC_COUNT",0)
                                row.setValue("TBD_FC_COUNT",0)
                                row.setValue("OTHER_FC_COUNT",0)             
                                row.setValue("TOTAL_INTD_COUNT", 0)
                                row.setValue("TOTAL_DET_COUNT", 0)
                                row.setValue("NULL_VALUE_COUNTS", "NA")
                                row.setValue("TBD_VALUE_COUNTS", "NA")
                                row.setValue("OTHER_VALUE_COUNTS", "NA")
                                row.setValue("POP_VALS", "NA")

                #required FEATURE CLASS does not exist 
                else:
                    for fc in compFCs:
                        for field in arcpy.ListFields(os.path.join(compGDB,theFDS,fc)):
                            row.setValue("FDS", theFDS)
                            row.setValue("FDS_MISSING", "F")
                            row.setValue("FC", fc)
                            row.setValue("FC_MISSING", "T")
                            row.setValue("FIELD", field.name)
                            row.setValue("FIELD_MISSING", "T")
                            row.setValue("POP_VALS_COUNT",0)
                            row.setValue("TBD_FC_COUNT",0)
                            row.setValue("OTHER_FC_COUNT",0)             
                            row.setValue("TOTAL_INTD_COUNT", 0)
                            row.setValue("TOTAL_DET_COUNT", 0)
                            row.setValue("NULL_VALUE_COUNTS", "NA")
                            row.setValue("TBD_VALUE_COUNTS", "NA")
                            row.setValue("OTHER_VALUE_COUNTS", "NA")
                            row.setValue("POP_VALS", "NA")
                    
            #required FEATURE DATASET does not exist
            else:
                for fc in compFCs:
                    for field in arcpy.ListFields(os.path.join(compGDB,fc)):
                        row.setValue("FDS", theFDS)
                        row.setValue("FDS_MISSING", "T")
                        row.setValue("FC", fc)
                        row.setValue("FC_MISSING", "T")
                        row.setValue("FIELD", field.name)
                        row.setValue("FIELD_MISSING", "T")
                        row.setValue("POP_VALS_COUNT",0)
                        row.setValue("TBD_FC_COUNT",0)
                        row.setValue("OTHER_FC_COUNT",0)             
                        row.setValue("TOTAL_INTD_COUNT", 0)
                        row.setValue("TOTAL_DET_COUNT", 0)
                        row.setValue("NULL_VALUE_COUNTS", "NA")
                        row.setValue("TBD_VALUE_COUNTS", "NA")
                        row.setValue("OTHER_VALUE_COUNTS", "NA")
                        row.setValue("POP_VALS", "NA")

                        
        rows.insertRow(row)
        del row
        del rows    
    
    except Exception as e:
        # Error time
        t = datetime.now()
        print(t)
        print e.args[0]
        

compareGDBs(compGDB,installGDB)