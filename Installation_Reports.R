# References for automation 
# http://www.r-bloggers.com/how-to-source-an-r-script-automatically-on-a-mac-using-automator-and-ical/
# http://www.engadget.com/2013/03/18/triggering-applescripts-from-calendar-alerts-in-mountain-lion/

# File 1: Should be an R-Script 
# contains a loop that iteratively calls an Rmarkdown file (i.e. File 2)

setwd("C:\\Users\\stevenconnorg\\Documents\\knight-federal-solutions\\ViewerAttribution")


library(knitr)
library(markdown)
library(rmarkdown)
library(ggmap)
library(Rcpp)
library(sf)

# for each type of car in the data create a report
# these reports are saved in output_dir with the name specified by output_file

installationGDBs <- list.files(paste0(getwd(),"/gdbs"),full.names = T)
installationGDB<-installationGDBs[3]
for (installationGDB in installationGDBs){
  
  basename<-basename(installationGDB)
  installationName<-tools::file_path_sans_ext(basename)
  reportDir<-paste0(getwd(),"/Missing_Data_Reports/",installationName)
  dir.create(reportDir,recursive=TRUE,showWarnings = F)
  
  rmarkdown::render(input = paste0(getwd(),"/Installation_Reports.Rmd"),
          output_format = "pdf_document",
          output_file = paste0(installationName,"_Missing_Data_Report_",Sys.Date(),"_.pdf"),
          output_dir = reportDir)
  
}

