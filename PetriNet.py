import pm4py
import math
import networkx
import re
import Constants

class Place(object):
    """
    A class representing places in a Petri net.
    """
    def __init__(self, name: str, preset: list = None, postset: list = None):
        self.name = name
        self.preset = preset if preset is not None else []
        self.postset = postset if postset is not None else []

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return id(self)

class Transition(object):
    """
    A class representing transitions in a Petri net.
    """
    def __init__(self, name: str, label: str = None, preset: list = None, postset: list = None):
        self.name = name
        self.label = label
        self.preset = preset if preset is not None else []
        self.postset = postset if postset is not None else []

    def __repr__(self):
        if self.label is None:
            return str(self.name) + "(τ)"
        else:
            return str(self.name) + "(" + str(self.label) + ")"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return id(self)

class PetriNet(object):
    """
    A class representing Petri nets.
    """
    def __init__(self, places: list, transitions: list, flow: list, initial_marking: dict, final_marking: dict={}, name: str="Petri net"):
        # set the attributes as defined by the user
        self.name = name
        self.places = places
        self.transitions = transitions
        self.flow = flow
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        # calculate the pre- and postset of all places and transitions
        for (x,y) in flow:
            x.postset += [y]
            y.preset += [x]
        # calculate the set of xor-splits and xor-joins
        self.xor_splits = []
        self.xor_joins = []
        for place in self.places:
            if len(place.postset) > 1:
                self.xor_splits += [place]
            if len(place.preset) > 1:
                self.xor_joins += [place]
        # calculate the set of and-splits and and-joins
        self.and_splits = []
        self.and_joins = []
        for transition in self.transitions:
            if len(transition.postset) > 1:
                self.and_splits += [transition]
            if len(transition.preset) > 1:
                self.and_joins += [transition]

    def __repr__(self):
        representation = self.name + " = (P, T, F) with \n"
        # collect the set of places in the Petri net
        representation += "P = {"
        for index in range(len(self.places)):
            representation += str(self.places[index])
            if index < len(self.places) - 1:
                representation += ", "
        representation += "}, \n"
        # collect the set of transitions in the Petri net
        representation += "T = {"
        for index in range(len(self.transitions)):
            representation += str(self.transitions[index])
            if index < len(self.transitions) - 1:
                representation += ", "
        representation += "}, \n"
        # collect the flow relation of the Petri net
        representation += "F = {"
        for index in range(len(self.flow)):
            representation += "(" + str(self.flow[0]) + ", " + str(self.flow[1]) + ")"
            if index < len(self.flow) - 1:
                representation += ", "
        representation += "}."
        return representation

    def __str__(self):
        return self.__repr__()

    def transform_to_pm4py_PetriNet(self):
        net = pm4py.objects.petri_net.obj.PetriNet(self.name + " transformed to pm4py")
        node_dict = {}
        # transform all places to pm4py places
        for place in self.places:
            p = pm4py.objects.petri_net.obj.PetriNet.Place(place.name)
            net.places.add(p)
            node_dict[place] = p
        # transform all transitions to pm4py transitions
        for transition in self.transitions:
            t = pm4py.objects.petri_net.obj.PetriNet.Transition(transition.name + "(" + str(id(transition)) + ")", transition.label)
            net.transitions.add(t)
            node_dict[transition] = t
        # transform all arcs into pm4py arcs
        for arc in self.flow:
            start = arc[0]
            end = arc[1]
            pm4py.objects.petri_net.utils.petri_utils.add_arc_from_to(node_dict[start], node_dict[end], net)
        # transform the initial marking to a pm4py marking
        initial_marking = pm4py.objects.petri_net.obj.Marking()
        for place in self.initial_marking:
            initial_marking[node_dict[place]] = self.initial_marking[place]
        # transform the final marking to a pm4py marking
        final_marking = pm4py.objects.petri_net.obj.Marking()
        for place in self.final_marking:
            final_marking[node_dict[place]] = self.final_marking[place]
        return net, initial_marking, final_marking

    def visualize(self):
        # use the builtin visualizer by pm4py to show the Petri net
        pm4py_net, pm4py_im, pm4py_fm = self.transform_to_pm4py_PetriNet()
        pm4py.view_petri_net(pm4py_net, pm4py_im, pm4py_fm)

    def export_png(self, filename=None):
        # use the builtin exporter by pm4py to store the Petri net
        pm4py_net, pm4py_im, pm4py_fm = self.transform_to_pm4py_PetriNet()
        if filename == None:
            import string
            filename = (Constants.OUTPUT_PATH + 'model-') + re.sub(r'[^a-zA-Z0-9\s]', '', self.name)
        pm4py.save_vis_petri_net(pm4py_net, pm4py_im, pm4py_fm, file_path=filename + ".png")

    def export(self, filename=None):
        # use the builtin PNML exporter by pm4py to export the Petri net
        pm4py_net, pm4py_im, pm4py_fm = self.transform_to_pm4py_PetriNet()
        if filename == None:
            import string
            filename = (Constants.OUTPUT_PATH + 'model-') + re.sub(r'[^a-zA-Z0-9\s]', '', self.name)
        pm4py.write_pnml(pm4py_net, pm4py_im, pm4py_fm, filename + ".pnml")

    def transform_to_networkx(self, undirected = False):
        model_graph = networkx.Graph() if undirected else networkx.DiGraph()
        # add all places as nodes to the graph
        for place in self.places:
            model_graph.add_node(place)
        # add all transitions as nodes to the graph
        for transition in self.transitions:
            model_graph.add_node(transition)
        # add all arcs of the Petri net to the graph
        for (x,y) in self.flow:
            model_graph.add_edge(x, y)
        return model_graph

    def size(self):
        return len(self.places) + len(self.transitions)

    def connector_mismatch(self):
        # calculate the mismatch values for xor connectors
        mismatch_xor = 0
        for xor_split in self.xor_splits:
            mismatch_xor += len(xor_split.postset)
        for xor_join in self.xor_joins:
            mismatch_xor -= len(xor_join.preset)
        mismatch_xor = abs(mismatch_xor)
        # calculate the mismatch value for and connectors
        mismatch_and = 0
        for and_split in self.and_splits:
            mismatch_and += len(and_split.postset)
        for and_join in self.and_joins:
            mismatch_and -= len(and_join.preset)
        mismatch_and = abs(mismatch_and)
        return mismatch_xor + mismatch_and

    def connector_heterogeneity(self):
        # count the number of different connector types
        num_xor_connectors = len(set(self.xor_splits + self.xor_joins))
        num_and_connectors = len(set(self.and_splits + self.and_joins))
        num_all_connectors = num_xor_connectors + num_and_connectors
        # return a special value if there are no connectors
        if num_all_connectors == 0:
            return None
        # calculate the ratio of xor- and and-connectors
        xor_ratio = num_xor_connectors / num_all_connectors
        and_ratio = num_and_connectors / num_all_connectors
        # return zero if any of the ratios is 0
        if xor_ratio == 0 or and_ratio == 0:
            return 0
        return -(and_ratio * math.log2(and_ratio) + xor_ratio * math.log2(xor_ratio))

    def cross_connectivity(self):
        def calculate_node_weight(node):
            node_weight = 1 # the weight of transitions and non-connectors
            indeg = len(node.preset) # the number of incoming arcs
            outdeg = len(node.postset) # the number of outgoing arcs
            if node in self.xor_splits + self.xor_joins:
                node_weight = 1 / (indeg + outdeg)
            return node_weight
        def calculate_walk_weight(walk):
            # a walk consisting of a single node or no nodes has weight 0
            if len(walk) < 2:
                return 0
            # initialize the cost with the neutral element of multiplication
            cost = 1
            for i in range(1, len(walk)):
                first_node_weight = calculate_node_weight(walk[i-1])
                second_node_weight = calculate_node_weight(walk[i])
                cost *= (first_node_weight * second_node_weight)
            return cost
        # transform the model into a directed graph
        model_graph = self.transform_to_networkx(undirected=False)
        # initialize a table of connection values with all 0 entries
        # and set the weights of each edge
        connection_values = {}
        for start in model_graph.nodes:
            connection_values[start] = {}
            for end in model_graph.nodes:
                connection_values[start][end] = 0
                # calculate the weight only if the edge exists
                if model_graph.has_edge(start, end):
                    weight_start = calculate_node_weight(start)
                    weight_end = calculate_node_weight(end)
                    log_weight = -math.log(weight_start * weight_end)
                    model_graph[start][end]["weight"] = log_weight
        # calculate the shortest paths for the constructed graph
        sum_of_weights = 0
        for start in model_graph.nodes:
            paths = networkx.single_source_dijkstra_path(model_graph, source=start)
            for end in paths.keys():
                path = paths[end]
                weight_of_way = calculate_walk_weight(path)
                connection_values[start][end] = weight_of_way
                sum_of_weights += weight_of_way
        # calculate the connection values of nodes to themselves
        for cycle in networkx.simple_cycles(model_graph):
            cycle_weight = calculate_walk_weight(cycle + [cycle[0]])
            for node in cycle:
                if cycle_weight > connection_values[node][node]:
                    sum_of_weights -= connection_values[node][node]
                    connection_values[node][node] = cycle_weight
                    sum_of_weights += cycle_weight
        # calculate the total cross connectivity score
        maximum_sum_of_weights = len(model_graph.nodes) * len(model_graph.nodes)
        cross_connectivity = 1 - (sum_of_weights / maximum_sum_of_weights)
        return cross_connectivity

    def token_split(self):
        token_split = 0
        for and_split in self.and_splits:
            token_split += len(and_split.postset) - 1
        return token_split

    def separability(self):
        model_graph = self.transform_to_networkx(undirected = True)
        cut_vertices = list(networkx.articulation_points(model_graph))
        all_vertices = self.places + self.transitions
        return 1 - (len(cut_vertices) / len(all_vertices))

    def control_flow_complexity(self):
        cfc = len(self.and_splits)
        for xor_split in self.xor_splits:
            cfc += len(xor_split.postset)
        return cfc

    def average_connector_degree(self):
        sum_of_degrees = 0
        connectors = set(self.xor_splits + self.xor_joins + self.and_splits + self.and_joins)
        for connector in connectors:
            sum_of_degrees += len(connector.preset) + len(connector.postset)
        number_of_connectors = len(connectors)
        if number_of_connectors == 0:
            return None
        return sum_of_degrees / number_of_connectors

    def maximum_connector_degree(self):
        maximum_degree = -math.inf
        connectors = set(self.xor_splits + self.xor_joins + self.and_splits + self.and_joins)
        for connector in connectors:
            degree = len(connector.preset) + len(connector.postset)
            if degree > maximum_degree:
                maximum_degree = degree
        if maximum_degree == -math.inf:
            return None
        return maximum_degree

    def sequentiality(self):
        num_sequential_arcs = 0
        connectors = set(self.xor_splits + self.xor_joins + self.and_splits + self.and_joins)
        for (x,y) in self.flow:
            if x not in connectors and y not in connectors:
                num_sequential_arcs += 1
        if len(self.flow) == 0:
            return None
        return 1 - (num_sequential_arcs / len(self.flow))

    def depth(self):
        def calculate_weight_of_path(graph, path):
            weight = 0
            for i in range(1, len(path)):
                start = path[i-1]
                end = path[i]
                if graph[start][end]["weight"] > 0 or weight != 0: # bugfix
                    weight += graph[start][end]["weight"]
            return weight

        def calculate_highest_path_length(weighted_graph, start, end):
            maximum_weight = 0
            for path in networkx.all_simple_paths(weighted_graph, start, end):
                weight = calculate_weight_of_path(weighted_graph, path)
                if weight > maximum_weight:
                    maximum_weight = weight
            return maximum_weight

        def calculate_maximum_node_depths(graph):
            maximum_node_depths = {}
            for node in graph.nodes:
                maximum_node_depths[node] = 0
            for start in graph.nodes:
                for end in graph.nodes:
                    node_depth = calculate_highest_path_length(graph, start, end)
                    if node_depth > maximum_node_depths[end]:
                        maximum_node_depths[end] = node_depth
            return maximum_node_depths

        # calculate the in-depth of each node
        model_graph = self.transform_to_networkx(undirected = False)
        split_nodes = set(self.xor_splits + self.and_splits)
        join_nodes = set(self.xor_joins + self.and_joins)
        # set the weights of the edges
        for (u, v) in model_graph.edges:
            if u in split_nodes:
                if v not in join_nodes:
                    model_graph[u][v]["weight"] = 1
                else:
                    model_graph[u][v]["weight"] = 0
            else:
                if v not in join_nodes:
                    model_graph[u][v]["weight"] = 0
                else:
                    model_graph[u][v]["weight"] = -1
        maximum_node_in_depths = calculate_maximum_node_depths(model_graph)

        # next, calculate the out-depth of each node
        model_graph = model_graph.reverse()
        # set the weights of the edges
        for (u, v) in model_graph.edges:
            if u in join_nodes:
                if v not in split_nodes:
                    model_graph[u][v]["weight"] = 1
                else:
                    model_graph[u][v]["weight"] = 0
            else:
                if v not in split_nodes:
                    model_graph[u][v]["weight"] = 0
                else:
                    model_graph[u][v]["weight"] = -1
#        for (u, v) in model_graph.edges:
#            if u in join_nodes:
#                if v not in split_nodes:
#                    model_graph[u][v]["weight"] = 1
#                else:
#                    model_graph[u][v]["weight"] = 0
#            else:
#                if v not in split_nodes:
#                    model_graph[u][v]["weight"] = 0
#                else:
#                    model_graph[u][v]["weight"] = -1
        maximum_node_out_depths = calculate_maximum_node_depths(model_graph)

        # calculate the depth of the Petri net
        depth = 0
        for node in model_graph.nodes:
            in_depth = maximum_node_in_depths[node]
            out_depth = maximum_node_out_depths[node]
            minimum = min(in_depth, out_depth)
            if minimum > depth:
                depth = minimum
        return depth

    def diameter(self):
        model_graph = self.transform_to_networkx(undirected = False)
        maximum_simple_path_length = -math.inf
        for start in model_graph.nodes:
            for end in model_graph.nodes:
                for path in networkx.all_simple_paths(model_graph, start, end):
                    if len(path) > maximum_simple_path_length:
                        maximum_simple_path_length = len(path)
        return maximum_simple_path_length

    def cyclicity(self):
        model_graph = self.transform_to_networkx(undirected = False)
        nodes_on_cycles = set()
        for component in networkx.strongly_connected_components(model_graph):
            if len(component) > 1:
                nodes_on_cycles.update(component)
        return len(nodes_on_cycles) / (len(self.places) + len(self.transitions))

    def density(self):
        number_of_arcs = len(self.flow)
        maximum_number_of_arcs = 2 * len(self.places) * len(self.transitions)
        if maximum_number_of_arcs == 0:
            return None
        return number_of_arcs / maximum_number_of_arcs

    def coefficient_of_network_connectivity(self):
        return len(self.flow) / (len(self.places) + len(self.transitions))

    def number_of_duplicate_tasks(self):
        encountered_transition_labels = set()
        duplicates = 0
        for transition in self.transitions:
            if transition.label in encountered_transition_labels:
                duplicates += 1
            encountered_transition_labels.add(transition.label)
        return duplicates

    def empty_sequence_flows(self):
        empty_sequence_flows = 0
        for place in self.places:
            empty_sequence_node = True
            for transition in place.preset:
                if transition not in self.and_splits:
                    empty_sequence_node = False
            if len(place.preset) == 0: # bugfix
                empty_sequence_node = False # bugfix
            for transition in place.postset:
                if transition not in self.and_joins:
                    empty_sequence_node = False
            if len(place.postset) == 0: # bugfix
                empty_sequence_node = 0 # bugfix
            if empty_sequence_node:
                empty_sequence_flows += 1
        return empty_sequence_flows

def is_model_workflow_net(model: PetriNet):
    initial_place = None
    final_place = None
    # 1. find if there is an initial and a final place
    for place in model.places:
        # if the place has no incoming arcs, it could be the initial place
        if len(place.preset) == 0:
            # but only if we haven't found an initial place so far
            if initial_place is not None:
                return (False, None, None)
            else:
                initial_place = place
        # if the place has no outgoing arcs, it could be the final place
        if len(place.postset) == 0:
            # but only if we haven't found a final place so far
            if final_place is not None:
                return (False, None, None)
            else:
                final_place = place
    if initial_place is None or final_place is None:
        return (False, None, None)
    # 2. check if the short-circuited net is strongly connected
    model_graph = model.transform_to_networkx(undirected=False)
    model_graph.add_edge(final_place, initial_place)
    num_connected_components = len(list(networkx.strongly_connected_components(model_graph)))
    if num_connected_components != 1:
        return (False, None, None)
    else:
        return (True, initial_place, final_place)

class WorkflowNet(PetriNet):
    def __init__(self, places: list, transitions: list, flow: list, name: str="Workflow net"):
        PetriNet.__init__(self, places, transitions, flow, {}, {}, name)
        (is_wfn, initial_place, final_place) = is_model_workflow_net(self)
        if not is_wfn:
            raise Exception("The specified model is not a workflow net.")
        self.initial_place = initial_place
        self.final_place = final_place
        self.initial_marking = {initial_place: 1}
        self.final_markung = {final_place: 1}

    def cross_connectivity(self):
        def calculate_node_weight(node):
            node_weight = 1 # the weight of transitions and non-connectors
            indeg = len(node.preset) # the number of incoming arcs
            outdeg = len(node.postset) # the number of outgoing arcs
            if node in self.xor_splits + self.xor_joins:
                node_weight = 1 / (indeg + outdeg)
            return node_weight
        def calculate_walk_weight(walk):
            # a walk consisting of a single node or no nodes has weight 0
            if len(walk) < 2:
                return 0
            # initialize the cost with the neutral element of multiplication
            cost = 1
            for i in range(1, len(walk)):
                first_node_weight = calculate_node_weight(walk[i-1])
                second_node_weight = calculate_node_weight(walk[i])
                cost *= (first_node_weight * second_node_weight)
            return cost
        # transform the model into a directed graph
        model_graph = self.transform_to_networkx(undirected=False)
        # initialize a table of connection values with all 0 entries
        # and set the weights of each edge
        connection_values = {}
        for start in model_graph.nodes:
            connection_values[start] = {}
            for end in model_graph.nodes:
                connection_values[start][end] = 0
                # calculate the weight only if the edge exists
                if model_graph.has_edge(start, end):
                    weight_start = calculate_node_weight(start)
                    weight_end = calculate_node_weight(end)
                    log_weight = -math.log(weight_start * weight_end)
                    model_graph[start][end]["weight"] = log_weight
        # calculate the shortest paths for the constructed graph
        sum_of_weights = 0
        for start in model_graph.nodes:
            paths = networkx.single_source_dijkstra_path(model_graph, source=start)
            for end in paths.keys():
                path = paths[end]
                weight_of_way = calculate_walk_weight(path)
                connection_values[start][end] = weight_of_way
                sum_of_weights += weight_of_way
        # calculate the connection values of nodes to themselves
        for cycle in networkx.simple_cycles(model_graph):
            cycle_weight = calculate_walk_weight(cycle + [cycle[0]])
            for node in cycle:
                if cycle_weight > connection_values[node][node]:
                    sum_of_weights -= connection_values[node][node]
                    connection_values[node][node] = cycle_weight
                    sum_of_weights += cycle_weight
        # calculate the total cross connectivity score
        maximum_sum_of_weights = (len(model_graph.nodes)-1) * (len(model_graph.nodes)-1)
        cross_connectivity = 1 - (sum_of_weights / maximum_sum_of_weights)
        return cross_connectivity

    def separability(self):
        model_graph = self.transform_to_networkx(undirected = True)
        cut_vertices = list(networkx.articulation_points(model_graph))
        all_vertices = self.places + self.transitions
        return 1 - (len(cut_vertices) / (len(all_vertices) - 2))

    def depth(self):
        def calculate_weight_of_path(graph, path):
            weight = 0
            for i in range(1, len(path)):
                start = path[i-1]
                end = path[i]
                if graph[start][end]["weight"] > 0 or weight != 0: # bugfix
                    weight += graph[start][end]["weight"]
            return weight

        def calculate_highest_path_length(weighted_graph, start, end):
            maximum_weight = 0
            for path in networkx.all_simple_paths(weighted_graph, start, end):
                weight = calculate_weight_of_path(weighted_graph, path)
                if weight > maximum_weight:
                    maximum_weight = weight
            return maximum_weight

        def calculate_maximum_node_depths(graph, start):
            maximum_node_depths = {}
            for end in graph.nodes:
                node_depth = calculate_highest_path_length(graph, start, end)
                maximum_node_depths[end] = node_depth
            return maximum_node_depths

        # calculate the in-depth of each node
        model_graph = self.transform_to_networkx(undirected = False)
        split_nodes = set(self.xor_splits + self.and_splits)
        join_nodes = set(self.xor_joins + self.and_joins)
        # set the weights of the edges
        for (u, v) in model_graph.edges:
            if u in split_nodes:
                if v not in join_nodes:
                    model_graph[u][v]["weight"] = 1
                else:
                    model_graph[u][v]["weight"] = 0
            else:
                if v not in join_nodes:
                    model_graph[u][v]["weight"] = 0
                else:
                    model_graph[u][v]["weight"] = -1
        maximum_node_in_depths = calculate_maximum_node_depths(model_graph, self.initial_place)

        # next, calculate the out-depth of each node
        model_graph = model_graph.reverse()
        # set the weights of the edges
        for (u, v) in model_graph.edges:
            if u in join_nodes:
                if v not in split_nodes:
                    model_graph[u][v]["weight"] = 1
                else:
                    model_graph[u][v]["weight"] = 0
            else:
                if v not in split_nodes:
                    model_graph[u][v]["weight"] = 0
                else:
                    model_graph[u][v]["weight"] = -1
#        for (u, v) in model_graph.edges:
#            if u in split_nodes:
#                if v not in join_nodes:
#                    model_graph[u][v]["weight"] = -1
#                else:
#                    model_graph[u][v]["weight"] = 0
#            else:
#                if v not in join_nodes:
#                    model_graph[u][v]["weight"] = 0
#                else:
#                    model_graph[u][v]["weight"] = 1
        maximum_node_out_depths = calculate_maximum_node_depths(model_graph, self.final_place)

        # calculate the depth of the Petri net
        depth = 0
        for node in model_graph.nodes:
            in_depth = maximum_node_in_depths[node]
            out_depth = maximum_node_out_depths[node]
            minimum = min(in_depth, out_depth)
            if minimum > depth:
                depth = minimum
        return depth

    def diameter(self):
        model_graph = self.transform_to_networkx(undirected = False)
        maximum_simple_path_length = -math.inf
        start = self.initial_place
        end = self.final_place
        for path in networkx.all_simple_paths(model_graph, start, end):
            if len(path) > maximum_simple_path_length:
                maximum_simple_path_length = len(path)
        return maximum_simple_path_length

    def cyclicity(self):
        model_graph = self.transform_to_networkx(undirected = False)
        nodes_on_cycles = set()
        for component in networkx.strongly_connected_components(model_graph):
            if len(component) > 1:
                nodes_on_cycles.update(component)
        return len(nodes_on_cycles) / (len(self.places) + len(self.transitions) - 2)

    def density(self):
        number_of_arcs = len(self.flow)
        maximum_number_of_arcs = 2 * len(self.transitions) * (len(self.places) - 1)
        return number_of_arcs / maximum_number_of_arcs

def transform_to_petri_net(model, im=None, fm=None):
    if type(model) is PetriNet:
        return model
    elif type(model) is WorkflowNet:
        name = model.name
        # extract the places of the Petri net
        pm4py_node_dict = {}
        places = []
        for p in model.places:
            new_place = Place(p.name)
            places += [new_place]
            pm4py_node_dict[p] = new_place
        # extract the transitions of the Petri net
        transitions = []
        for t in model.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            pm4py_node_dict[t] = new_transition
        # collect the flow relation of the Petri net
        flow = []
        for (x,y) in model.flow:
            flow += [(pm4py_node_dict[x], pm4py_node_dict[y])]
        initial_marking = {model.initial_place: 1}
        final_marking = {model.final_place: 1}
        return PetriNet( places, transitions, flow, initial_marking, final_marking, name)
    elif type(model) is pm4py.objects.petri_net.obj.PetriNet:
        name = model.name
        # extract the places of the Petri net
        pm4py_node_dict = {}
        places = []
        for p in model.places:
            new_place = Place(p.name)
            places += [new_place]
            pm4py_node_dict[p] = new_place
        # extract the transitions of the Petri net
        transitions = []
        for t in model.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            pm4py_node_dict[t] = new_transition
        # collect the flow relation of the Petri net
        flow = []
        for arc in model.arcs:
            source = arc.source
            target = arc.target
            flow += [(pm4py_node_dict[source], pm4py_node_dict[target])]
        initial_marking = {}
        final_marking = {}
        return PetriNet( places, transitions, flow, initial_marking, final_marking, name)
    else:
        raise Exception("Cannot convert object of type " + str(type(model)) + " to PetriNet.")

def transform_to_workflow_net(model):
    if type(model) is WorkflowNet:
        return model
    elif type(model) is PetriNet:
        (is_wfn, ip, fp) = is_model_workflow_net(model)
        # return special value None if it is no workflow net
        if not is_wfn:
            return None
        name = model.name
        # extract the places of the Petri net
        pn_node_dict = {}
        places = []
        for p in model.places:
            new_place = Place(p.name)
            places += [new_place]
            pn_node_dict[p] = new_place
        # extract the transitions of the Petri net
        transitions = []
        for t in model.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            pn_node_dict[t] = new_transition
        # collect the flow relation of the Petri net
        flow = []
        for arc in model.flow:
            source = arc[0]
            target = arc[1]
            flow += [(pn_node_dict[source], pn_node_dict[target])]
        return WorkflowNet(places, transitions, flow, name)
    elif type(model) is pm4py.objects.petri_net.obj.PetriNet:
        # check if the model is a workflow net
        pn = transform_to_petri_net(model)
        (is_wfn, ip, fp) = is_model_workflow_net(pn)
        # return special value None if it is no workflow net
        if not is_wfn:
            return None
        name = model.name
        # extract the places of the Petri net
        pm4py_node_dict = {}
        places = []
        for p in model.places:
            new_place = Place(p.name)
            places += [new_place]
            pm4py_node_dict[p] = new_place
        # extract the transitions of the Petri net
        transitions = []
        for t in model.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            pm4py_node_dict[t] = new_transition
        # collect the flow relation of the Petri net
        flow = []
        for arc in model.arcs:
            source = arc.source
            target = arc.target
            flow += [(pm4py_node_dict[source], pm4py_node_dict[target])]
        return WorkflowNet(places, transitions, flow, name)

def sequential_combination(workflow_nets: list):
    # raise an exception if the list of workflow nets is empty
    if len(workflow_nets) == 0:
        raise Exception("Cannot perform the sequential combination of 0 nets.")
    # if the list contains exactly one workflow net, return it
    if len(workflow_nets) == 1:
        return workflow_nets[0]
    # otherwise, there are at least two workflow nets in the passed list
    # collect the names of them to combine them into a new informative name
    name = "sequential combination of "
    for i in range(len(workflow_nets)-1):
        name += workflow_nets[i].name + ", "
    name += "and " + workflow_nets[-1].name
    # initialize lists for the places, transitions and arcs
    places = []
    transitions = []
    flow = []
    # iterate through all of the passed workflow nets
    initial_places = []
    final_places = []
    for net in workflow_nets:
        # keep a dictionary to collect the flow relation later
        node_dict = {}
        # collect the places of the nets
        for p in net.places:
            new_place = Place(p.name)
            places += [new_place]
            node_dict[p] = new_place
        # collect the transitions of the nets
        for t in net.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            node_dict[t] = new_transition
        # collect the flow relation of the nets
        for (x,y) in net.flow:
            flow += [(node_dict[x], node_dict[y])]
        # collect the initial and final places of the nets
        initial_places += [node_dict[net.initial_place]]
        final_places += [node_dict[net.final_place]]
    # add transitions between the initial places and final places
    for i in range(1,len(initial_places)):
        transition = Transition("t_{" + str((i-1, i)) + "}", None)
        transitions += [transition]
        flow += [(final_places[i-1], transition)]
        flow += [(transition, initial_places[i])]
    return WorkflowNet(places, transitions, flow, name)

def parallel_combination(workflow_nets: list):
    # raise an exception if the list of workflow nets is empty
    if len(workflow_nets) == 0:
        raise Exception("Cannot perform the sequential combination of 0 nets.")
    # if the list contains exactly one workflow net, return it
    if len(workflow_nets) == 1:
        return workflow_nets[0]
    # otherwise, there are at least two workflow nets in the passed list
    # collect the names of them to combine them into a new informative name
    name = "parallel combination of "
    for i in range(len(workflow_nets)-1):
        name += workflow_nets[i].name + ", "
    name += "and " + workflow_nets[-1].name
    # initialize lists for the places, transitions and arcs
    places = []
    transitions = []
    flow = []
    # iterate through all of the passed workflow nets
    initial_places = []
    final_places = []
    for net in workflow_nets:
        # keep a dictionary to collect the flow relation later
        node_dict = {}
        # collect the places of the nets
        for p in net.places:
            new_place = Place(p.name)
            places += [new_place]
            node_dict[p] = new_place
        # collect the transitions of the nets
        for t in net.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            node_dict[t] = new_transition
        # collect the flow relation of the nets
        for (x,y) in net.flow:
            flow += [(node_dict[x], node_dict[y])]
        # collect the initial and final places of the nets
        initial_places += [node_dict[net.initial_place]]
        final_places += [node_dict[net.final_place]]
    # add and transitions according to the parallel construction
    start_place = Place("p_i^*")
    places += [start_place]
    start_transition = Transition("t_i^*", None)
    transitions += [start_transition]
    flow += [(start_place, start_transition)]
    for initial_place in initial_places:
        flow += [(start_transition, initial_place)]
    end_place = Place("p_o^*")
    places += [end_place]
    end_transition = Transition("t_o^*", None)
    transitions += [end_transition]
    flow += [(end_transition, end_place)]
    for final_place in final_places:
        flow += [(final_place, end_transition)]
    return WorkflowNet(places, transitions, flow, name)

def choice_combination(workflow_nets: list):
    # raise an exception if the list of workflow nets is empty
    if len(workflow_nets) == 0:
        raise Exception("Cannot perform the sequential combination of 0 nets.")
    # if the list contains exactly one workflow net, return it
    if len(workflow_nets) == 1:
        return workflow_nets[0]
    # otherwise, there are at least two workflow nets in the passed list
    # collect the names of them to combine them into a new informative name
    name = "choice combination of "
    for i in range(len(workflow_nets)-1):
        name += workflow_nets[i].name + ", "
    name += "and " + workflow_nets[-1].name
    # initialize lists for the places, transitions and arcs
    places = []
    transitions = []
    flow = []
    # iterate through all of the passed workflow nets
    initial_places = []
    final_places = []
    for net in workflow_nets:
        # keep a dictionary to collect the flow relation later
        node_dict = {}
        # collect the places of the nets
        for p in net.places:
            new_place = Place(p.name)
            places += [new_place]
            node_dict[p] = new_place
        # collect the transitions of the nets
        for t in net.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            node_dict[t] = new_transition
        # collect the flow relation of the nets
        for (x,y) in net.flow:
            flow += [(node_dict[x], node_dict[y])]
        # collect the initial and final places of the nets
        initial_places += [node_dict[net.initial_place]]
        final_places += [node_dict[net.final_place]]
    # add and transitions according to the parallel construction
    start_place = Place("p_i^*")
    places += [start_place]
    for i in range(len(initial_places)):
        initial_place = initial_places[i]
        start_transition = Transition("t_{" + str(i+1) + "}^*", None)
        transitions += [start_transition]
        flow += [(start_place,start_transition), (start_transition,initial_place)]
    end_place = Place("p_o^*")
    places += [end_place]
    for i in range(len(final_places)):
        final_place = final_places[i]
        end_transition = Transition("s_{" + str(i+1) + "}^*", None)
        transitions += [end_transition]
        flow += [(final_place,end_transition), (end_transition,end_place)]
    return WorkflowNet(places, transitions, flow, name)

def loop_combination(workflow_nets: list):
    # raise an exception if the list of workflow nets is empty
    if len(workflow_nets) == 0:
        raise Exception("Cannot perform the sequential combination of 0 nets.")
    # if the list contains exactly one workflow net, return it
    if len(workflow_nets) == 1:
        return workflow_nets[0]
    # otherwise, there are at least two workflow nets in the passed list
    # collect the names of them to combine them into a new informative name
    name = "loop combination of "
    for i in range(len(workflow_nets)-1):
        name += workflow_nets[i].name + ", "
    name += "and " + workflow_nets[-1].name
    # initialize lists for the places, transitions and arcs
    places = []
    transitions = []
    flow = []
    # iterate through all of the passed workflow nets
    initial_places = []
    final_places = []
    for net in workflow_nets:
        # keep a dictionary to collect the flow relation later
        node_dict = {}
        # collect the places of the nets
        for p in net.places:
            new_place = Place(p.name)
            places += [new_place]
            node_dict[p] = new_place
        # collect the transitions of the nets
        for t in net.transitions:
            new_transition = Transition(t.name, t.label)
            transitions += [new_transition]
            node_dict[t] = new_transition
        # collect the flow relation of the nets
        for (x,y) in net.flow:
            flow += [(node_dict[x], node_dict[y])]
        # collect the initial and final places of the nets
        initial_places += [node_dict[net.initial_place]]
        final_places += [node_dict[net.final_place]]
    # add and transitions according to the parallel construction
    start_place_left = Place("p_i^*")
    places += [start_place_left]
    start_transition_left = Transition("t^*", None)
    transitions += [start_transition_left]
    flow += [(start_place_left,start_transition_left)]
    start_place = Place("p^*")
    places += [start_place]
    flow += [(start_transition_left,start_place)]
    end_place_right = Place("p_o^*")
    places += [end_place_right]
    end_transition_right = Transition("s^*", None)
    transitions += [end_transition_right]
    flow += [(end_transition_right,end_place_right)]
    end_place = Place("q^*")
    places += [end_place]
    flow += [(end_place,end_transition_right)]
    for i in range(len(initial_places)):
        if i == 1:
            transition = Transition("t_{" + str(i+1) + "}^*", None)
            transitions += [transition]
            flow += [(start_place,transition), (transition,initial_places[i])]
        else:
            transition = Transition("s_{" + str(i+1) + "}^*", None)
            transitions += [transition]
            flow += [(transition,initial_places[i]), (end_place,transition)]
    for i in range(len(final_places)):
        if i == 1:
            transition = Transition("s_{" + str(i+1) + "}^*", None)
            transitions += [transition]
            flow += [(final_places[i],transition), (transition,end_place)]
        else:
            transition = Transition("t_{" + str(i+1) + "}^*", None)
            transitions += [transition]
            flow += [(transition,start_place), (final_places[i],transition)]
    return WorkflowNet(places, transitions, flow, name)
