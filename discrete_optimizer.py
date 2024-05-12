from typing import Callable, Iterable, List, Optional, Tuple, Dict
from copy import copy
from pprint import pprint

class Values:
    def __init__(self) -> None:
        self.values = None

    def get_first_value(self):
        return None

    def __contains__(self, key) -> bool:
        return False

    def __iter__(self):
        return self 

    def __next__(self):
        raise StopIteration

    def __repr__(self) -> str:
        return str(self.values)

    def __hash__(self) -> int:
        if self.values is not None:
            return hash(None)
        else:
            return hash(tuple(self.values))


class ListValues(Values):
    def __init__(self, values: List[int]) -> None:
        super().__init__()
        self.values = values 

    def __iter__(self):
        self.iter_index = 0
        return self
   
    def __next__(self):
        if self.iter_index < len(self.values):
            return_value = self.values[self.iter_index]
            self.iter_index += 1
            return return_value
        else:
            raise StopIteration


    def __contains__(self, key) -> bool:
        return (key in self.values)

    def get_first_value(self):
        return self.values[0]


class Parameter:
    def __init__(self, name: str, dependencies: Dict[Tuple[Optional["Parameter"], Optional[Values]], Values]) -> None:
        self.name = name
        # CAUTION: currently only one dependency is supported
        self.dependencies = dependencies
        self.current_value = None 
        self.contrained_values = None
 
    def __iter__(self):
        self.constrain_values_via_dependencies() 
        self.current_value = self.contrained_values[0]
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.contrained_values):
            self.current_value = self.contrained_values[self.index]
            self.index += 1
            return self.current_value
        else:
            raise StopIteration 

    def __repr__(self) -> str:
        return f"{self.name}={self.current_value}"

    def __hash__(self) -> int:
        return hash(self.name)


    def infer_initial_value(self):
        # if there is no dependency to another parameter set it to the first value for values
        if (None, None) in self.dependencies.keys():
            self.current_value = self.dependencies[(None, None)].get_first_value()
        else:
            # get current values of all parameter dependencies
            dependency_parameters = set()

            for parameter, value_range in self.dependencies.keys():
                dependency_parameters.add(parameter)

            # for each parameter infer the initial value
            for parameter in dependency_parameters:
                parameter.infer_initial_value()

            self.constrain_values_via_dependencies()

            if len(self.contrained_values) == 0:
                self.current_value = None
            else:
                self.current_value = self.contrained_values[0]

    def constrain_values_via_dependencies(self):
        if (None, None) in self.dependencies.keys():
            self.contrained_values = list(self.dependencies[(None,None)]) 
        else:
            possible_values = set()

            for (constraining_parameter, contraining_value_range), possible_value_range in self.dependencies.items():
                # check if the current value of constraining parameter is in the constraining range
                # if this is the case add the values of the possible value range to values
                if constraining_parameter.current_value in contraining_value_range:
                    for value in possible_value_range:
                        possible_values.add(value)

            self.contrained_values = sorted(list(possible_values))


class ParameterSet:
    def __init__(self, parameters: List[Parameter]) -> None:
        # CAUTION: parameters need to be ordered by their dependencies
        self.parameters = parameters
        self.initialize_parameters()
          
    def initialize_parameters(self):
        for parameter in self.parameters:
            parameter.infer_initial_value()

    def get_design_space(self):
        design_space = [[]]

        for index, current_parameter in enumerate(self.parameters):
            new_design_space = []
            for design_point in design_space:
                # set the curren_value of parameters on which the current_parameter might 
                # depend to the to the value in the design point in order to constrain the 
                # current_parameter correctly
                for i in range(index):
                    self.parameters[i].current_value = design_point[i]

                # when iterating over the values of a parameter it is automatically 
                # contrained
                for value in current_parameter:
                    new_design_point = design_point + [value]
                    new_design_space.append(new_design_point)
            design_space = new_design_space

        return design_space


    def __repr__(self) -> str:
        return str(self.parameters)


class DiscreteOptimizer:
    def __init__(self, parameter_set: ParameterSet, objective_function: Callable) -> None:
        self.parameter_set = parameter_set
        self.objective_function = objective_function 


class GlobalSearch(DiscreteOptimizer):
    ...

if __name__ == "__main__":
    p0_values = ListValues([0,1,2,3,4,5]) 
    p0 = Parameter("p0", {(None, None): p0_values})
    #p0.infer_initial_value()

    p1_values0 = ListValues([0,1,2,3]) 
    p1_values1 = ListValues([2,3,4,5]) 

    p1 = Parameter("p1", {(p0, ListValues([0,1,2])): p1_values0, (p0, ListValues([3,4,5])): p1_values1 })
    #p1.infer_initial_value()

    p2_values0 = ListValues([0]) 
    p2_values1 = ListValues([1]) 
    p2 = Parameter("p2", {(p1, ListValues([0,1,2,3,4])): p2_values0, (p1, ListValues([5])): p2_values1})

    ps = ParameterSet([p0, p1, p2])
    ds = ps.get_design_space()

    for dp in ds:
        print(dp)
