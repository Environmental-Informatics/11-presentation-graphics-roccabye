#!/bin/env python
# Author: Alka Tiwari (purdue id: tiwari13)
# Github: https://github.com/Environmental-Informatics/11-presentation-graphics-roccabye
# Created on: April 24, 2020
# This program creates six plots for the foloowing USGS Streamgauge in central Indiana.
# USGS 03331500 TIPPECANOE RIVER NEAR ORA, IN
# USGS 03335000 WILDCAT CREEK NEAR LAFAYETTE, IN
# This program creates the figures for a oral presentation highlighting the differences between the two rivers 
# by plotting the metrics calculated in assignment 10

# important libraries
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
   
    # Gross error check for negative discharge values
    DataDF['Discharge'][(DataDF['Discharge']<0)]=np.nan
    
    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    
    # start date = October 1, 1969; enddate = September 30, 2019.
    # 50 water years of streamflow data for the analysis
    # clip the given streamflow timeseries for a given range of startdate to enddate
    DataDF = DataDF.loc[startDate:endDate]
    
    # quantifying the missing values 
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )
    
def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    
     # open and read the file
    DataDF = pd.read_csv(fileName, header=0, delimiter=',', parse_dates=['Date'])
    DataDF = DataDF.set_index('Date') # Set Date as index 
    
    return( DataDF )

# Figure 3.5 uses the functions GetMonthlyStatistics and GetMonthlyAverages
def GetMonthlyStatistics(DataDF):
    """This function calculates monthly descriptive statistics and metrics 
    for the given streamflow time series.  Values are returned as a dataframe
    of monthly values for each year."""
    
    # define column names for the dataframe
    colNames = ['site_no','Mean Flow','Coeff Var','Tqmean','R-B Index']
    
    # Monthly distribution of the streamflow timeseries.
    Month_dist = DataDF.resample('MS')
    
    # Creating dataframe of monthly descriptive statistics and metrics for the given streamflow time series
    data_monthly = Month_dist.mean()
    MoDataDF=pd.DataFrame(0,index=data_monthly.index,columns=colNames)
    
    # Providing statistics to fill the MoDataDF dataframe.
    # mean value of the site number
    MoDataDF['site_no']=Month_dist['site_no'].mean()
    
    # mean value of streamflow discharge 
    MoDataDF['Mean Flow']=Month_dist['Discharge'].mean()
    
    # coefficient of variation(st. deviation/mean) of streamflow discharge
    MoDataDF['Coeff Var']=(Month_dist['Discharge'].std()/Month_dist['Discharge'].mean())*100
     
    return ( MoDataDF )

def GetMonthlyAverages(MoDataDF):
    """This function calculates annual average monthly values for all 
    statistics and metrics.  The routine returns an array of mean values 
    for each metric in the original dataframe."""
     
    # define column names for the dataframe
    colNames = ['site_no','Mean Flow','Coeff Var','Tqmean','R-B Index']
    
    # Creating dataframe of annual average monthly values statistics and metrics 
    MonthlyAverages = pd.DataFrame(0,index = range(1,13),columns = colNames)
    
    # mean value of the site number of MoDataDF dataframe
    for j in range(0,12):
        MonthlyAverages.iloc[j,0]=MoDataDF['site_no'][::12].mean() 
    
    index = [(0,3),(1,4),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11),(9,0),(10,1),(11,2)]
        
    # Providing statistics to fill the MonthlyAverages dataframe
    for (j,i) in index:
        # mean of mean value of streamflow discharge from MoDataDF dataframe
        MonthlyAverages.iloc[j,1]=MoDataDF['Mean Flow'][i::12].mean()
       
        # mean value of the coefficient of variation (st. deviation/mean) of MoDataDF dataframe
        MonthlyAverages.iloc[j,2]=MoDataDF['Coeff Var'][i::12].mean()
        
        # mean of Tqmean of streamflow from ModataDF dataframe
        MonthlyAverages.iloc[j,3]=MoDataDF['Tqmean'][i::12].mean()
       
        # mean of RBIndex from the MoDataDF dataframe
        MonthlyAverages.iloc[j,4]=MoDataDF['R-B Index'][i::12].mean()
        
    return( MonthlyAverages )
    
# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }
    
    # directory for the USGS streamflow files for gauges Tippecanoe(1943 - 2020) and Wildcat Creek(1954-2020)
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    # Create blank directories where the values are being stored
    DataDF = {}
    MissingValues = {}
    MoDataDF = {}
    MonthlyAverages = {}
   
    for file in fileName.keys():
        #Read the data
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
        # Sort/Clip data
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '1969-10-01', '2019-09-30' ) 
        # Monthly metrics
        MoDataDF[file] = GetMonthlyStatistics(DataDF[file])
        #annual average monthly values for all statistics and metrics
        MonthlyAverages[file] = GetMonthlyAverages(MoDataDF[file]) 
    
    # Read the annual metric file created in Lab10 for Figure 3.2   
    Metrics_A = ReadMetrics('Annual_Metrics.csv')     
    # Sort data of annual metrics by the station name
    Tippe_A = Metrics_A[Metrics_A['Station']=='Tippe']
    Wildcat_A = Metrics_A[Metrics_A['Station']=='Wildcat']
    
    # FIGURE 3.1: Daily flow for both streams for the last 5 years of the record.

    Tippe_Clip = DataDF['Tippe']['2014-10-01' : '2019-09-30'] #last 5 years 
    Wildcat_Clip = DataDF['Wildcat']['2014-10-01' : '2019-09-30'] #Last 5 years
    # creating labels and legends
    plt.plot(Tippe_Clip['Discharge'], color='teal',label='Tippecanoe')
    plt.scatter(Wildcat_Clip.index,Wildcat_Clip['Discharge'], marker = '.', color='orangered',label='Wildcat')
    plt.xlabel('Date')
    plt.ylabel('Discharge (cfs)')
    plt.xticks(rotation=70)
    plt.title('Daily Flow for both rivers (2014 to 2019)')
    plt.rcParams.update({'font.size':12})
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('DailyFlow_5yr.png', dpi=96) 
    plt.show()
    
    # FIGURE3.2: Annual Coefficient of Variation (st. deviation/mean) of streamflow discharge
    plt.plot(Tippe_A['Coeff Var'],color='teal',label='Tippecanoe',linestyle='None',marker ='o')
    plt.plot(Wildcat_A['Coeff Var'],color='orangered',label='Wildcat',linestyle='None',marker = '<')
    plt.xlabel("Year")
    plt.ylabel("Coefficient of Variation")
    plt.title('Annual Coefficient of Variation')
    plt.rcParams.update({'font.size':12})
    plt.legend(loc='upper left', fontsize = 10)
    plt.savefig("COV_Annual.png",dpi=96)
    plt.show()
    
    
    # FIGURE3.3: Annual TQmean (fraction of time that daily streamflow exceeds mean streamflow for each year)
    
    plt.plot(Tippe_A['Tqmean'],'teal',label='Tippecanoe River',linestyle='None',marker ='o')
    plt.plot(Wildcat_A['Tqmean'],'orangered',label='Wildcat Creek',linestyle='None',marker = '<')
    plt.xlabel("Year")
    plt.ylabel("TQmean")
    plt.title('TQmean')
    plt.rcParams.update({'font.size':12})
    plt.legend(loc='best')
    plt.savefig("TQmean_Annual.png",dpi=96)
    plt.show()
    
    # FIGURE3.4:R-B index (sum of the absolute values of day-to-day changes in daily discharge 
    # volumes/total discharge volumes for each year)
    
    plt.plot(Tippe_A['R-B Index'],'teal',label='Tippecanoe River')
    plt.plot(Wildcat_A['R-B Index'],'orangered',label='Wildcat Creek')
    plt.xlabel("Year")
    plt.ylabel("R-B Index")
    plt.title('Annual R-B Index ')
    plt.rcParams.update({'font.size':12})
    plt.legend(loc='best')
    plt.savefig("R-B Index_Annual.png",dpi=96)
    plt.show()
    
    # FIGURE3.5: Average annual monthly flow; using functions GetMonthlyStatistics and GetMonthlyAverages
   
    plt.plot(MonthlyAverages['Tippe']['Mean Flow'],'teal',label='Tippecanoe River')
    plt.plot(MonthlyAverages['Wildcat']['Mean Flow'],'orangered',label='Wildcat Creek')
    plt.xticks(np.linspace(0,12,12), ('Jan', 'Feb', 'Mar', 'Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov', 'Dec'))
    plt.xlabel('Month of the Year')
    plt.ylabel('Discharge (cfs)')
    plt.title('Average Annual Monthly Flow')
    plt.rcParams.update({'font.size':12})
    plt.legend(loc='upper right')
    plt.savefig('Average_Monthly_Flow.png',dpi=96)
    plt.show()
    
    # FIGURE3.6:Return period of annual peak flow events
    # drop all other colums from metric file to choose only Peak Flow column

    dropfile_T = Tippe_A.drop(columns=['site_no', 'Mean Flow', 'Median Flow', 'Coeff Var', 'Skew', 'Tqmean', 'R-B Index', '7Q', '3xMedian'])
    dropfile_WC = Wildcat_A.drop(columns=['site_no', 'Mean Flow', 'Median Flow', 'Coeff Var', 'Skew', 'Tqmean', 'R-B Index', '7Q', '3xMedian'])
    
    # Sort Peak Flow from highest to lowest value.
    Sort_PK_T = dropfile_T.sort_values('Peak Flow', ascending=False) # For Tippecanoe
    Sort_PK_WC = dropfile_WC.sort_values('Peak Flow', ascending=False) # For Wildcat
    
    # Assigning rank from 1 to N. 
    Rank_PK_T = stats.rankdata(Sort_PK_T['Peak Flow'], method='average') # For Tippecanoe
    Rank_PK_WC = stats.rankdata(Sort_PK_WC['Peak Flow'], method='average') # For Wildcat

   # Reversing so that Rank 1 is the highest event, and rank N is the lowest event.
    Rank_T = Rank_PK_T[::-1] #For Tippecanoe
    Rank_WC = Rank_PK_WC[::-1] # For Wildcat
    
    # Calculate the plotting position (or exceedence probability) for each event 
    # using the Weibull plotting position equation: 
    #P(x)=m(x)/N+1, where m = rank of precipitation event x, and N = number of observations.
    # Multiply 100 in the equation to convert fraction probability to percentage probability.
    Exce_Prob_Tippe = [((Rank_T[i]/(len(Sort_PK_T)+1))) for i in range(len(Sort_PK_T))] # For Tippecanoe
    Exce_Prob_Wildcat = [((Rank_WC[i]/(len(Sort_PK_WC)+1))) for i in range(len(Sort_PK_WC))] # For Wildcat
    
    # Plot Return Period of Annual peak flow event
    plt.scatter(Exce_Prob_Tippe, Sort_PK_T['Peak Flow'],color='teal', label='Tippecanoe River',marker='o')
    plt.scatter(Exce_Prob_Wildcat, Sort_PK_WC['Peak Flow'], color='orangered', label='Wildcat Creek',marker='<')
    ax= plt.gca()
    ax.set_xlim(1,0) # Reverse the x axis from 1 to 0
    plt.xlabel('Exceedence Probability (%)')
    plt.ylabel('Peak Discharge (cfs)')
    plt.title('Return Period of Annual Peak Flow Events')
    plt.rcParams.update({'font.size':12})
    plt.legend(loc='best')
    plt.savefig('Exceedence Probability.png', dpi=96,bbox_inches='tight')   
    plt.show()
    
# The two watersheds drain very similar areas that are very close together 
# There is no significant difference in climate, and both watersheds have similar land use (dominated by agricultural use). 
# That should mean that their hydrologic response, measured as streamflow, should be similar. Are they?
# But they are not which is highlighted in the figures developed here.