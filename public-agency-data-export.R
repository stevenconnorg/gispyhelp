###############################
### author: steven c gonzalez
### date: 7/26/2017
### title: geodatabase feature classes to shapes
### description: generating public and agency versions of parcel shapefiles
###############################

# install required packages, not required if already installed
install.packages("rgdal",repos='https://cran.revolutionanalytics.com/')
install.packages("RODBC",repos='https://cran.revolutionanalytics.com/')
require(RODBC)
require(rgdal)
require(sp)
###############################
### define inputs inside quotation marks
###############################
year<-format(Sys.Date(), "%Y") 					# get current year for later
md<-format(Sys.Date(), "%b_%d") 
mainDir<-"\\\\bcad90\\gis\\GIS_DATA\\GIS_Public_Data\\"	# main directory - in BCAD90/gis/GIS_DATA/GIS_Public_Data/
subDir_pub<-paste0(year,"_","GIS_Public_Data")   		# make subdirectories for Public Data in GIS_Public_Data directory
subDir_agency<-paste0(year,"_","GIS_Agency_Data")		# make subdirectories for Agency  Data in GIS_Public_Data directory

agncy_dir<-paste0(mainDir,subDir_agency)     			# assign directory of agency GIS data
pub_dir<-paste0(mainDir,subDir_pub)       			# assign directory for public GIS data

dir.create(path=agncy_dir)						# create public and agency data folders in public data directories
dir.create(path=pub_dir)						# if already created, it will throw error

fgdb_name<-"\\BCAD_2017.gdb" 						# what is the geodatabase name with the parcel layer you'd like to export from?

fgdb <- paste0(agncy_dir,fgdb_name)  		 		# the original geodatabase with the parcels will be in the agency dir (unfiltered)

## List all feature classes in a file geodatabase
subset(ogrDrivers(), grepl("GDB", name))
fc_list <- ogrListLayers(fgdb)  					# create list of layers in fgdb
print(fc_list) 					 			# list objects / fgdb feature classes


parcel_name<-"Parcels_without_attributes" 			# what is the parcel layer name within the aforementioned file geodatabase


cn<-odbcDriverConnect(							# make SQL server connection for IS data table
		connection="Driver=				
			{SQL Server Native Client 11.0};
 		server=xxxxxx;
 		database=xxxxxxx;
		Uid=xxxxxx;
 		Pwd=xxxxxxx;")



# view contents of database connection
sqlTables(cn)

tablename<- "vw015_GIS_publicdata"						# input table name of PID attributes from IS

###############################
### just run after this line 
###############################

parcels_stage <- readOGR(dsn=fgdb,layer=parcel_name)  		# Read the parcels layer
atts<-sqlFetch(cn,tablename,rows_at_time=10000,as.is=TRUE)
head(atts)
summary(atts)

??sqlFetch
parcels<-parcels_stage
colnames(parcels@data)
colnames(atts)

parcels@data = data.frame(parcels_stage@data, atts[match(parcels@data[,"prop_id"], atts[,"PropID"]),])


# set NA values in confidential_flag column to FALSE
parcels@data$confidential_flag[is.na(parcels@data$confidential_flag)] <- 'F'

# set NA values throughout dataframe to character string "NA"
parcels@data[is.na(parcels@data)] <- "NA"

# make public and agency parcels from parcels
agency_parcels <- parcels
pub_parcels<-agency_parcels


str(pub_parcels@data)
# make rows empty for following columns where confidential flag column = TRUE

pub_parcels@data$Owner[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$Situs[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$AddrLn1[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$AddrLn2[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$AddrCity[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$AddrSt[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$Country[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$Zip[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$Zip4[pub_parcels@data$confidential_flag=='T']=''
pub_parcels@data$DBA[pub_parcels@data$confidential_flag=='T']=''


dim(parcels@data[parcels@data$confidential_flag=='T',])

### drop confidential column
drops <- c("confidential_flag")
pub_parcels@data<-pub_parcels@data[ , !(names(pub_parcels@data) %in% drops)]
colnames(pub_parcels@data)


# write agency shapefile to agency directory and public shapefile to public directory
writeOGR(agency_parcels, driver="ESRI Shapefile",dsn=agncy_dir, layer=paste0("BCAD_",year,"_","Agency_Parcels_with_Attributes","_",md),overwrite=TRUE)
writeOGR(pub_parcels, driver="ESRI Shapefile",dsn=pub_dir, layer=paste0("BCAD_",year,"_","Public_Parcels_with_Attributes","_",md),overwrite=TRUE)



