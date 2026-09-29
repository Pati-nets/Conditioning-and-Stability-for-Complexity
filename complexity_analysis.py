import datetime # to infer artificial timestamps if needed
from feeed import extract_features # for calculating the scores of log measures
import os # for finding .xes files on the file system
import pandas # for handling collections of log complexity data
import pm4py # for importing Petri nets from PNML
from time import time # to stop time during measure calculations

import Constants # to know where to look for input and where to export output
import PetriNet # for the internal representation of Petri nets

def collect_log_measure_data(measures: list, input_path: str):
    """
    Collects the complexity scores for all of the measures passed in a list.
    This function goes through all .xes files in the path specified at
    input_path, imports the .xes file using the library pm4py, and
    adds the complexity scores of the event log to a panda DataFrame.
    The resulting table of complexity scores is automatically stored in a .csv
    file found at the path specified by Constants.OUTPUT_PATH. Furthermore, the
    resulting panda DataFrame is returned alongside the number of imported
    .xes files.

    Parameters
    ----------
    measures : list
        the list of measures whose complexity score should be calculated
    input_path: str
        a path to a folder containing .xes files

    Returns
    -------
    DataFrame
        a panda DataFrame whose header contains the names of the specified
        complexity measures, and where each row contains the complexity scores
        according to these measures for one of the .xes files located at the
        folder specified in input_path
    int
        the number of event logs that were imported from input_path
        and whose complexity scores were calculated
    """
    header = measures
    collected_data = []
    filenames = []
    iteration = 1
    for file in os.listdir(input_path):
        # make sure that we only consider event log files in XES format.
        full_file_path = os.path.join(input_path, file)
        if os.path.isfile(full_file_path) and file.endswith(".xes") and not file.startswith("."):
            filenames += [str(os.path.basename(file))]
            # infer timestamps to the event log if necessary
            from pm4py.objects.log.importer.xes import importer as xes_importer
            log = xes_importer.apply(full_file_path)
            export = False
            for trace in log:
                for event in trace:
                    if 'time:timestamp' not in event.keys():
                        event['time:timestamp'] = datetime.datetime.now()
                        export = True
            if export:
                from pm4py.objects.log.exporter.xes import exporter as xes_exporter
                xes_exporter.apply(log, full_file_path)
            # calculate the complexity scores
            complexity_scores = extract_features(full_file_path, measures)
            data = []
            for measure in header:
                data += [complexity_scores[measure]]
            collected_data += [data]
            iteration += 1
    complexity = pandas.DataFrame(collected_data, index=filenames, columns=header)
    complexity.to_csv(Constants.OUTPUT_PATH + "log_complexity_scores.csv", mode='w', encoding='utf-8')
    return complexity, iteration-1

def collect_model_complexity_data(measures: list, input_path: str):
    """
    Collects the complexity scores for all of the measures passed in a list.
    This function goes through all .pnml files in the path specified at
    input_path, imports the .xes file using the library pm4py, and
    adds the complexity scores of the event log to a panda DataFrame.
    The resulting table of complexity scores is automatically stored in a .csv
    file found at the path specified by Constants.OUTPUT_PATH. Furthermore, the
    resulting panda DataFrame is returned alongside the number of imported
    .pnml files.

    Parameters
    ----------
    measures : list
        the list of measures whose complexity score should be calculated
    input_path: str
        a path to a folder containing .pnml files

    Returns
    -------
    DataFrame
        a panda DataFrame whose header contains the names of the specified
        complexity measures, and where each row contains the complexity scores
        according to these measures for one of the .pnml files located at the
        folder specified in input_path
    int
        the number of Petri net models that were imported from input_path
        and whose complexity scores were calculated
    """
    header = measures
    collected_data = []
    filenames = []
    iteration = 1
    for file in os.listdir("./ReliabilityData/models"):
        # make sure that we only consider event log files in XES format.
        full_file_path = os.path.join("./ReliabilityData/models", file)
        if os.path.isfile(full_file_path) and file.endswith(".pnml") and not file.startswith("."):
            print("Startin iteration", iteration)
            filenames += [str(os.path.basename(file))]
            model, im, fm = pm4py.read_pnml(full_file_path)
            pn = PetriNet.transform_to_petri_net(model, im, fm)
            data = []
            for i in range(len(measures)):
                start_time = time()
                complexity = eval('pn.' + measures[i] + '()')
                data += [complexity]
                end_time = time()
                elapsed_time = end_time - start_time
                print("INFO:", full_file_path, "calculating", measures[i], "(" + str(complexity) + ")", f"took {elapsed_time:.2f} milliseconds.", end='')
                if i < len(measures) - 1:
                    print("Next measure:", measures[i+1])
                else:
                    print("This was the last measure.")
            collected_data += [data]
            iteration += 1
    complexity = pandas.DataFrame(collected_data, index=filenames, columns=header)
    complexity.to_csv(Constants.OUTPUT_PATH + "model_complexity_scores.csv", mode='w', encoding='utf-8')
    return complexity, iteration-1

def prepare_data_for_analysis(csv_to_log_complexity: str, csv_to_model_complexity: str, log_measure: str, mod_measure: str, miner: str, as_dict = False):
    """
    Prepares complexity data for conditioning and stability analysis.
    It takes two paths to .csv files as input. The first one must
    contain complexity data for the event logs that should be analyzed.
    The second one must contain complexity data for the models that
    should be analyzed.
    Since this function was created for the Reliability Data published by
    Anandi Karunaratne, Artem Polyvyanyy, and Alistair Moffat, the code
    assumes that the original event logs have names such as
    Sepsis_1000.xes
    while noise derivates of these event logs are called
    Sepsis_1000_MIXED_0.1_1.xes,
    Sepsis_1000_ABSENCE_0.1_1.xes,
    Sepsis_1000_ORDERING_0.1_1.xes,
    and so on.

    Parameters
    ----------
    csv_to_log_complexity : str
        the path to a .csv file that contains log complexity data
    csv_to_model_complexity : str
        the path to a .csv file that contains model complexity data
    log_measure: str
        the name of the log complexity measure that should be analyzed
    mod_measure: str
        the name of the model complexity measure that should be analyzed
    miner: str
        the name of the discovery algorithm used to automatically discovery
        the .pnml files whose complexity scores are contained in the second
        .csv file. The name of these .pnml files must end with this string.
    as_dict: bool
        a boolean that decides whether the resulting table should be returned
        as a dict with one Pandas DataFrame per original log or if these
        DataFrames should be concatenated and returned as a single DataFrame.

    Returns
    -------
    DataFrame / dict
        if the boolean as_dict is true, this function returns a dictionary
        of DataFrames. Each DataFrame contains the normalized distances of
        the log complexity scores (under the column dl) and the normalized
        distances of the model complexity scores (under the column dm).
        If as_dict is false, this function returns these data in a single
        DataFrame instead.
    """
    # import complexity data from the provided .csv files
    log_complexity = pandas.read_csv(csv_to_log_complexity, index_col=0)
    mod_complexity = pandas.read_csv(csv_to_model_complexity, index_col=0)
    # get a list of base logs without noise, e.g., Sepsis_1000.xes. These logs feature only one '_' symbol in their name.
    base_logs = [row.name for index, row in log_complexity.iterrows() if len(row.name.split("_")) <= 2]
    distance_info = dict()
    # go through all of the collected base logs
    for base_log in base_logs:
        dist_dict = dict()
        base_name = base_log.removesuffix('.xes')
        C_system = log_complexity.loc[base_log][log_measure]
        # iterate through all logs in the imported table
        for index, row in log_complexity.iterrows():
            if row.name.startswith(base_name):
                # only consider the current event log if it is a derivate of the current base log
                row_name = row.name.removesuffix('.xes')
                dist_dict[row_name] = dict()
                C_log = log_complexity.loc[row.name][log_measure]
                # calculate the normalized difference of the log complexity scores
                normalized_diff = abs(C_system - C_log) / C_log
                dist_dict[row_name]['dl'] = normalized_diff
        # next, find the complexity of the model for the current base log
        C_system_model = mod_complexity.loc[base_name + "_" + miner + ".pnml"][mod_measure]
        for index, row in mod_complexity.iterrows():
            # only consider the current model if it was constructed from a derivate from the current base log
            if row.name.startswith(base_name + "_") and row.name.endswith("_" + miner + ".pnml"):
                row_name = row.name.removesuffix("_" + miner + ".pnml")
                # ignore the model if the data is missing the event log it was discovered from
                if row_name in dist_dict.keys():
                    C_model = mod_complexity.loc[row.name][mod_measure]
                    # calculate the normalized difference of the model complexity scores
                    normalized_diff = abs(C_system_model - C_model) / C_model
                    dist_dict[row_name]['dm'] = normalized_diff
        # store the calculated table, but drop rows where a column contains NaN
        distance_info[base_name] = pandas.DataFrame.from_dict(dist_dict, orient='index').dropna()
    if as_dict:
        return distance_info
    else:
        return pandas.concat(list(distance_info.values()))
