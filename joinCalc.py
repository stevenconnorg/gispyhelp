import arcpy, os
from arcpy import env
env.overwriteOutput = True

#join table
joinFc =arcpy.GetParameterAsText(0)
#join key field
joinIdFld =arcpy.GetParameterAsText(1)
#join value field to be transferred
joinValFld=arcpy.GetParameterAsText(2)


#feature class to update
pointFc =arcpy.GetParameterAsText(3)
#update fc key field
IdFld =arcpy.GetParameterAsText(4)
#update field
updateFld =arcpy.GetParameterAsText(5)
whereClause=arcpy.GetParameterAsText(6)
checkedLeftstrip = arcpy.GetParameterAsText(7)
checkedRemoveBlanks = arcpy.GetParameterAsText(8)


#join key field
sourceRPSUID =arcpy.GetParameterAsText(9)


#join key field
updateRPSUID =arcpy.GetParameterAsText(10)

# remove leading zeros from destination join id field?
if checkedLeftstrip:
    with arcpy.da.UpdateCursor(pointFc,[IdFld]) as cursor:
            for row in cursor:
                row=[i.lstrip('0') for i in row]
                cursor.updateRow(row)
                
if checkedRemoveBlanks:
    with arcpy.da.UpdateCursor(pointFc,[IdFld]) as cursor:
        for row in cursor:
            row=[i.strip() if i is not None else None for i in row]
            cursor.updateRow(row)
        
def unique_values(table , field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({str(row[0]) for row in cursor})

myRPSUIDs = unique_values(pointFc, str(updateRPSUID))

for RPSUID in myRPSUIDs:
    # for RPSUID in myRPSUIDs:
    arcpy.AddMessage(RPSUID)
    tbl = os.path.join("in_memory","tbl")
    
    if arcpy.Exists(tbl):
        arcpy.Delete_management(tbl)
    arcpy.TableSelect_analysis(joinFc,tbl, where_clause=sourceRPSUID+' =' +RPSUID+" and "+joinValFld+ " "+whereClause)
    
	#create dictionary
	#Key: join field
	#Value: field with value to be transferred
    valueDi = dict([(key, val) for key, val in
    					 arcpy.da.SearchCursor
    					 (tbl, [joinIdFld, joinValFld])])
    
    
    # convert dictionary keys and values to update fc field types
    f1=arcpy.ListFields(pointFc, wild_card=updateFld)[0]
    f2=arcpy.ListFields(pointFc, wild_card=IdFld)[0]
    
    # convert dictionary values 
    if f1.type == "String":
         valueDi =  {k:str(v) for k, v in valueDi.iteritems()}
    if f1.type == "Short":
         valueDi =  {k:int(v) for k, v in valueDi.iteritems()}         
    elif f1.type == "Long":
         valueDi =  {k:float(v) for k, v in valueDi.iteritems()}  
    else:
        pass
    # convert dictionary keys 
    if f2.type == "String":
     valueDi =  {str(k):v for k, v in valueDi.iteritems()}
     
    if f2.type == "Short":
         valueDi =  {int(k):v for k, v in valueDi.iteritems()}         
    elif f2.type == "Long":
         valueDi =  {float(k):v for k, v in valueDi.iteritems()}  
    else:
        pass
    
    
    #update feature class
    with arcpy.da.UpdateCursor (pointFc, [updateFld, IdFld],where_clause=updateRPSUID+" = '"+RPSUID+"'") as cursor:
        for update, key in cursor:
    			#skip if key value is not in dictionary
            if not key in valueDi:
                continue
    			#create row tuple
            row = (valueDi [key], key)
            arcpy.AddMessage(row)
    			#update row
            cursor.updateRow (row)
            del row
    
    #arcpy.MakeLayer_management(pointFc,str(pointFc))
    #arcpy.JoinField_management (str(pointFc), updateFld, joinFc, joinValFld)
    
    
    del cursor
    arcpy.Delete_management(tbl)


