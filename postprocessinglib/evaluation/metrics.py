"""
The metrics module contains all of the metrics required during the prost processing process.
Each metric has a function and there are hepler functions that help with error checking and 
reading and preparation of data to be evaluated.  

"""

import numpy as np
import pandas as pd

from postprocessinglib.evaluation import preprocessing

def available_metrics() -> list[int]:
    """ Get a list of currently available metrics

    Returns
    -------
    List[str]
        List of implemented metric names.

    """
    metrics = [
        "MSE", "RMSE", "MAE", "NSE", "NegNSE", "LogNSE", "NegLogNSE",
        "KGE", "NegKGE", "KGE 2012", "BIAS", "AbsBIAS", "TTP", "TTCoM", "SPOD" 
    ]
    
    return metrics


def generate_dataframes(csv_fpath: str, num_min: int = 0, start_date :str = "",
                        end_date: str = "") -> tuple[pd.DataFrame, pd.DataFrame]:
    """ Function to Generate the required dataframes

    Parameters
    ----------
    csv_fpath : string
            the path to the csv file. It can be relative or absolute
    num_min: int 
            number of days required to "warm up" the system
    start_date: str 
            The date at which you want to start calculating the metric [yyyy-mm-dd]
    end_date: str
            The date at which you want the calculations to end [yyyy-mm-dd]

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        the observed dataframe, the simulated dataframe

    """

    if csv_fpath is not None:
        # read the csv into a dataframe making sure to account for unnecessary spaces.
        df = pd.read_csv(csv_fpath, skipinitialspace = True, index_col = ["YEAR", "JDAY"])
    
    # if there are any extra columns at the end of the csv file, remove them
    if len(df.columns) % 2 != 0:
        df.drop(columns=df.columns[-1], inplace = True) 

    # Take off the warm up time
    simulated = observed = df[num_min:].copy()
    simulated.drop(simulated.iloc[:, 0:], inplace=True, axis=1)
    observed.drop(observed.iloc[:, 0:], inplace=True, axis=1)
    for j in range(0, len(df.columns), 2):
        arr1 = df.iloc[num_min:, j]
        arr2 = df.iloc[num_min:, j+1]
        observed = pd.concat([observed, arr1], axis = 1)
        simulated = pd.concat([simulated, arr2], axis = 1)

    # splice the dataframes according to the time frame
    if not start_date and end_date:
        # there's an end date but no start date
        end_index = preprocessing.datetime_to_index(end_date)
        simulated = simulated.loc[:end_index]
        observed = observed.loc[:end_index]
    elif not end_date and start_date:
        # there's and end date but no start date
        start_index = preprocessing.datetime_to_index(start_date)
        simulated = simulated.loc[start_index:]
        observed = observed.loc[start_index:]
    elif start_date and end_date:
        # there's a start and end date
        start_index = preprocessing.datetime_to_index(start_date)
        end_index = preprocessing.datetime_to_index(end_date)
        simulated = simulated.loc[start_index:end_index]
        observed = observed.loc[start_index:end_index]
    
    # validate inputs
    preprocessing.validate_data(observed, simulated)
    
    return observed, simulated


def station_dataframe(observed: pd.DataFrame, simulated: pd.DataFrame,
               station_num: int) -> pd.DataFrame:
    """ Extracts a stations data from the observed and simulated 

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    station_num: List[int]
            array containing the index of the particular stations(s)

    Returns
    -------
    pd.DataFrames:
            The station(s) observed and simulated data

    """

    # validate inputs
    preprocessing.validate_data(observed, simulated)
    print("okay")

    Stations = []
    if station_num <= observed.columns.size:
        for j in range(0, station_num):
            station_df =  observed.copy()
            station_df.drop(station_df.iloc[:, 0:], inplace=True, axis=1)
            station_df = pd.concat([station_df, observed.iloc[:, j], simulated.iloc[:, j]], axis = 1)
            Stations.append(station_df)
        return Stations


def mse(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int) -> float:
    """ Calculates the Mean Square value of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    float:
        the mean square value of the data

    """     
    # validate inputs
    preprocessing.validate_data(observed, simulated)

    MSE = []    
    for j in range(0, num_stations):
        # Remove the invalid values from that station
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)        
    
        summation = np.sum((abs(valid_observed.iloc[:, j] - simulated.iloc[:, j]))**2)        
        mse = summation/len(valid_observed)  #dividing summation by total number of values to obtain average    
        MSE.append(mse)
    
    return MSE


def rmse(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int,
        num_min: int=0) -> float:
    """ Calculates the Root Mean Square value of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    float:
        the root mean square value of the data

    """   
    # validate inputs
    preprocessing.validate_data(observed, simulated)
    
    RMSE =[]
    for j in range(0, num_stations):
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        summation = np.sum((abs((valid_observed.iloc[:, j]) - simulated.iloc[:, j]))**2)
        rmse = np.sqrt(summation/len(valid_observed)) #dividing summation by total number of values to obtain average    
        RMSE.append(rmse)    

    return RMSE


def mae(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int) -> float:
    """ Calculates the Mean Average value of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    float:
        the mean average value of the data

    """
    # validate inputs
    preprocessing.validate_data(observed, simulated)
    
    MAE = []
    for j in range(0, num_stations): 
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        summation = np.sum(abs(valid_observed.iloc[:, j] - simulated.iloc[:, j]))
        mae = summation/len(valid_observed)  #dividing summation by total number of values to obtain average   
        MAE.append(mae)
    
    return MAE


def nse(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int) -> float:
    """ Calculates the Nash-Sutcliffe Efficiency of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    float:
        the Nash-Sutcliffe Efficiency of the data

    """       
    # validate inputs
    preprocessing.validate_data(observed, simulated)

    NSE = []
    for j in range(0, num_stations):  
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        num_valid = len(valid_observed.iloc[:, j])
        observed_mean = np.sum(valid_observed.iloc[:, j])
        observed_mean = observed_mean/num_valid

        summation_num = np.sum((abs(valid_observed.iloc[:, j] - simulated.iloc[:, j]))**2)
        summation_denom = np.sum((abs(valid_observed.iloc[:, j] - observed_mean))**2)
        
        nse = (1 - (summation_num/summation_denom))  #dividing summation by total number of values to obtain average
        NSE.append(nse)
        
    return NSE

def lognse(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int) -> float:
    """ Calculates the Logarithmic Nash-Sutcliffe Efficiency of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    float:
        the Logarithmic Nash-Sutcliffe Efficiency of the data

    """       
    # validate inputs
    preprocessing.validate_data(observed, simulated)

    LOGNSE = []
    for j in range(0, num_stations):  
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        num_valid = len(valid_observed.iloc[:, j])
        observed_mean = np.sum(np.log(valid_observed.iloc[:, j]))
        observed_mean = observed_mean/num_valid

        summation_num = np.sum((abs(np.log(valid_observed.iloc[:, j]) - np.log(simulated.iloc[:, j])))**2)
        summation_denom = np.sum((abs(np.log(valid_observed.iloc[:, j]) - observed_mean))**2)
        
        lognse = (1 - (summation_num/summation_denom))  #dividing summation by total number of values to obtain average
        LOGNSE.append(lognse)
        
    return LOGNSE


def kge(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int,
             scale: list[float]=[1. ,1. ,1.]) -> float:
    """ Calculates the Kling-Gupta Efficiency of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data
    scale: list[float, float, float]
            Scale factor for correlation[0], alpha[1], and beta[2] components 
            in the calculation of KGE

    Returns
    -------
    float:
        the Kling-Gupta Efficiency of the data

    """
    # validate inputs
    preprocessing.validate_data(observed, simulated)

    KGE = []
    for j in range(0, num_stations): 
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        num_valid = len(valid_observed.iloc[:, j])
        mean_observed = np.sum(valid_observed.iloc[:, j]) 
        mean_simulated = np.sum(simulated.iloc[:, j][valid_observed.iloc[:, j].index])
        mean_observed = mean_observed / num_valid
        mean_simulated = mean_simulated / num_valid
        
        
        std_observed = np.sum((valid_observed.iloc[:, j] - mean_observed)**2) 
        std_simulated = np.sum((simulated.iloc[:, j][valid_observed.iloc[:, j].index] - mean_simulated)**2)
        sum = np.sum((valid_observed.iloc[:, j] - mean_observed) * (simulated.iloc[:, j] - mean_simulated))
        
        # r: Pearson's Correlation Coefficient
        r = sum / np.sqrt(std_simulated * std_observed)
        
        std_observed = np.sqrt(std_observed/(num_valid - 1))
        std_simulated = np.sqrt(std_simulated/(num_valid - 1))

        # a: A term representing the variability of prediction errors,
        # b: A bias term
        b = mean_simulated / mean_observed
        a = std_simulated / std_observed
        
        kge = 1 - np.sqrt((scale[0]*(r - 1))**2 + (scale[1]*(a - 1))**2 + (scale[2]*(b - 1))**2)
        KGE.append(kge)
    
    return KGE


def kge_2012(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int,
             scale: list[float]=[1. ,1. ,1.]) -> float:
    """ Calculates the Kling-Gupta Efficiency of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data
    scale: list[float, float, float]
            Scale factor for correlation[0], alpha[1], and beta[2] components 
            in the calculation of KGE

    Returns
    -------
    float:
        the Kling-Gupta Efficiency of the data

    """
    # validate inputs
    preprocessing.validate_data(observed, simulated)

    KGE = []
    for j in range(0, num_stations):
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        num_valid = len(valid_observed.iloc[:, j])
        mean_observed = np.sum(valid_observed.iloc[:, j]) 
        mean_simulated = np.sum(simulated.iloc[:, j][valid_observed.iloc[:, j].index])
        mean_observed = mean_observed / num_valid
        mean_simulated = mean_simulated / num_valid
        
        
        std_observed = np.sum((valid_observed.iloc[:, j] - mean_observed)**2) 
        std_simulated = np.sum((simulated.iloc[:, j][valid_observed.iloc[:, j].index] - mean_simulated)**2)
        sum = np.sum((valid_observed.iloc[:, j] - mean_observed) * (simulated.iloc[:, j] - mean_simulated))
        
        # r: Pearson's Correlation Coefficient
        r = sum / np.sqrt(std_simulated * std_observed)
        
        std_observed = np.sqrt(std_observed/(num_valid - 1))
        std_simulated = np.sqrt(std_simulated/(num_valid - 1))

        # a: A term representing the variability of prediction errors,
        # b: A bias term
        b = mean_simulated / mean_observed
        a =  (std_simulated/ mean_simulated)/(std_observed / mean_observed)
        
        kge = 1 - np.sqrt((scale[0]*(r - 1))**2 + (scale[1]*(a - 1))**2 + (scale[2]*(b - 1))**2)
        KGE.append(kge)
    
    return KGE


def bias(observed: pd.DataFrame, simulated: pd.DataFrame, num_stations: int) -> float:
    """ Calculates the Percentage Bias of the data

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    float:
        the Percentage Bias of the data

    """    
    # validate inputs
    preprocessing.validate_data(observed, simulated)
    
    BIAS = []
    for j in range(0, num_stations):   
        # Remove the invalid values from that station 
        valid_observed = preprocessing.filter_valid_data(observed.iloc[:], station_num = j, remove_neg = True)
        
        bias = np.sum(simulated.iloc[:, j] - valid_observed.iloc[:, j])/np.sum(abs(valid_observed.iloc[:, j])) * 100
        BIAS.append(bias)
    
    return BIAS
        

def time_to_peak(df: pd.DataFrame, num_stations: int)->float:
    """ Calculates the time to peak of a given series of data whether observed 
        or simulated

    Parameters:
    -----------
    df: pd.DataFrame
            the observed or simulated dataframe

    num_stations: int
            number of stations in the data

    Returns:
    --------
    int:
        the average time to peak value of the given data
    
    """
    TTP = []
    last_year = df.index[-1][0]
    for j in range(0, num_stations):
        year = df.index[0][0]
        first = 0
        yearly_ttp = []
        while year != last_year:
            # check the number of days
            num_of_days = 365
            if preprocessing.is_leap_year(year):
                num_of_days = 366
            
            valid_values = np.sum(np.fromiter((df.index[i][0] == year for i in range(first, num_of_days+first)), int))
            
            if valid_values > 200 and np.sum(df.iloc[first:num_of_days+first, j]) > 0.0:
                peak_day = np.argmax(df.iloc[first:num_of_days+first, j]) + 1
                yearly_ttp.append(peak_day)
            first += valid_values
            year += 1
        ttp = np.mean(yearly_ttp)
        TTP.append(ttp)
    return TTP

def time_to_centre_of_mass(df: pd.DataFrame, num_stations: int)->float:
    """ Calculates the time it takes to obtain 50% of the stream flow in a given year

    Parameters:
    -----------
    df: pd.DataFrame
            the observed or simulated dataframe

    num_stations: int
            number of stations in the data

    Returns:
    --------
    int:
        the average time to the centre of mass for the station
    """
    TTCoM = []
    last_year = df.index[-1][0]
    for j in range(0, num_stations):
        year = df.index[0][0]
        first = 0
        yearly_ttcom = []
        while year != last_year:
            # check the number of days
            num_of_days = 365
            if preprocessing.is_leap_year(year):
                num_of_days = 366

            valid_values = np.sum(np.fromiter((df.index[i][0] == year for i in range(first, num_of_days+first)), int))
            
            if valid_values > 200 and np.sum(df.iloc[first:num_of_days+first, j]) > 0.0:
                CoM = np.sum(np.arange(1, num_of_days+1) * df.iloc[first:num_of_days+first, j])
                CoM = CoM / np.sum(df.iloc[first:num_of_days+first, j])
                yearly_ttcom.append(CoM)
            first += valid_values
            year += 1
        ttcom = np.mean(yearly_ttcom)
        TTCoM.append(ttcom)
    return TTCoM

def SpringPulseOnset(df: pd.DataFrame, num_stations: int)->int:
    """ Calculates when spring start i.e., the beginning of snowmelt

    Parameters:
    -----------
    df: pd.DataFrame
            the observed or simulated dataframe

    num_stations: int
            number of stations in the data

    Returns:
    --------
    int:
        the average time it takes till when snowmelt begins 
    """
    SPOD = []
    last_year = df.index[-1][0]
    for j in range(0, num_stations):
        year = df.index[0][0]
        first = 0
        yearly_spod = []
        while year != last_year:
            # check the number of days
            num_of_days = 365
            if preprocessing.is_leap_year(year):
                num_of_days = 366

            valid_values = np.sum(np.fromiter((df.index[i][0] == year for i in range(first, num_of_days+first)), int))

            if valid_values > 200 and np.sum(df.iloc[first:num_of_days+first, j]) > 0.0:
                mean = np.mean(df.iloc[first:num_of_days+first, j])
                minimum_cumulative = 1.0E38         # Some Arbitrarily large number
                cumulative = 0
                onset_day = 0
                for index in range(first, num_of_days+first):
                    cumulative += (df.iloc[index, j] - mean)
                    if cumulative < minimum_cumulative:
                        minimum_cumulative = cumulative
                        onset_day = (index % num_of_days) + 1
                yearly_spod.append(onset_day)
            first += valid_values
            year += 1          
        print("\n")
        spod = np.mean(yearly_spod)
        SPOD.append(spod)
    return SPOD


def calculate_all_metrics(observed: pd.DataFrame, simulated: pd.DataFrame,
                          num_stations: int) -> dict[str: float]:
    """Calculate all metrics.

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    num_stations: int
            number of stations in the data

    Returns
    -------
    dict{str: float}
            A dictionary containing every metric that can be evaluated and
            its result 
            
    """
    # validate inputs
    preprocessing.validate_data(observed, simulated)
    parameters = (observed, simulated, num_stations)

    preprocessing.check_valid_dataframe(observed, simulated)

    results = {
        "MSE" : mse(*parameters),
        "RMSE" : rmse(*parameters),
        "MAE" : mae(*parameters),
        "NSE" : nse(*parameters),
        "NegNSE" : [-x for x in nse(*parameters)],
        "LogNSE" : lognse(*parameters),
        "NegLogNSE" : [-x for x in lognse(*parameters)],
        "KGE" : kge(*parameters),
        "NegKGE" : [-x for x in kge(*parameters)],
        "KGE 2012" : kge_2012(*parameters),
        "BIAS" : bias(*parameters),
        "AbsBIAS" : list(map(abs, bias(*parameters))), 
        "TTP_obs" : time_to_peak(observed, num_stations),
        "TTP_sim" : time_to_peak(simulated, num_stations),
        "TTCoM_obs" : time_to_centre_of_mass(observed, num_stations),
        "TTCoM_sim" : time_to_centre_of_mass(simulated, num_stations),
        "SPOD_obs" : SpringPulseOnset(observed, num_stations),
        "SPOD_sim" : SpringPulseOnset(simulated, num_stations),
    }

    return results

def calculate_metrics(observed: pd.DataFrame, simulated: pd.DataFrame, metrices: list[str],
                      num_stations: int) -> dict[str, float]:
    """Calculate the requested metrics.

    Parameters
    ---------- 
    observed: pd.DataFrame
            Observed values[1: Day of the year; 2: Streamflow Values]
    simulated: pd.DataFrame
            Simulated values[1: Day of the year; 2: Streamflow Values]
    metrices: List[str]
            List of metrics to be calculated
    num_min: int 
            number of days required to "warm up" the system

    Returns
    -------
    dict{str: float}
            A dictionary containing each metric to be evaluated and its result 
            
    """
    # validate inputs
    preprocessing.validate_data(observed, simulated)
    parameters = (observed, simulated, num_stations)

    if "all" in metrices:
        return calculate_all_metrics(*parameters)
    
    preprocessing.check_valid_dataframe(observed, simulated)

    values = {}
    for metric in metrices:
        if metric.lower() ==  "mse":
            values["MSE"] = mse(*parameters)
        elif metric.lower() ==  "rmse":
            values["RMSE"] = rmse(*parameters)
        elif metric.lower() ==  "mae":
            values["MAE"] = mae(*parameters)
        elif metric.lower() ==  "nse":
            values["NSE"] = nse(*parameters)
        elif metric.lower() ==  "negnse":
            values["NegNSE"] = [-x for x in nse(*parameters)]
        elif metric.lower() ==  "lognse":
            values["LogNSE"] = lognse(*parameters)
        elif metric.lower() ==  "neglognse":
            values["NegLogNSE"] = [-x for x in lognse(*parameters)]
        elif metric.lower() ==  "kge":
            values["KGE"] = kge(*parameters)
        elif metric.lower() ==  "negkge":
            values["NegKGE"] = [-x for x in kge(*parameters)]
        elif metric.lower() ==  "kge 2012":
            values["KGE 2012"] = kge_2012(*parameters)
        elif metric.lower() ==  "bias":
            values["BIAS"] = bias(*parameters)
        elif metric.lower() == "pbias":
            values["BIAS"] = bias(*parameters)
        elif metric.lower() ==  "absbias":
            values["AbsBIAS"] = list(map(abs, bias(*parameters))),
        elif metric.lower() == "ttp_obs":
            values["TTP_obs"] = time_to_peak(observed, num_stations)
        elif metric.lower() == "ttp_sim":
            values["TTP_sim"] = time_to_peak(simulated, num_stations)
        elif metric.lower() == "ttcom_obs":
            values["TTCoM_obs"] = time_to_centre_of_mass(observed, num_stations)
        elif metric.lower() == "ttcom_sim":
            values["TTCoM_sim"] = time_to_centre_of_mass(simulated, num_stations)
        elif metric.lower() == "spod_obs":
            values["SPOD_obs"] = SpringPulseOnset(observed, num_stations)
        elif metric.lower() == "spod_sim":
            values["SPOD_sim"] = SpringPulseOnset(simulated, num_stations)
        else:
            raise RuntimeError(f"Unknown metric {metric}")
        

    return values
