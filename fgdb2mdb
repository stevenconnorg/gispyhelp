import os  
  
fgdb =   sys.argv[0]       #full path to existing file geodatabase  
pgdb_dir = sys.argv[1]     #folder to hold personal geodatabase  
pgdb_name =  sys.argv[2]   #name of personal geodatabase, excluding extension  
  
pgdb = arcpy.CreatePersonalGDB_management(pgdb_dir, pgdb_name)  
pgdb = pgdb.__str__()  #extract geodatabase string value for os.path.join  
  
gdb, fds, fcs = next(arcpy.da.Walk(fgdb))  
for i in fds + fcs:  
    arcpy.Copy_management(os.path.join(gdb,i), os.path.join(pgdb, i))  
