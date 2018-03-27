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
import time
from datetime import date

# Start time
time = datetime.now()
print(time)

# Get username
#username = getpass.getuser()

# Main folder directory variable

# when running outside of IDE
#mainDir = os.path.dirname(os.path.realpath(__file__)))

# change this to the location of python script
mainDir = "C:\\Users\\stevenconnorg\\Documents\\knight-federal-solutions\\ViewerAttribution"
os.chdir(mainDir)

# within the main directory, create a directory called "gdbs" that houses all the geodatabase you want to compare.
installationGDBdir = os.path.join(mainDir,"gdbs")

# or get directory of geodatabases as parameters 
# installationGDBdir = sys.argv[1] 


# get a list of all the geodatabase paths...
installationgdbList = []


for subdir, dirs, files in os.walk(installationGDBdir):
    for subdir in dirs:
        subdirPath = os.path.join(installationGDBdir,subdir)
        installationgdbList.append(subdirPath)
        installationName = os.path.splitext(os.path.basename(subdir))[0]

# compGDB = mainDir+"/Viewer_minimum.gdb"
compGDB = mainDir+"/Full_geodatabase.gdb"

# or get comparison database as parameter !
# compGDB = sys.argv[2] 

arcpy.env.workspace = compGDB


# CREATE TABLE TO APPEND ERRORS FOR EACH FEATURE DATASET
   # if error table already exists, delete rows
   # otherwise, create empty table
def createNullTable(installGDB,nullTableName="MissingData"):
    errorTable = os.path.join(installGDB,nullTableName)
    arcpy.CreateTable_management(installGDB,nullTableName)
    # Installation Name
    arcpy.AddField_management(errorTable, "INSTALLATION", "TEXT", field_length = 50) 
    # Name of Field
    arcpy.AddField_management(errorTable, "FDS", "TEXT", field_length = 50) 
    # Name of Field
    arcpy.AddField_management(errorTable, "FC", "TEXT", field_length = 50) 
    # Name of Field
    arcpy.AddField_management(errorTable, "FIELD", "TEXT", field_length = 50) 
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
    arcpy.AddField_management(errorTable, "NULL_VALUE_COUNTS", "TEXT", field_length = 32766)   
    # break out of individual values and counts for Null, None, NA, etc...
    arcpy.AddField_management(errorTable, "TBD_VALUE_COUNTS", "TEXT", field_length = 32766)     
    # break out of individual values and counts for Null, None, NA, etc...
    arcpy.AddField_management(errorTable, "OTHER_VALUE_COUNTS", "TEXT", field_length = 32766)   
    # total number of indeterminant values (NULLS + Others + TBD)
    arcpy.AddField_management(errorTable, "TOTAL_INTD_COUNT", "LONG", field_length = 50)   
    # total number of indeterminant values (NULLS + Others + TBD)
    arcpy.AddField_management(errorTable, "TOTAL_DET_COUNT", "LONG", field_length = 50)   
    # Total Number of populated values (not null, tbd, or other)
    arcpy.AddField_management(errorTable, "POP_VALS_COUNT", "LONG",field_length = 50)    
    # Total Number of populated values (not null, tbd, or other)
    arcpy.AddField_management(errorTable, "POP_VALS", "TEXT",field_length = 32766)
    # Total Number of populated values (not null, tbd, or other)
    arcpy.AddField_management(errorTable, "INC_POP_VALS", "TEXT",field_length = 32766)
    print (nullTableName + " Table Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])
    
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
    print (missingFLDTblName + " Table Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])

    
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
    print (missingFCTblName + " Table Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])

   # otherwise, create empty table
def createMissingFDstbl(installGDB,missingFDTblName="MissingFDS"):
    errorTable = os.path.join(installGDB,missingFDTblName)
    arcpy.CreateTable_management(installGDB,missingFDTblName)
    # is feature class empty? True/False
    arcpy.AddField_management(errorTable, "FDS_MISSING", "TEXT",field_length =  50)
    # Installation Name
    arcpy.AddField_management(errorTable, "INSTALLATION", "TEXT", field_length = 100)         
    print (missingFDTblName + " Table Created in " + os.path.splitext(os.path.basename(installGDB) + "gdb")[0])

    
def compareGDBs(installGDB,compGDB):
    '''
    inputs: file paths to 2 geodatabases
        installGDB = geodatabase to be compared against 'compGDB'
        compGDB    = geodatabase that install GDB is compared against
        
        
    outputs: 4 tables created within input 'installGDB'
        MissingFDS (table)    : which feature datasets are missing in the installGDB that are included in compGDB?
            -- fields within MissingFDS Table -- 
                1) INSTALLATION - name of installGDB
    
                2) FDS_MISSING - name of feature dataset missing
    
        MissingFC  (table)    : within feature datasets correctly included, which feature classes are missing?
            -- fields within MissingData Table -- 
                1) INSTALLATION - name of installGDB
    
                2) FDS - name of feature dataset for feature class being analyzed
    
                3) FC_MISSING- name of feature class missing
    
    
        MissingFields (table) : within the feature dataset/feature class combo correctly included, which fields are missing?
            -- fields within MissingData Table -- 
                1) INSTALLATION - name of installGDB
    
                2) FDS - name of feature dataset for field being analyzed
    
                3) FC- name of feature feature class for field being analyzed
    
                4) FIELD_MISSING - name of field missing from feature dataset/feature class that is included in the comparison GDB.
    
    
        MissingData (table)   : within the feature dataset/feature class combo correctly included, what data is missing?
            -- fields within MissingData Table -- 
                1) INSTALLATION - name of installGDB
    
                2) FDS - name of feature dataset for field being analyzed
    
                3) FC- name of feature feature class for field being analyzed
    
                4) FIELD - name of field being analyzed
    
                5) FIELD_NONSDS - True or False? If the field is not included in compGDB == T
    
                6) EMPTY_FC - is this feature class empty? T/F
    
                7) NULL_FC_COUNT - the count of features with NULL values within field
                    NULL values are counted if cell equals any of following:  [None, "None", "none", "NONE", "",99999,-99999, " ", "NA", "N/A", "n/a","NULL","Null","<NULL>","<Null>"]
                    
                8) TBD_FC_COUNT - the count of features with TBD values within field
                    TBD values are counted if cell equals any of following: ["tbd","TBD","To be determined"]
                    
                9) OTHER_FC_COUNT - the count of features with OTHER values within field
                    OTHER values are counted if cell equals any of following:  [ "Other", "other", "OTHER"]
                    
                10) NULL_VALUE_COUNTS - the individual counts of each unique entry for NULL cells, 
                        e.g.: " '' has 1 feature. ' '  has 1 feature. 'None' has 2 feature. "
                        
                11) TBD_VALUE_COUNTS - the individual counts of each unique entry for TBD cells 
                        e.g.: " 'tbd' has 1 feature. 'TBD'  has 1 feature. 'To be determined' has 2 feature. "
                        
                12) OTHER_VALUE_COUNTS - the individual counts of each unique entry for OTHER cells
                        e.g.: " 'OTHER' has 1 feature. 'other'  has 1 feature. 'Other' has 2 feature. "
                        
                13) TOTAL_INTD_COUNT - total count of cells with INDETERMINANT values (i.e.: Null, TBD, or Other values) per field
    
                14) TOTAL_DET_COUNT - total count of cells with DETERMINANT values (i.e.: NOT Null, NOT TBD, or NOT Other values) per field
    
                15) POP_VALS_COUNT  - total count of features POPULATED (either INDETERMINANT or DETERMINANT) within field
    
                16) POP_VALS - the individual counts of each unique entry for DETERMINED (not null, tbd, or other) cells that are 'correctly' populated (i.e.: adheres to domain-contraint or text in non-domain contrained field)
                        e.g.: "'BX Exchange' has 1 feature. 'Homestead Air Reserve Base' has 2 feature. U.S. 'Customs Ramp Area' has 1 feature."
                        
                17) INC_POP_VALS - the individual counts of each unique entry for DETERMINED (not null, tbd, or other) cells that are 'incorrectly' populated (i.e.: DOES NOT adhere to domain-contrained field) 
                        e.g.: "'9999' has 1 feature. '341' has 1 feature. '343' has 1 feature. "
    
    '''
    
    import time
    from datetime import datetime 
    start_time = datetime.now()
    installationName = os.path.splitext(os.path.basename(installGDB))[0]
    arcpy.env.workspace = installGDB

    
    
    missingFDTblName="MissingFDS"
    missingFCTblName="MissingFCs"
    missingFLDTblName="MissingFields"
    nullTableName="MissingData"


    # IF THE TABLE EXISTS, DELETE ROWS,
    # ELSE CREATE ERROR TABLE FOR EACH FEATURE DATASET IN COMPGDB
    
    ### TK put this table creation part in a loop
    
    # CREATE MISSING FEATURE DATASET TABLE
    if arcpy.Exists(os.path.join(installGDB,missingFDTblName)): 
        arcpy.Delete_management(os.path.join(installGDB,missingFDTblName))
        print (missingFDTblName + " Table already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createMissingFDstbl(installGDB,missingFDTblName)
    else:
        createMissingFDstbl(installGDB,missingFDTblName)
    
    # CREATE MISSING FEATURE CLASS TABLE
    if arcpy.Exists(os.path.join(installGDB,missingFCTblName)): 
        arcpy.Delete_management(os.path.join(installGDB,missingFCTblName))
        print (missingFCTblName + " Table already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createMissingFCtbl(installGDB,missingFCTblName)
    else:
        createMissingFCtbl(installGDB,missingFCTblName)
    
    # CREATE MISSING FIELD TABLE
    if arcpy.Exists(os.path.join(installGDB,missingFLDTblName)): 
        arcpy.Delete_management(os.path.join(installGDB,missingFLDTblName))
        print (missingFLDTblName + " Table already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
        createMissingFLDtbl(installGDB,missingFLDTblName)
    else:
        createMissingFLDtbl(installGDB,missingFLDTblName)
    
    # CREATE NULL DATA TABLE
    if arcpy.Exists(os.path.join(installGDB,nullTableName)): 
        arcpy.Delete_management(os.path.join(installGDB,nullTableName))
        print (nullTableName + " Table already exists in " + os.path.splitext(os.path.basename(installGDB) )[0]+ ".gdb -- REPLACING")
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
    
    arcpy.env.workspace = compGDB
    for theFDS in arcpy.ListDatasets():
        arcpy.env.workspace = compGDB
        for theFC in arcpy.ListFeatureClasses(feature_dataset=theFDS):
            minFields = (fld.name.upper() for fld in arcpy.ListFields(os.path.join(compGDB,theFDS,theFC)) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
# =============================================================================
# 
            reqDomains = (fld.domain for fld in arcpy.ListFields(os.path.join(compGDB,theFDS,theFC)) if str(fld.name) not in ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area'])
#             for theFLD in minFields:
#                 theFLD
#                 today = date.today()
#                 
#                 import time
#                 timenow = time.strftime('%I:%M:%S-%p')
#                 
# 
# =============================================================================
            import time
            today = date.today()
            timenow = time.strftime('%I:%M:%S-%p')
            printDate = today.strftime('%mm_%dd_%Y')
            print(": Working on "+installationName + "   ---  " + printDate + " at " + timenow + " ---  Feature : " + theFDS + "//" + theFC )     
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
                    for theFLD in arcpy.ListFields(os.path.join(installGDB,str(theFDS).upper(),str(theFC).upper())):
                        arcpy.env.workspace = installGDB
                        ignoreFLD = ['Shape', 'OBJECTID', 'Shape_Length', 'Shape_Area']
                        row = nullrows.newRow()
                        if theFLD.name not in ignoreFLD:           
                            with arcpy.da.SearchCursor(os.path.join(installGDB,theFDS,theFC), str(theFLD.name).upper()) as cur:
                                row.setValue("FIELD", theFLD.name)
                                minF = list(minFields)
                                minF = [x.upper() for x in minF]
                                if theFLD.name.upper() not in minF:
                                    row.setValue("FIELD_NONSDS", "T")
                                else:
                                   row.setValue("FIELD_NONSDS", "F") 
                                instFCFields = [(str(afld.name).upper(), afld) for afld in arcpy.ListFields(os.path.join(installGDB,theFDS,theFC))]
                                domains = arcpy.da.ListDomains()
                                idx = map(itemgetter(0), instFCFields).index(theFLD.name.upper())
                                row.setValue("FDS", theFDS)
                                row.setValue("FC", theFC)
                                
                                #CREATE SEARCH CURSOR ON FDS, FC, AND FIELDS TO BUILD LIST OF VALUES AND COUNTS
                                #with arcpy.da.SearchCursor(os.path.join(installGDB,"Recreation","RecArea_A"), str("recreationAreaType").upper()) as cur:
                                nullValues = [None, "None", "none", "NONE", "","-99999","77777",77777, " ", "NA", "N/A", "n/a","NULL","Null","<NULL>","<Null>","  ","   ","    ","     "]
                                otherValues = [ "Other", "other", "OTHER","88888",88888]
                                tbdValues = ["tbd","TBD","To be determined","Tbd",99999,"99999"]
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

                                sumIndt = sumNulls + sumTBD + sumOther
                                sumDetr = sumValues - sumIndt
                                
                                
                                #populate counts of populated values, nulls, tbds, and others
                                row.setValue("INSTALLATION",installationName)
                                row.setValue("POP_VALS_COUNT",sumValues)
                                row.setValue("NULL_FC_COUNT",sumNulls)
                                row.setValue("TBD_FC_COUNT",sumTBD)
                                row.setValue("OTHER_FC_COUNT",sumOther)             
                                row.setValue("TOTAL_INTD_COUNT", sumIndt)
                                row.setValue("TOTAL_DET_COUNT", sumDetr)
                                                        
                                # get other values to populate cell cleanly 
                                otherStrings = str()
                                for element in countOthers:
                                    if element[0] is None:
                                            value = "NULL"
                                    elif element[0] is int or type(element[0]) is float or type(element[0]) is int or type(element[0]) is datetime:
                                    #elif element[0] is not str:
                                        value =unicode(str(element[0]).encode('utf-8'), errors="ignore")
                                    else:
                                        value =unicode(element[0].encode('utf-8'), errors="ignore")
                                    count =str(element[1])     
                                    if int(count) < 2 :
                                        valCount = "'"+value+"' has "+count+" feature"
                                        otherStrings = otherStrings + valCount +". "
                                    else:
                                        valCount = "'"+value+"' has "+count+" features"
                                        otherStrings = otherStrings + valCount +". "
                                                         
                                # get tbd values to populate cell cleanly 
                                tbdStrings = str()
                                for element in countTBD:
                                    if element[0] is None:
                                            value = "NULL"
                                    elif element[0] is int or type(element[0]) is float or type(element[0]) is int or type(element[0]) is datetime:
                                    #elif element[0] is not str:
                                        value =unicode(str(element[0]).encode('utf-8'), errors="ignore")
                                    else:
                                        value =unicode(element[0].encode('utf-8'), errors="ignore")
                                    count =str(element[1])   
                                    if int(count) < 2 :
                                        valCount = "'"+value+"' has "+count+" feature"
                                        tbdStrings = tbdStrings + valCount +". "
                                    else:
                                        valCount = "'"+value+"' has "+count+" features"
                                        tbdStrings = tbdStrings + valCount +". "   
                                                     
                                # get null values to populate cell cleanly 
                                nullStrings = str()
                                for element in countNulls:
                                    if element[0] is None:
                                            value = "NULL"
                                    elif element[0] is int or type(element[0]) is float or type(element[0]) is int or type(element[0]) is datetime:
                                    #elif element[0] is not str:
                                        value =unicode(str(element[0]).encode('utf-8'), errors="ignore")
                                    else:
                                        value =unicode(element[0].encode('utf-8'), errors="ignore")
                                    count =str(element[1])     
                                    if int(count) < 2 :
                                        valCount = "'"+value+"' has "+count+" feature"
                                        nullStrings = nullStrings + valCount +". "
                                    else:
                                        valCount = "'"+value+"' has "+count+" features"
                                        nullStrings = nullStrings + valCount +". "                       
                                
                                
                                
                                # populate individual value counts for NULL
                                row.setValue("NULL_VALUE_COUNTS", nullStrings)
                                row.setValue("TBD_VALUE_COUNTS", tbdStrings)
                                row.setValue("OTHER_VALUE_COUNTS", otherStrings)
                                
                                domainName = map(itemgetter(1), instFCFields)[idx].domain
                                domainVals = []
                                domainRng = []
                                
                                for domain in domains:
                                        if domain.name == domainName:
                                            if domain.domainType == 'CodedValue':
                                                domainVals = [val for val, desc in domain.codedValues.items()]
                                            elif domain.domainType == 'Range':
                                                domainRng = range(int(domain.range[0]), int((domain.range[1]+1)))
                                        #for domain.name not in reqDomains:
                                            #.... 
                          
                                if sumValues == 0:                                
                                    row.setValue("EMPTY_FC", "T")
                                else:
                                    row.setValue("EMPTY_FC", "F")
            
                                
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
                                if len(vals)> 50:
                                        valstr = "Greater than 50 unique values -- not included."
                                        incvalstr = "Greater than 50 unique values -- not included."
                                else:
                                    for v in vals:
                                        
                                        # OPEN TEXT FIELDS; NO DOMAIN CONSTRAINT
                                        
                                        if domainVals == [] and domainRng == []: 
                                            if v[0] is None:
                                                dom = "NULL"
                                            elif v[0] is int or type(v[0]) is float or type(v[0]) is int or type(v[0]) is datetime:
                                            #elif v[0] is not str:
                                                dom =unicode(str(v[0]).encode('utf-8'), errors="ignore")
                                            else:
                                                dom =unicode(v[0].encode('utf-8'), errors="ignore")
                                            val =str(v[1])
                                            if val < 2:
                                                domCount = "'"+dom+"' has "+val+" feature"
                                                valstr = valstr + domCount +". "
                                            else:
                                               domCount = "'"+dom+"' has "+val+" features"
                                               valstr = valstr + domCount +". " 
                                        # CORRECTLY POPULATED CODED VALUES WITHIN A DOMAIN CONSTRAINED FIELD 
                                        elif domainVals != [] and v[0] in domainVals: 
                                            if v[0] is None:
                                                dom = "NULL"
                                            elif v[0] is int or type(v[0]) is float or type(v[0]) is int or type(v[0]) is datetime:
                                            #elif v[0] is not str:
                                                dom =unicode(str(v[0]).encode('utf-8'), errors="ignore")
                                            else:
                                                dom =unicode(v[0].encode('utf-8'), errors="ignore")
                                            val =str(v[1])
                                            if val < 2:
                                                domCount = "'"+dom+"' has "+val+" feature"
                                                valstr = valstr + domCount +". "
                                            else:
                                               domCount = "'"+dom+"' has "+val+" features"
                                               valstr = valstr + domCount +". " 
                                        # CORRECTLY POPULATED RANGE VALUES WITHIN A DOMAIN CONSTRAINED FIELD                                    
                                        elif domainRng != [] and v[0] in domainRng:
                                        #elif domainRng != [] and [i for i in v if i in domainRng]:
                                            if v[0] is None:
                                                dom = "NULL"
                                            elif v[0] is int or type(v[0]) is float or type(v[0]) is int or type(v[0]) is datetime:
                                            #elif v[0] is not str:
                                                dom =unicode(str(v[0]).encode('utf-8'), errors="ignore")
                                            else:
                                                dom =unicode(v[0].encode('utf-8'), errors="ignore")
                                            val =str(v[1])
                                            if val < 2: 
                                                domCount = "'"+dom+"' has "+val+" feature"
                                                valstr = valstr + domCount +". "
                                            else:
                                               domCount = "'"+dom+"' has "+val+" features"
                                               valstr = valstr + domCount +". " 
                                        # INCORRECTLY POPULATED VALUES WITHIN DOMAIN CONSTRAINED FIELDS
                                        else:    
                                            if v[0] is None:
                                                dom = "NULL"
                                            elif v[0] is int or type(v[0]) is float or type(v[0]) is int or type(v[0]) is datetime:
                                            # elif v[0] is not str:
                                                dom =unicode(str(v[0]).encode('utf-8'), errors="ignore")
                                            else:
                                                dom =unicode(v[0].encode('utf-8'), errors="ignore")
                                            val =str(v[1])
                                            if val < 2:
                                                domCount = "'"+dom+"' has "+val+" feature"
                                                incvalstr = incvalstr + domCount +". "
                                            else:
                                               domCount = "'"+dom+"' has "+val+" features"
                                               incvalstr = incvalstr + domCount +". "
                                # remove last comma at end of value string 
                                row.setValue("POP_VALS",valstr)  
                                row.setValue("INC_POP_VALS",incvalstr)  
                                nullrows.insertRow(row)
                        else:
                            pass
                        del row
                    for minFLD in minFields:
                        if findField(os.path.join(installGDB,theFDS,theFC),minFLD):
                            pass
                        else:
                            fldrow = fldrows.newRow()
                            fldrow.setValue("FDS", theFDS)
                            fldrow.setValue("FC", theFC)
                            fldrow.setValue("FIELD_MISSING", minFLD)
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
    
    columns_to_check=['FDS','INSTALLATION','FC','FIELD_MISSING']
    arcpy.DeleteIdentical_management(missFLDTable,fields=columns_to_check)
    
    edit.stopOperation()
    edit.stopEditing(True)  
    del nullrows 
    del fdrows
    del fldrows
    del fcrows
    
    from datetime import datetime 
    time_elapsed = datetime.now() - start_time 
    print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
            
        
# =============================================================================
# except Exception as e:
#     # Error time
#     t = datetime.now()
#     print(t)
#     print e.args[0]
# =============================================================================
        
      
installGDB = installationgdbList[3]
# or apply function across geodatabases in serial...
for installGDB in installationgdbList:
    compareGDBs(installGDB,compGDB)
  

# or apply function across geodatabases in parallel!
from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()
num_cores = num_cores - 1
Parallel(n_jobs=num_cores)(delayed(compareGDBs)(installGDB) for installGDB in installationgdbList)


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




import numpy
import pandas


def summariseComparisons(installGDB):
    
    '''
    inputs: file paths to 2 geodatabases
        installGDB = geodatabase to be compared against 'compGDB'
        
        
    outputs: 4 tables created within input 'installGDB'
    
        NullCellCountbyFC (table)    : xxxxxxxxxxx?
            -- fields within NullCellCountbyFC Table --
            
                1) INSTALLATION - xxxxxxxxxxx
                        e.g.: xxxxx
                2) FDS_MISSING - xxxxxxxxxxx
    


    
    '''
    
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
    
    
    # replace cells with '' as NaN
    pdNullTbl = pdNullTbl.replace('', numpy.nan)
    pdFLDTbl = pdFLDTbl.replace('', numpy.NaN)
    pdFCTbl = pdFCTbl.replace('', numpy.NaN)
    pdFDSTbl = pdFDSTbl.replace('', numpy.NaN)


    # FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE NULL
    ## THEN EXPORT THEM TO THE GEODATABASE
    nullCntByFC = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['NULL_FC_COUNT'].agg('sum').fillna(0).reset_index()

    nullCntByFC=pandas.DataFrame(nullCntByFC)

    x = numpy.array(numpy.rec.fromrecords(nullCntByFC))
    names = nullCntByFC.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"NullCellCountbyFC")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)
    
    # FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE TBD
    ## THEN EXPORT THEM TO THE GEODATABASE
    tbdCntByFC = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['TBD_FC_COUNT'].agg('sum').fillna(0).reset_index()
    tbdCntByFC=pandas.DataFrame(tbdCntByFC)

    x = numpy.array(numpy.rec.fromrecords(tbdCntByFC))
    names = tbdCntByFC.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"TBDCellCountbyFC")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)


    # FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE OTHER
    ## THEN EXPORT THEM TO THE GEODATABASE
    otherCntByFC = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['OTHER_FC_COUNT'].agg('sum').fillna(0).reset_index()
    otherCntByFC=pandas.DataFrame(otherCntByFC)

    x = numpy.array(numpy.rec.fromrecords(otherCntByFC))
    names = otherCntByFC.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"OtherCellCountbyFC")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)


    
    ''' do the above but grouping by field also '''
        # FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE NULL
    ## THEN EXPORT THEM TO THE GEODATABASE
    nullCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION','FIELD'])['NULL_FC_COUNT'].agg('sum').fillna(0).reset_index()

    nullCntByFLD=pandas.DataFrame(nullCntByFLD)
    nullCntByFLD=nullCntByFLD.query('NULL_FC_COUNT > 0')
    
    x = numpy.array(numpy.rec.fromrecords(nullCntByFLD))
    names = nullCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"NullCellCountbyFLD")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)
    
    # FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE TBD
    ## THEN EXPORT THEM TO THE GEODATABASE
    tbdCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION','FIELD'])['TBD_FC_COUNT'].agg('sum').fillna(0).reset_index()
    tbdCntByFLD=pandas.DataFrame(tbdCntByFLD)
    tbdCntByFLD=tbdCntByFLD.query('TBD_FC_COUNT > 0')
    
    
    x = numpy.array(numpy.rec.fromrecords(tbdCntByFLD))
    names = tbdCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"TBDCellCountbyFLD")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)


    # FOR EACH FEATURE CLASS, GET COUNT OF CELLS THAT ARE OTHER
    ## THEN EXPORT THEM TO THE GEODATABASE
    otherCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION','FIELD'])['OTHER_FC_COUNT'].agg('sum').fillna(0).reset_index()
    otherCntByFLD=pandas.DataFrame(otherCntByFLD)
    otherCntByFLD=otherCntByFLD.query('OTHER_FC_COUNT > 0')

    x = numpy.array(numpy.rec.fromrecords(otherCntByFLD))
    names = otherCntByFLD.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"OtherCellCountbyFLD")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)
    
    




    # FOR EACH FEATURE CLASS GET TOTAL COUNTS OF DETERMINANT and INTEDETERMINANT (NULL + OTHER + TBD) VALUES, THEN PROPORTION OF DETERMINANT VALUES 

    indtCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['TOTAL_INDT_COUNT'].agg('sum').fillna(0).reset_index()
    indtCntByFLD=pandas.DataFrame(indtCntByFLD)

    detCntByFLD = pdNullTbl.groupby(['FDS','FC','INSTALLATION'])['TOTAL_DET_COUNT'].agg('sum').fillna(0).reset_index()
    detCntByFLD=pandas.DataFrame(detCntByFLD)
    
    indtDetCounts = detCntByFLD.join ( indtCntByFLD.set_index( [ 'FDS','FC','INSTALLATION'], verify_integrity=True ),
                   on=[ 'FDS','FC','INSTALLATION'], how='left' )

    indtDetCounts['PERCENT_DETERMINED_VALUES'] = indtDetCounts.TOTAL_DET_COUNT/(indtDetCounts.TOTAL_INTD_COUNT+indtDetCounts.TOTAL_DET_COUNT)
    

    
    x = numpy.array(numpy.rec.fromrecords(indtDetCounts))
    names = indtDetCounts.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"Determinant_Values_by_FC")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)


    ### FOR EACH FEATURE CLASS INCLUDED, HOW MANY ARE EMPTY? 
    emptyFCbyFDS=pdNullTbl.query("EMPTY_FC == 'T'").groupby(['FDS','FC','INSTALLATION']).size().reset_index()
    emptyFCbyFDS=pandas.DataFrame(emptyFCbyFDS)
    emptyFCbyFDS.columns = ['FDS','FC','INSTALLATION','TOTAL_EMPTY_FIELDS']

    x = numpy.array(numpy.rec.fromrecords(emptyFCbyFDS))
    names = emptyFCbyFDS.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"EmptyFeatureClasses")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)
    

    ### FOR EACH FEATURE CLASS INCLUDED, HOW MANY ARE EMPTY?
    emptyFCcnt = len(pdNullTbl.query("EMPTY_FC == 'T'").groupby(['FDS','FC','EMPTY_FC']).size().reset_index() )
    nonemptyFCcnt = len(pdNullTbl.query("EMPTY_FC == 'F'").groupby(['FDS','FC','EMPTY_FC']).size().reset_index() )
    installationName = os.path.splitext(os.path.basename(installGDB))[0]


    emptyFLDsum = emptyFCbyFDS.groupby(['INSTALLATION'])['TOTAL_EMPTY_FIELDS'].agg('sum').fillna(0).reset_index()
    emptyFLDsum = emptyFLDsum.iloc[0]['TOTAL_EMPTY_FIELDS']
    
    
    
    
    ### GET NUMBER OF MISSING FEATURE DATASETS
    missingFDScnt = pdFDSTbl.groupby(['FDS_MISSING','INSTALLATION']).ngroups
    
    ### GET NUMBER OF MISSING FEATURE CLASSES per FEATURE DATASET
    missingFCcnt = pdFCTbl.groupby(['FDS','FC_MISSING','INSTALLATION']).ngroups


    # BIND DATA INTO A PANDAS DATAFRAME
    d = {'Installation':[installationName],'MissingFDScount': [missingFDScnt], 'MissingFCcount': [missingFCcnt],'InclFeatsEmpty':[emptyFCcnt],'InclFeatsNonEmpty':[nonemptyFCcnt],'TotalMissingFields':[emptyFLDsum]}
    
    
    
    df = pandas.DataFrame(data=d)
    x = numpy.array(numpy.rec.fromrecords(df))
    names = df.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    gdbTbl = os.path.join(installGDB,"Overview")
    if arcpy.Exists(gdbTbl):
        arcpy.Delete_management(gdbTbl)
    arcpy.da.NumPyArrayToTable(x, gdbTbl)

# apply in parallel
Parallel(n_jobs=num_cores)(delayed(summariseComparisons)(installGDB) for installGDB in installationgdbList)

