#  SPDX-FileCopyrightText: 2025 EasyScience contributors  <core@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2025 Contributors to the EasyScience project <https://github.com/easyScience/EasyScience

from __future__ import annotations

import copy
import numbers
import re
import warnings
import weakref
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import numpy as np
import scipp as sc
from asteval import Interpreter
from scipp import UnitError
from scipp import Variable

from easyscience import global_object
from easyscience.global_object.undo_redo import property_stack

from .descriptor_number import DescriptorNumber
from .descriptor_number import notify_observers


class Parameter(DescriptorNumber):
    """
    A Parameter is a DescriptorNumber which can be used in fitting. It has additional fields to facilitate this.
    """

    # Used by serializer
    _REDIRECT = DescriptorNumber._REDIRECT
    _REDIRECT['callback'] = None

    def __init__(
        self,
        name: str,
        value: numbers.Number,
        unit: Optional[Union[str, sc.Unit]] = '',
        variance: Optional[numbers.Number] = 0.0,
        min: Optional[numbers.Number] = -np.inf,
        max: Optional[numbers.Number] = np.inf,
        fixed: Optional[bool] = False,
        unique_name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        display_name: Optional[str] = None,
        callback: property = property(),
        parent: Optional[Any] = None,
    ):
        """
        This class is an extension of a `DescriptorNumber`. Where the descriptor was for static
        objects, a `Parameter` is for dynamic objects. A parameter has the ability to be used in fitting and has
        additional fields to facilitate this.

        :param name: Name of this object
        :param value: Value of this object
        :param unit: This object can have a physical unit associated with it
        :param variance: The variance of the value
        :param min: The minimum value for fitting
        :param max: The maximum value for fitting
        :param fixed: If the parameter is free to vary during fitting
        :param description: A brief summary of what this object is
        :param url: Lookup url for documentation/information
        :param display_name: The name of the object as it should be displayed
        :param parent: The object which is the parent to this one

        .. note::
            Undo/Redo functionality is implemented for the attributes `value`, `variance`, `error`, `min`, `max`, `bounds`, `fixed`, `unit`
        """  # noqa: E501
        if not isinstance(min, numbers.Number):
            raise TypeError('`min` must be a number')
        if not isinstance(max, numbers.Number):
            raise TypeError('`max` must be a number')
        if not isinstance(value, numbers.Number):
            raise TypeError('`value` must be a number')
        if value < min:
            raise ValueError(f'{value=} can not be less than {min=}')
        if value > max:
            raise ValueError(f'{value=} can not be greater than {max=}')
        if np.isclose(min, max, rtol=1e-9, atol=0.0):
            raise ValueError('The min and max bounds cannot be identical. Please use fixed=True instead to fix the value.')
        if not isinstance(fixed, bool):
            raise TypeError('`fixed` must be either True or False')
        self._independent = True
        self._fixed = fixed # For fitting, but must be initialized before super().__init__
        self._min = sc.scalar(float(min), unit=unit)
        self._max = sc.scalar(float(max), unit=unit)

        super().__init__(
            name=name,
            value=value,
            unit=unit,
            variance=variance,
            unique_name=unique_name,
            description=description,
            url=url,
            display_name=display_name,
            parent=parent,
        )

        self._callback = callback  # Callback is used by interface to link to model
        if self._callback.fdel is not None:
            weakref.finalize(self, self._callback.fdel)

        # Create additional fitting elements
        self._initial_scalar = copy.deepcopy(self._scalar)

    @classmethod
    def from_dependency(cls, name: str, dependency_expression: str, dependency_map: Optional[dict] = None, **kwargs) -> Parameter:  # noqa: E501
        """
        Create a dependent Parameter directly from a dependency expression.
        
        :param name: The name of the parameter
        :param dependency_expression: The dependency expression to evaluate. This should be a string which can be evaluated by the ASTEval interpreter.
        :param dependency_map: A dictionary of dependency expression symbol name and dependency object pairs. This is inserted into the asteval interpreter to resolve dependencies. 
        :param kwargs: Additional keyword arguments to pass to the Parameter constructor.
        :return: A new dependent Parameter object.
        """  # noqa: E501
        parameter = cls(name=name, value=0.0, unit='', variance=0.0, min=-np.inf, max=np.inf, **kwargs)
        parameter.make_dependent_on(dependency_expression=dependency_expression, dependency_map=dependency_map)
        return parameter

    def _update(self) -> None:
        """
        Update the parameter. This is called by the DescriptorNumbers/Parameters who have this Parameter as a dependency.
        """
        if not self._independent:
            # Update the value of the parameter using the dependency interpreter
            temporary_parameter = self._dependency_interpreter(self._clean_dependency_string)
            self._scalar.value = temporary_parameter.value
            self._scalar.unit = temporary_parameter.unit
            self._scalar.variance = temporary_parameter.variance
            self._min.value = temporary_parameter.min if isinstance(temporary_parameter, Parameter) else temporary_parameter.value  # noqa: E501
            self._max.value = temporary_parameter.max if isinstance(temporary_parameter, Parameter) else temporary_parameter.value  # noqa: E501
            self._min.unit = temporary_parameter.unit
            self._max.unit = temporary_parameter.unit
            self._notify_observers()
        else:
            warnings.warn('This parameter is not dependent. It cannot be updated.')

    def make_dependent_on(self, dependency_expression: str, dependency_map: Optional[dict] = None) -> None:
        """
        Make this parameter dependent on another parameter. This will overwrite the current value, unit, variance, min and max.

        How to use the dependency map:
        If a parameter c has a dependency expression of 'a + b', where a and b are parameters belonging to the model class,
        then the dependency map needs to have the form {'a': model.a, 'b': model.b}, where model is the model class.
        I.e. the values are the actual objects, whereas the keys are how they are represented in the dependency expression.

        The dependency map is not needed if the dependency expression uses the unique names of the parameters.
        Unique names in dependency expressions are defined by quotes, e.g. 'Parameter_0' or "Parameter_0" depending on the quotes used for the expression.

        :param dependency_expression: The dependency expression to evaluate. This should be a string which can be evaluated by a python interpreter.
        :param dependency_map: A dictionary of dependency expression symbol name and dependency object pairs. This is inserted into the asteval interpreter to resolve dependencies. 
        """  # noqa: E501
        if not isinstance(dependency_expression, str):
            raise TypeError('`dependency_expression` must be a string representing a valid dependency expression.')
        if not (isinstance(dependency_map, dict) or dependency_map is None):
            raise TypeError('`dependency_map` must be a dictionary of dependencies and their corresponding names in the dependecy expression.')  # noqa: E501
        if isinstance(dependency_map, dict):
            for key, value in dependency_map.items():
                if not isinstance(key, str):
                    raise TypeError('`dependency_map` keys must be strings representing the names of the dependencies in the dependency expression.')  # noqa: E501
                if not isinstance(value, DescriptorNumber):
                    raise TypeError(f'`dependency_map` values must be DescriptorNumbers or Parameters. Got {type(value)} for {key}.')  # noqa: E501

        # If we're overwriting the dependency, store the old attributes
        # in case we need to revert back to the old dependency
        self._previous_independent = self._independent
        if not self._independent:
            self._previous_dependency = {
                '_dependency_string': self._dependency_string,
                '_dependency_map': self._dependency_map,
                '_dependency_interpreter': self._dependency_interpreter,
                '_clean_dependency_string': self._clean_dependency_string,
            }
            for dependency in self._dependency_map.values():
                dependency._detach_observer(self)

        self._independent = False
        self._dependency_string = dependency_expression
        self._dependency_map = dependency_map if dependency_map is not None else {}
        # List of allowed python constructs for the asteval interpreter
        asteval_config = {'import':         False, 'importfrom':  False, 'assert':         False, 
                          'augassign':      False, 'delete':      False, 'if':             True, 
                          'ifexp':          True,  'for':         False, 'formattedvalue': False, 
                          'functiondef':    False, 'print':       False, 'raise':          False, 
                          'listcomp':       False, 'dictcomp':    False, 'setcomp':        False,
                          'try':            False, 'while':       False, 'with':           False}
        self._dependency_interpreter = Interpreter(config=asteval_config)

        # Process the dependency expression for unique names
        try:
            self._process_dependency_unique_names(self._dependency_string)
        except ValueError as error:
            self._revert_dependency(skip_detach=True)
            raise error

        for key, value in self._dependency_map.items():
                self._dependency_interpreter.symtable[key] = value
                self._dependency_interpreter.readonly_symbols.add(key) # Dont allow overwriting of the dependencies in the dependency expression  # noqa: E501
                value._attach_observer(self)
        # Check the dependency expression for errors
        try:
            dependency_result = self._dependency_interpreter.eval(self._clean_dependency_string, raise_errors=True)
        except NameError as message:
            self._revert_dependency()
            raise NameError('\nUnknown name encountered in dependecy expression:'+
                            '\n'+'\n'.join(str(message).split("\n")[1:])+
                            '\nPlease check your expression or add the name to the `dependency_map`') from None
        except Exception as message:
            self._revert_dependency()
            raise SyntaxError('\nError encountered in dependecy expression:'+
                            '\n'+'\n'.join(str(message).split("\n")[1:])+
                            '\nPlease check your expression') from None
        if not isinstance(dependency_result, DescriptorNumber):
            error_string = self._dependency_string
            self._revert_dependency()
            raise TypeError(f'The dependency expression: "{error_string}" returned a {type(dependency_result)}, it should return a Parameter or DescriptorNumber.')  # noqa: E501
        # Check for cyclic dependencies
        try:
            self._validate_dependencies()
        except RuntimeError as error:
            self._revert_dependency()
            raise error
        # Update the parameter with the dependency result
        self._fixed = False
        self._update()

    def make_independent(self) -> None:
        """
        Make this parameter independent.
        This will remove the dependency expression, the dependency map and the dependency interpreter.

        :return: None
        """
        if not self._independent:
            for dependency in self._dependency_map.values():
                dependency._detach_observer(self)
            self._independent = True
            del self._dependency_map
            del self._dependency_interpreter
            del self._dependency_string
            del self._clean_dependency_string
        else:
            raise AttributeError('This parameter is already independent.')

    @property
    def independent(self) -> bool:
        """
        Is the parameter independent?

        :return: True = independent, False = dependent
        """
        return self._independent
    
    @independent.setter
    def independent(self, value: bool) -> None:
        raise AttributeError('This property is read-only. Use `make_independent` and  `make_dependent_on` to change the state of the parameter.')  # noqa: E501

    @property
    def dependency_expression(self) -> str:
        """
        Get the dependency expression of this parameter.

        :return: The dependency expression of this parameter.
        """
        if not self._independent:
            return self._dependency_string
        else:
            raise AttributeError('This parameter is independent. It has no dependency expression.')
        
    @dependency_expression.setter
    def dependency_expression(self, new_expression: str) -> None:
        raise AttributeError('Dependency expression is read-only. Use `make_dependent_on` to change the dependency expression.')  # noqa: E501

    @property
    def dependency_map(self) -> Dict[str, DescriptorNumber]:
        """
        Get the dependency map of this parameter.

        :return: The dependency map of this parameter.
        """
        if not self._independent:
            return self._dependency_map
        else:
            raise AttributeError('This parameter is independent. It has no dependency map.')
        
    @dependency_map.setter
    def dependency_map(self, new_map: Dict[str, DescriptorNumber]) -> None:
        raise AttributeError('Dependency map is read-only. Use `make_dependent_on` to change the dependency map.')

    @property
    def value_no_call_back(self) -> numbers.Number:
        """
        Get the currently hold value of self suppressing call back.

        :return: Value of self without unit.
        """
        return self._scalar.value

    @property
    def full_value(self) -> Variable:
        """
        Get the value of self as a scipp scalar. This is should be usable for most cases.
        If a scipp scalar is not acceptable then the raw value can be obtained through `obj.value`.

        :return: Value of self with unit and variance.
        """
        if self._callback.fget is not None:
            scalar = self._callback.fget()
            if scalar != self._scalar:
                self._scalar = scalar
        return self._scalar

    @full_value.setter
    def full_value(self, scalar: Variable) -> None:
        raise AttributeError(
            f'Full_value is read-only. Change the value and variance seperately. Or create a new {self.__class__.__name__}.'
        )  # noqa: E501

    @property
    def value(self) -> numbers.Number:
        """
        Get the value of self as a Number.

        :return: Value of self without unit.
        """
        if self._callback.fget is not None:
            existing_value = self._callback.fget()
            if existing_value != self._scalar.value:
                self._scalar.value = existing_value
        return self._scalar.value

    @value.setter
    @property_stack
    def value(self, value: numbers.Number) -> None:
        """
        Set the value of self. This only updates the value of the scipp scalar.

        :param value: New value of self
        """
        if self._independent:
            if not isinstance(value, numbers.Number):
                raise TypeError(f'{value=} must be a number')
            
            value = float(value)
            if value < self._min.value:
                value = self._min.value
            if value > self._max.value:
                value = self._max.value

            self._scalar.value = value

            if self._callback.fset is not None:
                self._callback.fset(self._scalar.value)

            # Notify observers of the change
            self._notify_observers()
        else:
            raise AttributeError("This is a dependent parameter, its value cannot be set directly.")

    @DescriptorNumber.variance.setter
    def variance(self, variance_float: float) -> None:
        """
        Set the variance.

        :param variance_float: Variance as a float
        """
        if self._independent:
            DescriptorNumber.variance.fset(self, variance_float)
        else:
            raise AttributeError("This is a dependent parameter, its variance cannot be set directly.")

    @DescriptorNumber.error.setter
    def error(self, value: float) -> None:
        """
        Set the standard deviation for the parameter.

        :param value: New error value
        """
        if self._independent:
            DescriptorNumber.error.fset(self, value)
        else:
            raise AttributeError("This is a dependent parameter, its error cannot be set directly.")

    def _convert_unit(self, unit_str: str) -> None:
        """
        Perform unit conversion. The value, max and min can change on unit change.

        :param new_unit: new unit
        :return: None
        """
        super()._convert_unit(unit_str=unit_str)
        new_unit = sc.Unit(unit_str)  # unit_str is tested in super method
        self._min = self._min.to(unit=new_unit)
        self._max = self._max.to(unit=new_unit)

    @notify_observers
    def convert_unit(self, unit_str: str) -> None:
        """
        Perform unit conversion. The value, max and min can change on unit change.

        :param new_unit: new unit
        :return: None
        """
        self._convert_unit(unit_str)

    @property
    def min(self) -> numbers.Number:
        """
        Get the minimum value for fitting.

        :return: minimum value
        """
        return self._min.value

    @min.setter
    @property_stack
    def min(self, min_value: numbers.Number) -> None:
        """
        Set the minimum value for fitting.
        - implements undo/redo functionality.

        :param min_value: new minimum value
        :return: None
        """
        if self._independent:
            if not isinstance(min_value, numbers.Number):
                raise TypeError('`min` must be a number')
            if np.isclose(min_value, self._max.value, rtol=1e-9, atol=0.0):
                raise ValueError('The min and max bounds cannot be identical. Please use fixed=True instead to fix the value.')
            if min_value <= self.value:
                self._min.value = min_value
            else:
                raise ValueError(f'The current value ({self.value}) is smaller than the desired min value ({min_value}).')
            self._notify_observers()
        else:
            raise AttributeError("This is a dependent parameter, its minimum value cannot be set directly.")

    @property
    def max(self) -> numbers.Number:
        """
        Get the maximum value for fitting.

        :return: maximum value
        """
        return self._max.value

    @max.setter
    @property_stack
    def max(self, max_value: numbers.Number) -> None:
        """
        Get the maximum value for fitting.
        - implements undo/redo functionality.

        :param max_value: new maximum value
        :return: None
        """
        if self._independent:
            if not isinstance(max_value, numbers.Number):
                raise TypeError('`max` must be a number')
            if np.isclose(max_value, self._min.value, rtol=1e-9, atol=0.0):
                raise ValueError('The min and max bounds cannot be identical. Please use fixed=True instead to fix the value.')
            if max_value >= self.value:
                self._max.value = max_value
            else:
                raise ValueError(f'The current value ({self.value}) is greater than the desired max value ({max_value}).')
            self._notify_observers()
        else:
            raise AttributeError("This is a dependent parameter, its maximum value cannot be set directly.")

    @property
    def fixed(self) -> bool:
        """
        Can the parameter vary while fitting?

        :return: True = fixed, False = can vary
        """
        return self._fixed

    @fixed.setter
    @property_stack
    def fixed(self, fixed: bool) -> None:
        """
        Change the parameter vary while fitting state.
        - implements undo/redo functionality.

        :param fixed: True = fixed, False = can vary
        """
        if not isinstance(fixed, bool):
            raise ValueError(f'{fixed=} must be a boolean. Got {type(fixed)}')
        if self._independent:
            self._fixed = fixed
        else:
            if self._global_object.stack.enabled:
                # Remove the recorded change from the stack
                global_object.stack.pop()
            raise AttributeError("This is a dependent parameter, dependent parameters cannot be fixed.")

    # Is this alias really needed?
    @property
    def free(self) -> bool:
        return not self.fixed

    @free.setter
    def free(self, value: bool) -> None:
        self.fixed = not value

    def _revert_dependency(self, skip_detach=False) -> None:
        """
        Revert the dependency to the old dependency. This is used when an error is raised during setting the dependency.
        """
        if self._previous_independent is True:
            self.make_independent()
        else:
            if not skip_detach:
                for dependency in self._dependency_map.values():
                    dependency._detach_observer(self)
            for key, value in self._previous_dependency.items():
                setattr(self, key, value)
            for dependency in self._dependency_map.values():
                dependency._attach_observer(self)
            del self._previous_dependency
        del self._previous_independent

    def _process_dependency_unique_names(self, dependency_expression: str):
        """
        Add the unique names of the parameters to the ASTEval interpreter. This is used to evaluate the dependency expression.

        :param dependency_expression: The dependency expression to be evaluated
        """
        # Get the unique_names from the expression string regardless of the quotes used
        inputted_unique_names = re.findall("(\'.+?\')", dependency_expression)
        inputted_unique_names += re.findall('(\".+?\")', dependency_expression)

        clean_dependency_string = dependency_expression
        existing_unique_names = self._global_object.map.vertices()
        # Add the unique names of the parameters to the ASTEVAL interpreter
        for name in inputted_unique_names:
            stripped_name = name.strip("'\"")
            if stripped_name not in existing_unique_names:
                raise ValueError(f'A Parameter with unique_name {stripped_name} does not exist. Please check your dependency expression.') # noqa: E501
            dependent_parameter = self._global_object.map.get_item_by_key(stripped_name)
            if isinstance(dependent_parameter, DescriptorNumber):
                self._dependency_map['__'+stripped_name+'__'] = dependent_parameter
                clean_dependency_string = clean_dependency_string.replace(name, '__'+stripped_name+'__')
            else:
                raise ValueError(f'The object with unique_name {stripped_name} is not a Parameter or DescriptorNumber. Please check your dependency expression.') # noqa: E501
        self._clean_dependency_string = clean_dependency_string

    def __copy__(self) -> Parameter:
        new_obj = super().__copy__()
        new_obj._callback = property()
        return new_obj

    def __repr__(self) -> str:
        """
        Return printable representation of a Parameter object.
        """
        super_str = super().__repr__()
        super_str = super_str[:-1]
        s = []
        if self.fixed:
            super_str += ' (fixed)'
        s.append(super_str)
        s.append('bounds=[%s:%s]' % (repr(float(self.min)), repr(float(self.max))))
        return '%s>' % ', '.join(s)

    # Seems redundant
    # def __float__(self) -> float:
    #     return float(self._scalar.value)

    def __add__(self, other: Union[DescriptorNumber, Parameter, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            if self.unit != 'dimensionless':
                raise UnitError('Numbers can only be added to dimensionless values')
            new_full_value = self.full_value + other
            min_value = self.min + other
            max_value = self.max + other
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            other_unit = other.unit
            try:
                other._convert_unit(self.unit)
            except UnitError:
                raise UnitError(f'Values with units {self.unit} and {other.unit} cannot be added') from None
            new_full_value = self.full_value + other.full_value
            min_value = self.min + other.min if isinstance(other, Parameter) else self.min + other.value
            max_value = self.max + other.max if isinstance(other, Parameter) else self.max + other.value
            other._convert_unit(other_unit)
        else:
            return NotImplemented
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter

    def __radd__(self, other: Union[DescriptorNumber, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            if self.unit != 'dimensionless':
                raise UnitError('Numbers can only be added to dimensionless values')
            new_full_value = self.full_value + other
            min_value = self.min + other
            max_value = self.max + other
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            original_unit = self.unit
            try:
                self._convert_unit(other.unit)
            except UnitError:
                raise UnitError(f'Values with units {other.unit} and {self.unit} cannot be added') from None
            new_full_value = self.full_value + other.full_value
            min_value = self.min + other.value
            max_value = self.max + other.value
            self._convert_unit(original_unit)
        else:
            return NotImplemented
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter

    def __sub__(self, other: Union[DescriptorNumber, Parameter, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            if self.unit != 'dimensionless':
                raise UnitError('Numbers can only be subtracted from dimensionless values')
            new_full_value = self.full_value - other
            min_value = self.min - other
            max_value = self.max - other
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            other_unit = other.unit
            try:
                other._convert_unit(self.unit)
            except UnitError:
                raise UnitError(f'Values with units {self.unit} and {other.unit} cannot be subtracted') from None
            new_full_value = self.full_value - other.full_value
            if isinstance(other, Parameter):
                min_value = self.min - other.max if other.max != np.inf else -np.inf
                max_value = self.max - other.min if other.min != -np.inf else np.inf
            else:
                min_value = self.min - other.value
                max_value = self.max - other.value
            other._convert_unit(other_unit)
        else:
            return NotImplemented
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter

    def __rsub__(self, other: Union[DescriptorNumber, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            if self.unit != 'dimensionless':
                raise UnitError('Numbers can only be subtracted from dimensionless values')
            new_full_value = other - self.full_value
            min_value = other - self.max
            max_value = other - self.min
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            original_unit = self.unit
            try:
                self._convert_unit(other.unit)
            except UnitError:
                raise UnitError(f'Values with units {other.unit} and {self.unit} cannot be subtracted') from None
            new_full_value = other.full_value - self.full_value
            min_value = other.value - self.max
            max_value = other.value - self.min
            self._convert_unit(original_unit)
        else:
            return NotImplemented
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter

    def __mul__(self, other: Union[DescriptorNumber, Parameter, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            new_full_value = self.full_value * other
            if other == 0:
                descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
                descriptor_number.name = descriptor_number.unique_name
                return descriptor_number
            combinations = [self.min * other, self.max * other]
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            new_full_value = self.full_value * other.full_value
            if (
                other.value == 0 and type(other) is DescriptorNumber
            ):  # Only return DescriptorNumber if other is strictly 0, i.e. not a parameter  # noqa: E501
                descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
                descriptor_number.name = descriptor_number.unique_name
                return descriptor_number
            if isinstance(other, Parameter):
                combinations = []
                for first, second in [
                    (self.min, other.min),
                    (self.min, other.max),
                    (self.max, other.min),
                    (self.max, other.max),
                ]:  # noqa: E501
                    if first == 0 and np.isinf(second):
                        combinations.append(0)
                    elif second == 0 and np.isinf(first):
                        combinations.append(0)
                    else:
                        combinations.append(first * second)
            else:
                combinations = [self.min * other.value, self.max * other.value]
        else:
            return NotImplemented
        min_value = min(combinations)
        max_value = max(combinations)
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter._convert_unit(parameter._base_unit())
        parameter.name = parameter.unique_name
        return parameter

    def __rmul__(self, other: Union[DescriptorNumber, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            new_full_value = other * self.full_value
            if other == 0:
                descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
                descriptor_number.name = descriptor_number.unique_name
                return descriptor_number
            combinations = [other * self.min, other * self.max]
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            new_full_value = other.full_value * self.full_value
            if other.value == 0:
                descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
                descriptor_number.name = descriptor_number.unique_name
                return descriptor_number
            combinations = [self.min * other.value, self.max * other.value]
        else:
            return NotImplemented
        min_value = min(combinations)
        max_value = max(combinations)
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter._convert_unit(parameter._base_unit())
        parameter.name = parameter.unique_name
        return parameter

    def __truediv__(self, other: Union[DescriptorNumber, Parameter, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            if other == 0:
                raise ZeroDivisionError('Cannot divide by zero')
            new_full_value = self.full_value / other
            combinations = [self.min / other, self.max / other]
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            other_value = other.value
            if other_value == 0:
                raise ZeroDivisionError('Cannot divide by zero')
            new_full_value = self.full_value / other.full_value
            if isinstance(other, Parameter):
                if other.min < 0 and other.max > 0:
                    combinations = [-np.inf, np.inf]
                elif other.min == 0:
                    if self.min < 0 and self.max > 0:
                        combinations = [-np.inf, np.inf]
                    elif self.min >= 0:
                        combinations = [self.min / other.max, np.inf]
                    elif self.max <= 0:
                        combinations = [-np.inf, self.max / other.max]
                elif other.max == 0:
                    if self.min < 0 and self.max > 0:
                        combinations = [-np.inf, np.inf]
                    elif self.min >= 0:
                        combinations = [-np.inf, self.min / other.min]
                    elif self.max <= 0:
                        combinations = [self.max / other.min, np.inf]
                else:
                    combinations = [self.min / other.min, self.max / other.max, self.min / other.max, self.max / other.min]
            else:
                combinations = [self.min / other.value, self.max / other.value]
            other.value = other_value
        else:
            return NotImplemented
        min_value = min(combinations)
        max_value = max(combinations)
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter._convert_unit(parameter._base_unit())
        parameter.name = parameter.unique_name
        return parameter

    def __rtruediv__(self, other: Union[DescriptorNumber, numbers.Number]) -> Parameter:
        original_self = self.value
        if original_self == 0:
            raise ZeroDivisionError('Cannot divide by zero')
        if isinstance(other, numbers.Number):
            new_full_value = other / self.full_value
            other_value = other
            if other_value == 0:
                descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
                descriptor_number.name = descriptor_number.unique_name
                return descriptor_number
        elif isinstance(other, DescriptorNumber):  # Parameter inherits from DescriptorNumber and is also handled here
            new_full_value = other.full_value / self.full_value
            other_value = other.value
            if other_value == 0:
                descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
                descriptor_number.name = descriptor_number.unique_name
                return descriptor_number
        else:
            return NotImplemented
        if self.min < 0 and self.max > 0:
            combinations = [-np.inf, np.inf]
        elif self.min == 0:
            if other_value > 0:
                combinations = [other_value / self.max, np.inf]
            elif other_value < 0:
                combinations = [-np.inf, other_value / self.max]
        elif self.max == 0:
            if other_value > 0:
                combinations = [-np.inf, other_value / self.min]
            elif other_value < 0:
                combinations = [other_value / self.min, np.inf]
        else:
            combinations = [other_value / self.min, other_value / self.max]
        min_value = min(combinations)
        max_value = max(combinations)
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter._convert_unit(parameter._base_unit())
        parameter.name = parameter.unique_name
        self.value = original_self
        return parameter

    def __pow__(self, other: Union[DescriptorNumber, numbers.Number]) -> Parameter:
        if isinstance(other, numbers.Number):
            exponent = other
        elif type(other) is DescriptorNumber:  # Strictly a DescriptorNumber, We can't raise to the power of a Parameter
            if other.unit != 'dimensionless':
                raise UnitError('Exponents must be dimensionless')
            if other.variance is not None:
                raise ValueError('Exponents must not have variance')
            exponent = other.value
        else:
            return NotImplemented

        try:
            new_full_value = self.full_value**exponent
        except Exception as message:
            raise message from None

        if np.isnan(new_full_value.value):
            raise ValueError('The result of the exponentiation is not a number')
        if exponent == 0:
            descriptor_number = DescriptorNumber.from_scipp(name=self.name, full_value=new_full_value)
            descriptor_number.name = descriptor_number.unique_name
            return descriptor_number
        elif exponent < 0:
            if self.min < 0 and self.max > 0:
                combinations = [-np.inf, np.inf]
            elif self.min == 0:
                combinations = [self.max**exponent, np.inf]
            elif self.max == 0:
                combinations = [-np.inf, self.min**exponent]
            else:
                combinations = [self.min**exponent, self.max**exponent]
        else:
            combinations = [self.min**exponent, self.max**exponent]
        if exponent % 2 == 0:
            if self.min < 0 and self.max > 0:
                combinations.append(0)
            combinations = [abs(combination) for combination in combinations]
        elif exponent % 1 != 0:
            if self.min < 0:
                combinations.append(0)
            combinations = [combination for combination in combinations if combination >= 0]
        min_value = min(combinations)
        max_value = max(combinations)
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter

    def __neg__(self) -> Parameter:
        new_full_value = -self.full_value
        min_value = -self.max
        max_value = -self.min
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter

    def __abs__(self) -> Parameter:
        new_full_value = abs(self.full_value)
        combinations = [abs(self.min), abs(self.max)]
        if self.min < 0 and self.max > 0:
            combinations.append(0)
        min_value = min(combinations)
        max_value = max(combinations)
        parameter = Parameter.from_scipp(name=self.name, full_value=new_full_value, min=min_value, max=max_value)
        parameter.name = parameter.unique_name
        return parameter
