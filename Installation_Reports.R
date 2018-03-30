# References for automation 
# http://www.r-bloggers.com/how-to-source-an-r-script-automatically-on-a-mac-using-automator-and-ical/
# http://www.engadget.com/2013/03/18/triggering-applescripts-from-calendar-alerts-in-mountain-lion/

# File 1: Should be an R-Script 
# contains a loop that iteratively calls an Rmarkdown file (i.e. File 2)


### use packrat for package management
setwd("C:\\Users\\stevenconnorg\\Documents\\knight-federal-solutions\\Installation_Feedback")
#library(packrat)
#packrat::init(options = list(ignored.packages = c("RgoogleMaps","rprojroot","dunits","proto","rgdal","jpeg")))
packrat::opts$ignored.packages(c("RgoogleMaps","dunits","proto","rgdal","jpeg"))
#packrat::snapshot()
#packrat::status()
#packrat::clean() 
#packrat::snapshot()


library(knitr)
library(markdown)
library(rmarkdown)
library(ggmap)
library(Rcpp)
library(sf)

# for each type of car in the data create a report
# these reports are saved in output_dir with the name specified by output_file

installationGDBs <- list.files(paste0(getwd(),"/gdbs"),full.names = T)
targetGDBs <- list.files(paste0(getwd(),"/gdbs-target"),full.names = T)

installationGDBs<-installationGDBs[1:7]
targetGDBs<-targetGDBs[1]

for (installationGDB in installationGDBs){
  for (targetGDB in targetGDBs){
    
    tbasename<-basename(targetGDB)
    compName<-tools::file_path_sans_ext(tbasename)
    
    basename<-basename(installationGDB)
    installationName<-tools::file_path_sans_ext(basename)
    
    reportDir<-paste0(getwd(),"/Missing_Data_Reports/",installationName)
    dir.create(reportDir,recursive=TRUE,showWarnings = F)
    
    rmarkdown::render(input = paste0(getwd(),"/Installation_Reports.Rmd"),
            output_format = "pdf_document",
            output_file = paste0(installationName,"_Missing_Data_Report_",compName,"_",Sys.Date(),".pdf"),
            output_dir = reportDir)
  }
}

# R version 3.4.1 (2017-06-30)
# Platform: x86_64-w64-mingw32/x64 (64-bit)
# Running under: Windows >= 8 x64 (build 9200)
# 
# Matrix products: default
# 
# locale:
#   [1] LC_COLLATE=English_United States.1252  
# LC_CTYPE=English_United States.1252    
# LC_MONETARY=English_United States.1252
# LC_NUMERIC=C
# LC_TIME=English_United States.1252    
# 
# attached base packages:
#   [1] stats     graphics  grDevices utils     datasets  methods   base     
# 
# loaded via a namespace (and not attached):
#   [1] compiler_3.4.1 tools_3.4.1    yaml_2.1.14   
