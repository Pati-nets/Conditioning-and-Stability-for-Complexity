import questionary # to ask the user for measures and discovery algorithms

import complexity_analysis # to calculate complexity scores and normalized distances
import complexity_conditioning # to calculate the conditioning of a discovery algorithm
import complexity_stability # to calculate the stability of a discovery algorithm

log_measures = ['n_events', # magnitude C_{mag}
                'n_unique_activities', # variety C_{var}
                'n_traces', # length C_{len}
                'trace_len_mean', # average trace length C_{TL-avg}
                'trace_len_max', # maximum trace length C_{TL-max}
                'number_of_ties', # number of ties C_{t-comp}
                'lempel_ziv_complexity', # Lempel-Ziv complexity C_{LZ}
                'n_variants', # number of distinct traces C_{DT-#}
                'ratio_variants_per_number_of_traces', # percentage of distinct traces C_{DT-%}
                'distinct_activities_mean', # structure C_{struct}
                'deviation_from_random', # deviation from random C_{dev-R}
                'epa_variant_entropy', # variant entropy C_{var-e}
                'epa_normalized_variant_entropy', # normalized variant entropy C_{nvar-e}
                'epa_sequence_entropy', # sequence entropy C_{seq-e}
                'epa_normalized_sequence_entropy' # normalized sequence entropy C_{nseq-e}
                ]

mod_measures = ['size', # size C_{size}
                'connector_mismatch', # connector mismatch C_{MM}
                'connector_heterogeneity', # connector heterogeneity C_{CH}
                'token_split', # token split C_{ts}
                'separability', # separability C_{sep}
                'control_flow_complexity', # control flow complexity C_{CFC}
                'average_connector_degree', # average connector degree C_{acd}
                'maximum_connector_degree', # maximum connector degree C_{mcd}
                'sequentiality', # sequentiality C_{seq}
                'cyclicity', # cyclicity C_{cyc}
                'density', # density C_{dens}
                'coefficient_of_network_connectivity', # coefficient of network connectivity C_{CNC}
                'number_of_duplicate_tasks', # number of duplicate tasks C_{dup}
                'empty_sequence_flows' # number of empty sequence flows C_{\emptyset}
                ]

discovery_algo = ['alpha', # Alpha Miner
                  'inductive', # Inductive Miner
                  'inductive_inf', # Inductive Miner Infrequent
                  'heuristics' # Heuristics Miner
                  ]

def ask_user_for_log_measure():
    question = "Please specify the log complexity measure you wish to analyze."
    response = questionary.select(question, choices=log_measures).ask()
    return response

def ask_user_for_model_measure():
    question = "Please specify the model complexity measure you wish to analyze."
    response = questionary.select(question, choices=mod_measures).ask()
    return response

def ask_user_for_discovery_algorithm():
    question = "Please specify the discovery algorithm you wish to analyze."
    response = questionary.select(question, choices=discovery_algo).ask()
    return response

if __name__ == "__main__":
    log_csv = "log_complexity_scores.csv"
    mod_csv = "model_complexity_scores.csv"
    print("Welcome to the analysis tool for conditioning and stability of ", end='')
    print("Complexity measures with respect do process discovery algorithms.\n")
    print("To begin, you first need to specify a log complexity measure.")
    log_measure = ask_user_for_log_measure()
    print("Now, we need a model complexity measure to evaluate the discovered Petri nets.")
    mod_measure = ask_user_for_model_measure()
    print("Okay! Now, please specify the discovery algorithm you want to analyze.")
    miner = ask_user_for_discovery_algorithm()
    print("I will now calculate the log and model distances based on ", end='')
    print("the data provided in " + log_csv + " and " + mod_csv + ".")
    print("This might need some time though.")
    distance_data = complexity_analysis.prepare_data_for_analysis(log_csv, mod_csv, log_measure, mod_measure, miner)
    print("Next, I will compute the conditioning of the provided data.")
    results = complexity_conditioning.assess_conditioning(distance_data)
    print("Next up is computing the stability of the provided data.")
    stability = complexity_stability.stability(list(distance_data['dm'].values))
    print("Done! Here are the results of your analysis:")
    complexity_conditioning.print_conditioning_report(results)
    print("Stability:", stability)
    print("This means the algorithm is ", end='')
    if stability > 0.8:
        print("SEVERELY UNSTABLE.")
    elif stability > 0.6:
        print("UNSTABLE.")
    elif stability > 0.4:
        print("MODERATELY STABLE.")
    elif stability > 0.2:
        print("STABLE.")
    else:
        print("PERFECTLY STABLE.")
