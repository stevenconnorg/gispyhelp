#-------------------------------------------------------------------------------
# Name:        GIS Viewer Attribution Evaluation
# Version:     V_2.0
# Purpose:     Produce report for installation geodatabase detailing data attribution
#
# Author:      Marie Cline Delgado & Steven Connor Gonzalez
#
# Created:     2018/01/26
# Last Update: 2018/03/22
# Description: Evaluate installation geodatabases for minimum attribution required
#              by AFCEC GIS viewer for best display of data.
#-------------------------------------------------------------------------------

# Import modules
import arcpy, time, os, sys, collections
from pandas import DataFrame
from datetime import datetime
from operator import itemgetter
import pickle


# Start time
time = datetime.now()
print(time)

# Get username
#username = getpass.getuser()

# Main folder directory variable
mainDir = "C:\\Users\\stevenconnorg\\Documents\\knight-federal-solutions\\ViewerAttribution"
os.chdir(mainDir)


### for gdb in directory of geodatabases.... 
installationGDBdir = os.path.join(mainDir,"gdbs")

''' or get directory of geodatabases as parameters ''' 
# installationGDBdir = sys.argv[1] 


installationgdbList = []


for subdir, dirs, files in os.walk(installationGDBdir):
    for subdir in dirs:
        subdirPath = os.path.join(installationGDBdir,subdir)
        installationgdbList.append(subdirPath)
        installationName = os.path.splitext(os.path.basename(subdir))[0]

# compGDB = mainDir+"/Viewer_minimum.gdb"
compGDB = mainDir+"/Full_geodatabase.gdb"

''' or get comparison database as parameter !'''
# compGDB = sys.argv[2] 

        

arcpy.env.workspace = compGDB

# =============================================================================
# def listFcsInGDB():
#     ''' set your arcpy.env.workspace to viewer minimum attribution gdb before calling '''
#     for fds in arcpy.ListDatasets('','feature') :
#         for fc in arcpy.ListFeatureClasses('','',fds):
#             minFields = (fld.name for fld in arcpy.ListFields(fc) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
#             reqDomains = (fld.domain for fld in arcpy.ListFields(fc) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
#             for f, d in zip(minFields, reqDomains):
#                 yield os.path.join(fds, fc, f, d) # add arcpy.env.workspace at beginning of join if want to keep the viewer workspace in the file path
# 
# =============================================================================
def listFcsInGDB():
    ''' set your arcpy.env.workspace to viewer minimum attribution gdb before calling '''
    for fds in arcpy.ListDatasets('','feature') :
        for fc in arcpy.ListFeatureClasses('','',fds):
            minFields = (fld.name for fld in arcpy.ListFields(fc) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
            reqDomains = (fld.domain for fld in arcpy.ListFields(fc) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
            for f, d in zip(minFields, reqDomains):
                yield os.path.join(fds, fc, f, d) # add arcpy.env.workspace at beginning of join if want to keep the viewer workspace in the file path
                
                
print("Getting required Feature Datasets, Feature Classes, Fields, and Domains in" + compGDB)        


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


# load correct vwrdatalist based on input comparison geodatabase
# if viewer attribute data exists, load, else create list and save
if compGDB == mainDir+"/Full_geodatabase.gdb":
    if os.path.exists('fullDataList.pkl'):
        with open('fullDataList.pkl', 'rb') as input:
            vwrDataList = pickle.load(input)
    else:     
        vwrDataList = list(listFcsInGDB())
        save_object(vwrDataList, 'fullDataList.pkl')
else:
    if os.path.exists('vwrDataList.pkl'):
            with open('vwrDataList.pkl', 'rb') as input:
                vwrDataList = pickle.load(input)
    else:     
        vwrDataList = list(listFcsInGDB())
        save_object(vwrDataList, 'vwrDataList.pkl')

print("Minimum attribution stored")


# GET FULL LIST OF FEATURE CLASSES IN COMPARISON GDB# 
compFDs = []    
arcpy.env.workspace = compGDB                    
for fds in arcpy.ListDatasets():
    compFDs.append(fds) # append comparison feature class name to list


# GET FULL LIST OF FEATURE CLASSES IN COMPARISON GDB# 
compFCs = []                        
for dirpath, dirnames, filenames in arcpy.da.Walk(compGDB, datatype="FeatureClass", type="Any"):
    for filename in filenames:
        compFCs.append(filename) # append comparison feature class name to list

# create error table for each feature dataset in 



# CREATE TABLE TO APPEND ERRORS FOR EACH FEATURE DATASET
   # if error table already exists, delete rows
   # otherwise, create empty table
def createNullTable(installGDB,nullTableName="MissingData"):
    errorTable = os.path.join(installGDB,nullTableName)
    arcpy.CreateTable_management(installGDB,nullTableName)
    # Installation Name
    arcpy.AddField_management(errorTable, "INSTALLATION", "TEXT", field_length = 100) 
    # Name of Field
    arcpy.AddField_management(errorTable, "FDS", "TEXT", field_length = 1000) 
    # Name of Field
    arcpy.AddField_management(errorTable, "FC", "TEXT", field_length = 500) 
    # Name of Field
    arcpy.AddField_management(errorTable, "FIELD", "TEXT", field_length = 500) 
    # is field missing? True/False
    arcpy.AddField_management(errorTable, "FIELD_NONSDS", "TEXT", field_length = 1)   
    # is feature class empty? True/False
    arcpy.AddField_management(errorTable, "EMPTY_FC", "TEXT", field_length = 1)         
    # How many NULL values per field?
    arcpy.AddField_management(errorTable, "NULL_FC_COUNT", "LONG",field_length =  50)      
    # How many TBD values per field?
    arcpy.AddField_management(errorTable, "TBD_FC_COUNT", "LONG", field_length = 50)      
    # How many OTHER values per field?
    arcpy.AddField_management(errorTable, "OTHER_FC_COUNT", "LONG",field_length =  50)     
    # break out of individual values and counts for Null, None, NA, etc...
    arcpy.AddField_management(errorTable, "NULL_VALUE_COUNTS", "TEXT", field_length = 500)   
    # break out of individual values and counts for Null, None, NA, etc...
    arcpy.AddField_management(errorTable, "TBD_VALUE_COUNTS", "TEXT", field_length = 500)     
    # break out of individual values and counts for Null, None, NA, etc...
    arcpy.AddField_management(errorTable, "OTHER_VALUE_COUNTS", "TEXT", field_length = 500)   
    # total number of indeterminant values (NULLS + Others + TBD)
    arcpy.AddField_management(errorTable, "TOTAL_INTD_COUNT", "LONG", field_length = 500)   
    # total number of indeterminant values (NULLS + Others + TBD)
    arcpy.AddField_management(errorTable, "TOTAL_DET_COUNT", "LONG", field_length = 500)   
    # Total Number of populated values (not null, tbd, or other)
    arcpy.AddField_management(errorTable, "POP_VALS_COUNT", "LONG",field_length = 50)    
    # Total Number of populated values (not null, tbd, or other)
    arcpy.AddField_management(errorTable, "POP_VALS", "TEXT",field_length = 50000000)
    # Total Number of populated values (not null, tbd, or other)
    arcpy.AddField_management(errorTable, "INC_POP_VALS", "TEXT",field_length = 500000000)
    print (errorTable + " Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])
    
       # otherwise, create empty table
def createMissingFLDtbl(installGDB,missingFLDTblName="MissingFields"):
    errorTable = os.path.join(installGDB,missingFLDTblName)
    arcpy.CreateTable_management(installGDB,missingFLDTblName)
    # is feature class empty? True/False
    arcpy.AddField_management(errorTable, "FDS", "TEXT", field_length = 50)
    # is feature class missing? True/False
    arcpy.AddField_management(errorTable, "FC", "TEXT",field_length =  50)   
    # is feature class missing? True/False
    arcpy.AddField_management(errorTable, "FIELD_MISSING", "TEXT", field_length = 50)   
    # Installation Name
    arcpy.AddField_management(errorTable, "INSTALLATION", "TEXT", field_length = 100)  
    print (errorTable + " Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])

    
   # otherwise, create empty table
def createMissingFCtbl(installGDB,missingFCTblName="MissingFCs"):
    errorTable = os.path.join(installGDB,missingFCTblName)
    arcpy.CreateTable_management(installGDB,missingFCTblName)
    # is feature class missing? True/False
    arcpy.AddField_management(errorTable, "FC_MISSING", "TEXT", field_length = 50)   
    # is feature class missing? True/False
    arcpy.AddField_management(errorTable, "FDS", "TEXT",field_length =  50)  
    # Installation Name
    arcpy.AddField_management(errorTable, "INSTALLATION", "TEXT",field_length =  100)  
    print (errorTable + " Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])

   # otherwise, create empty table
def createMissingFDstbl(installGDB,missingFDTblName="MissingFDS"):
    errorTable = os.path.join(installGDB,missingFDTblName)
    arcpy.CreateTable_management(installGDB,missingFDTblName)
    # is feature class empty? True/False
    arcpy.AddField_management(errorTable, "FDS_MISSING", "TEXT",field_length =  50)
    # Installation Name
    arcpy.AddField_management(errorTable, "INSTALLATION", "TEXT", field_length = 100)         
    print (errorTable + " Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])

    
def compareGDBs(installGDB,compGDB):
    installationName = os.path.splitext(os.path.basename(installGDB))[0]
    arcpy.env.workspace = installGDB

    
    
    missingFDTblName="MissingFDS"
    missingFCTblName="MissingFCs"
    missingFLDTblName="MissingFields"
    nullTableName="MissingData"

    # IF THE TABLE EXISTS, DELETE ROWS,
    # ELSE CREATE ERROR TABLE FOR EACH FEATURE DATASET IN COMPGDB

    # CREATE MISSING FEATURE DATASET TABLE
    if arcpy.Exists(os.path.join(installGDB,missingFDTblName)): 
        arcpy.Delete_management(os.path.join(installGDB,missingFDTblName))
        print (missingFDTblName + " already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createMissingFDstbl(installGDB,missingFDTblName)
    else:
        createMissingFDstbl(installGDB,missingFDTblName)
    
    # CREATE MISSING FEATURE CLASS TABLE
    if arcpy.Exists(os.path.join(installGDB,missingFCTblName)): 
        arcpy.Delete_management(os.path.join(installGDB,missingFCTblName))
        print (missingFCTblName + " already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createMissingFCtbl(installGDB,missingFCTblName)
    else:
        createMissingFCtbl(installGDB,missingFCTblName)
    
    # CREATE MISSING FIELD TABLE
    if arcpy.Exists(os.path.join(installGDB,missingFLDTblName)): 
        arcpy.Delete_management(os.path.join(installGDB,missingFLDTblName))
        print (missingFLDTblName + " already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createMissingFLDtbl(installGDB,missingFLDTblName)
    else:
        createMissingFLDtbl(installGDB,missingFLDTblName)
    
    # CREATE NULL DATA TABLE
    if arcpy.Exists(os.path.join(installGDB,nullTableName)): 
        arcpy.Delete_management(os.path.join(installGDB,nullTableName))
        print (nullTableName + " already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createNullTable(installGDB,nullTableName)
    else:
        createNullTable(installGDB,nullTableName)        
    
        
    edit = arcpy.da.Editor(arcpy.env.workspace)
    edit.startEditing(False, False)
    edit.startOperation()

    # WITHIN EACH REQUIRED FEATURE DATASET AND FEATURE CLASS THAT THE INSTALLATION HAS, 
    # WHICH FIELDS ARE MISSING?
    
    nullTable = os.path.join(installGDB,nullTableName)
    nullrows = arcpy.InsertCursor(nullTable)

    # WITHIN EACH REQUIRED FEATURE DATASET AND FEATURE CLASS THAT THE INSTALLATION HAS, 
    # WHICH FIELDS ARE MISSING?
    missFLDTable = os.path.join(installGDB,missingFLDTblName)
    fldrows = arcpy.InsertCursor(missFLDTable)
    
    # WITHIN THE FEATURE DATASETS THAT THE INSTALLATION HAS, 
    # WHICH FEATURE CLASSES ARE MISSING?
    missFCTable = os.path.join(installGDB,missingFCTblName)
    fcrows = arcpy.InsertCursor(missFCTable)
    
    # WHICH FEATURE DATASETS ARE MISSING FROM THE INSTALLATION DATABASE COMPARED TO COMPARISON DATABASE
    missFDSTable = os.path.join(installGDB,missingFDTblName)
    fdrows = arcpy.InsertCursor(missFDSTable)
    
    for data in vwrDataList:
        print("Working on "+installationName + " - " + data +": List Index #"+ str(vwrDataList.index(data)))

        theFDS = data.rsplit("\\", 3)[0]
        theFC = data.rsplit("\\", 3)[1]
        theFLD = data.rsplit("\\", 3)[2] 
        #theDMN = data.rsplit("\\", 3)[3]   
        row = nullrows.newRow()
        
       # CHECK FOR EXISTANCE OF REQUIRED FEATURE DATASET 
        if arcpy.Exists(os.path.join(installGDB,str(theFDS).upper())):
           # CHECK FOR EXISTANCE OF REQUIRED FEATURE CLASS in FEATURE DATASET
            if arcpy.Exists(os.path.join(installGDB,str(theFDS).upper(),str(theFC).upper())):
                # CHECK FOR EXISTANCE OF REQUIRED FIELD in FEATURE CLASS
                def findField(fc, fi):
                    fieldnames = [field.name.upper() for field in arcpy.ListFields(fc)]
                    if fi.upper() in fieldnames:
                        return True
                    else:
                        return False

                # IF required field exists....
                if findField(os.path.join(installGDB,theFDS,theFC),theFLD):        
                    row.setValue("FIELD", theFLD)
                    row.setValue("FIELD_NONSDS", "F")
                    instFCFields = [(str(afld.name).upper(), afld) for afld in arcpy.ListFields(os.path.join(installGDB,theFDS,theFC))]
                    domains = arcpy.da.ListDomains()
                    idx = map(itemgetter(0), instFCFields).index(theFLD.upper())
                    row.setValue("FDS", theFDS)
                    row.setValue("FC", theFC)
                    #CREATE SEARCH CURSOR ON FDS, FC, AND FIELDS TO BUILD LIST OF VALUES AND COUNTS
                    with arcpy.da.SearchCursor(os.path.join(installGDB,theFDS,theFC), str(theFLD).upper()) as cur:
                    #with arcpy.da.SearchCursor(os.path.join(installGDB,"Recreation","RecArea_A"), str("recreationAreaType").upper()) as cur:
                        nullValues = [None, "None", "none", "NONE", "",99999,-99999, " ", "NA", "N/A", "n/a","NULL","Null","<NULL>","<Null>"]
                        otherValues = [ "Other", "other", "OTHER"]
                        tbdValues = ["tbd","TBD","To be determined"]
                        NoneType = type(None)
                        indtList = nullValues + otherValues+ tbdValues
                        
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
                                                
                        # GET TOTAL COUNT OF POPULATED VALUES 
                        countDet = list((n[0], n[1]) for n in countValues.items() if n[0] not in indtList)

                        sumIndt = sumNulls + sumTBD + sumOther
                        sumDetr = sumValues - sumIndt
                        
                        
                                                
                        # get values to populate cell cleanly 
                        otherStrings = str()
                        for element in countOthers:
                            value = str(element[0])
                            count = str(element[1])   
                            if count > 1:
                                valCount = value+" has "+count+" feature"
                                otherStrings = otherStrings + valCount +". "
                            else:
                                valCount = value+" has "+count+" features"
                                otherStrings = otherStrings + valCount +". "
                                                 
                        # get values to populate cell cleanly 
                        tbdStrings = str()
                        for element in countTBD:
                            value = str(element[0])
                            count = str(element[1])   
                            if count > 1:
                                valCount = value+" has "+count+" feature"
                                tbdStrings = tbdStrings + valCount +". "
                            else:
                                valCount = value+" has "+count+" features"
                                tbdStrings = tbdStrings + valCount +". "   
                                             
                        # get values to populate cell cleanly 
                        nullStrings = str()
                        for element in countNulls:
                            value = str(element[0])
                            count = str(element[1])   
                            if count > 1:
                                valCount = value+" has "+count+" feature"
                                nullStrings = nullStrings + valCount +". "
                            else:
                                valCount = value+" has "+count+" features"
                                nullStrings = nullStrings + valCount +". "                       
                        
                        
                        
                        domainName = map(itemgetter(1), instFCFields)[idx].domain
                        domainVals = []
                        domainRng = []
                        for domain in domains:
                                if domain.name == domainName:
                                    if domain.domainType == 'CodedValue':
                                        domainVals = [val for val, desc in domain.codedValues.items()]
                                    elif domain.domainType == 'Range':
                                        domainRng = range(int(domain.range[0]), int((domain.range[1]+1)))
                  
                        if sumValues == 0:                                
                            row.setValue("EMPTY_FC", "T")
                        else:
                            row.setValue("EMPTY_FC", "F")
    
                        #populate counts of populated values, nulls, tbds, and others
                        row.setValue("INSTALLATION",installationName)
                        row.setValue("POP_VALS_COUNT",sumValues)
                        row.setValue("NULL_FC_COUNT",sumNulls)
                        row.setValue("TBD_FC_COUNT",sumTBD)
                        row.setValue("OTHER_FC_COUNT",sumOther)             
                        row.setValue("TOTAL_INTD_COUNT", sumIndt)
                        row.setValue("TOTAL_DET_COUNT", sumDetr)
                        
                        # populate individual value counts for NULL
                        row.setValue("NULL_VALUE_COUNTS", nullStrings)
                        row.setValue("TBD_VALUE_COUNTS", tbdStrings)
                        row.setValue("OTHER_VALUE_COUNTS", otherStrings)
                        
                        # get list of counts for each unique value in field
                        vals = sorted(countValues.items(), key=lambda x:x[1])
                        
                        # set and remove all values that have TBD, OTHER, or NULL (defined above)
                        vals = set(vals) - set(countTBD) - set(countOthers) - set(countNulls)
                        
                        # get set back to list
                        vals = list(vals)
                        
                        # create empty string to concatenate each value
                        
                        ## valstr = 'correctly' populated values (either conforms to domain, or text in non-domain contrained field)
                        ## incvalstr = incorrectly populated values (values not in accordance with domain)
                        valstr = str()
                        incvalstr = str()
                        
                        for v in vals:
                            
                            # OPEN TEXT FIELDS; NO DOMAIN CONSTRAINT
                            if domainVals == [] and domainRng == []: 
                                
                                dom = str(v[0])
                                val = str(v[1])
                                if val > 1:
                                    domCount = dom+" has "+val+" feature"
                                    valstr = valstr + domCount +". "
                                else:
                                   domCount = dom+" has "+val+" features"
                                   valstr = valstr + domCount +". " 
                            # CORRECTLY POPULATED CODED VALUES WITHIN A DOMAIN CONSTRAINED FIELD 
                            elif domainVals != [] and v[0] in domainVals: 
                                
                                dom = str(v[0])
                                val = str(v[1])
                                if val > 1:
                                    domCount = dom+" has "+val+" feature"
                                    valstr = valstr + domCount +". "
                                else:
                                   domCount = dom+" has "+val+" features"
                                   valstr = valstr + domCount +". " 
                            # CORRECTLY POPULATED RANGE VALUES WITHIN A DOMAIN CONSTRAINED FIELD                                    
                            elif domainRng != [] and v[0] in domainRng:
                            #elif domainRng != [] and [i for i in v if i in domainRng]:
                                
                                dom = str(v[0])
                                val = str(v[1])
                                if val > 1:
                                    domCount = dom+" has "+val+" feature"
                                    valstr = valstr + domCount +". "
                                else:
                                   domCount = dom+" has "+val+" features"
                                   valstr = valstr + domCount +". " 
                            # INCORRECTLY POPULATED VALUES WITHIN DOMAIN CONSTRAINED FIELDS
                            else:     
                                                                
                                dom = str(v[0])
                                val = str(v[1])
                                if val > 1:
                                    domCount = dom+" has "+val+" feature"
                                    incvalstr = incvalstr + domCount +". "
                                else:
                                   domCount = dom+" has "+val+" features"
                                   incvalstr = incvalstr + domCount +". "
                                
                        # remove last comma at end of value string 

                        len(valstr)
                        row.setValue("POP_VALS",valstr)  
                        row.setValue("INC_POP_VALS",incvalstr)  
                        nullrows.insertRow(row)
                        
                    
                else:
                    fldrow = fldrows.newRow()
                    fldrow.setValue("FDS", theFDS)
                    fldrow.setValue("FC", theFC)
                    fldrow.setValue("FIELD_MISSING", theFLD)
                    fldrow.setValue("INSTALLATION", installationName)
                    fldrows.insertRow(fldrow)
                    del fldrow           
            #required FEATURE CLASS does not exist 
            else:
                fcrow = fcrows.newRow()
                fcrow.setValue("FDS", theFDS)
                fcrow.setValue("FC_MISSING", theFC)
                fcrow.setValue("INSTALLATION", installationName)
                fcrows.insertRow(fcrow)
                del fcrow
    
        #required FEATURE DATASET does not exist
        else:
            fdrow = fdrows.newRow()
            fdrow.setValue("FDS_MISSING", theFDS)
            fdrow.setValue("INSTALLATION", installationName)
            fdrows.insertRow(fdrow)
            del fdrow
    
    # Missing FDS is appended for each record in loop... remove duplicates
    columns_to_check=['FDS_MISSING','INSTALLATION']
    arcpy.DeleteIdentical_management(missFDSTable,fields=columns_to_check)
    columns_to_check=['FDS','FC_MISSING','INSTALLATION']
    arcpy.DeleteIdentical_management(missFCTable,fields=columns_to_check)

    edit.stopOperation()
    edit.stopEditing(True)   
    del nullrows 
    del fdrows
    del fldrows
    del fcrows
    
# =============================================================================
# except Exception as e:
#     # Error time
#     t = datetime.now()
#     print(t)
#     print e.args[0]
# =============================================================================
        
        

from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()
num_cores = num_cores - 1
Parallel(n_jobs=num_cores)(delayed(compareGDBs)(installGDB) for installGDB in installationgdbList)


installGDB=installationgdbList[1]


# or apply function across geodatabases in serial...
for installGDB in installationgdbList:
    compareGDBs(installGDB,compGDB)


# borrowed from http://joelmccune.com/arcgis-to-pandas-data-frame-using-a-search-cursor/
def get_field_names(table):
    """
    Get a list of field names not inclusive of the geometry and object id fields.
    :param table: Table readable by ArcGIS
    :return: List of field names.
    """
    # list to store values
    field_list = []

    # iterate the fields
    for field in arcpy.ListFields(table):

        # if the field is not geometry nor object id, add it as is
        if field.type != 'Geometry' and field.type != 'OID':
            field_list.append(field.name)

        # if geomtery is present, add both shape x and y for the centroid
        elif field.type == 'Geometry':
            field_list.append('SHAPE@XY')

    # return the field list
    return field_list


def table_to_pandas_dataframe(table, field_names=None):
    """
    Load data into a Pandas Data Frame for subsequent analysis.
    :param table: Table readable by ArcGIS.
    :param field_names: List of fields.
    :return: Pandas DataFrame object.
    """
    # if field names are not specified
    if not field_names:

        # get a list of field names
        field_names = get_field_names(table)

    # create a pandas data frame
    dataframe = DataFrame(columns=field_names)

    # use a search cursor to iterate rows
    with arcpy.da.SearchCursor(table, field_names) as search_cursor:

        # iterate the rows
        for row in search_cursor:

            # combine the field names and row items together, and append them
            dataframe = dataframe.append(
                dict(zip(field_names, row)), 
                ignore_index=True
            )

    # return the pandas data frame
    return dataframe


## CONVERT TABLES TO PANDAS DATAFRAMES
missingFDTblName="MissingFDS"
missingFCTblName="MissingFCs"
missingFLDTblName="MissingFields"
nullTableName="MissingData"    

nullTable = os.path.join(installGDB,nullTableName)
missFLDTable = os.path.join(installGDB,missingFLDTblName)
missFCTable = os.path.join(installGDB,missingFCTblName)
missFDSTable = os.path.join(installGDB,missingFDTblName)


pdNullTbl= table_to_pandas_dataframe(nullTable, field_names=None)
pdFLDTbl= table_to_pandas_dataframe(missFLDTable, field_names=None)
pdFCTbl= table_to_pandas_dataframe(missFCTable, field_names=None)
pdFDSTbl= table_to_pandas_dataframe(missFDSTable, field_names=None)

import numpy
import pandas
def summariseComparisons(pdNullTbl,pdFLDTbl,pdFCTbl,pdFDSTbl):

    pdNullTbl = pdNullTbl.replace('', numpy.nan)
    pdFLDTbl = pdFLDTbl.replace('', numpy.NaN)
    pdFCTbl = pdFCTbl.replace('', numpy.NaN)
    pdFDSTbl = pdFDSTbl.replace('', numpy.NaN)


    ### FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE NULL, TBD, AND OTHER
    ## THEN EXPORT THEM TO THE GEODATABASE
    nullCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['NULL_FC_COUNT'].agg('sum').fillna(0).reset_index()

    nullCntByFLD=pandas.DataFrame(nullCntByFLD)

    x = numpy.array(numpy.rec.fromrecords(nullCntByFLD))
    names = nullCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    arcpy.da.NumPyArrayToTable(x, os.path.join(installGDB,"NullCellsbyFC"))
    
    
    tbdCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['TBD_FC_COUNT'].agg('sum').fillna(0).reset_index()
    tbdCntByFLD=pandas.DataFrame(tbdCntByFLD)

    x = numpy.array(numpy.rec.fromrecords(tbdCntByFLD))
    names = tbdCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    arcpy.da.NumPyArrayToTable(x, os.path.join(installGDB,"TBDCellsbyFC"))
    
    
    otherCntByFLD = pdNullTbl.=groupby(['FDS','FC','INSTALLATION'])['OTHER_FC_COUNT'].agg('sum').fillna(0).reset_index()
    otherCntByFLD=pandas.DataFrame(otherCntByFLD)

    x = numpy.array(numpy.rec.fromrecords(otherCntByFLD))
    names = otherCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    arcpy.da.NumPyArrayToTable(x, os.path.join(installGDB,"OtherCellsbyFC"))


       
    ### FOR EACH FEATURE CLASS INCLUDED, HOW MANY ARE EMPTY? 
    emptyFCbyFDS=pdNullTbl.query("EMPTY_FC == 'T'").groupby(['FDS','FC','INSTALLATION']).size().reset_index()
    emptyFCbyFDS=pandas.DataFrame(emptyFCbyFDS)
    emptyFCbyFDS.columns = ['FDS','FC','INSTALLATION','FIELDS']
    emptyFCbyFDS = emptyFCbyFDS.drop('FIELDS',1)
    
    x = numpy.array(numpy.rec.fromrecords(emptyFCbyFDS))
    names = emptyFCbyFDS.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    arcpy.da.NumPyArrayToTable(x, os.path.join(installGDB,"EmptyFeatureClasses"))
    
    ### FOR EACH FEATURE CLASS INCLUDED, HOW MANY ARE EMPTY?
    emptyFCcnt = len(pdNullTbl.query("EMPTY_FC == 'T'").groupby(['FDS','FC','EMPTY_FC']).size().reset_index() )
    nonemptyFCcnt = len(pdNullTbl.query("EMPTY_FC == 'F'").groupby(['FDS','FC','EMPTY_FC']).size().reset_index() )
    installationName = os.path.splitext(os.path.basename(installGDB))[0]

    ### GET NUMBER OF MISSING FEATURE DATASETS
    missingFDScnt = pdFDSTbl.groupby(['FDS_MISSING','INSTALLATION']).ngroups
    
    ### GET NUMBER OF MISSING FEATURE CLASSES per FEATURE DATASET
    missingFCcnt = pdFCTbl.groupby(['FDS','FC_MISSING','INSTALLATION']).ngroups


    # BIND DATA INTO A PANDAS DATAFRAME
    d = {'Installation':[installationName],'MissingFDScount': [missingFDScnt], 'MissingFCcount': [missingFCcnt],'InclFeatsEmpty':[emptyFCcnt],'InclFeatsNonEmpty':[nonemptyFCcnt]}
    df = pandas.DataFrame(data=d)
    x = numpy.array(numpy.rec.fromrecords(nullCntByFLD))
    names = nullCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    arcpy.da.NumPyArrayToTable(x, os.path.join(installGDB,"NullCellsbyFC"))




    ### GET COUNT OF FIELDS WITH INCORRECTLY POPULATED VALUES
    #pdNullTbl sum where INC_POP_VALS != ''
    pdNullTbl.loc[pdNullTbl['TOTAL_INTD_COUNT'] == '']
    pdNullTbl.loc[pdNullTbl['TOTAL_INTD_COUNT'] != '']
    
    print pdNullTbl.replace(r'\s+', numpy.nan, regex=True)
    pdNullTbl = pdNullTbl.replace(r'^\s+$', np.nan, regex=True)
    pdNullTbl.count()
    pdNullTbl.isnull()
    ### 
    ## ....
    print(str(errorTable))
