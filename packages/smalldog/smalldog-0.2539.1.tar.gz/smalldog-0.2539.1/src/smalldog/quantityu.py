import os
# import sys
import inspect
# import traceback
import numpy as np
import datetime as dt
# import uuid
import warnings, traceback

import astropy.units as u
from astropy import uncertainty as unc

from .temptoolclass_version import HeadVer
from .temptoolclass_pydocument import PyDocument
from .valueu import ValueU

class QuantityU:
    __fullname = 'Quantity tagged with Uncertainty'
    __firstwritten = dt.datetime.strptime('2023-09-06', '%Y-%m-%d')
    __lastupdate = dt.datetime.strptime('2025-08-26', '%Y-%m-%d')
    __version = HeadVer(1, __lastupdate, 0)
    __developer = {'name': 'DH.Koh', 'contact': 'donghyeok.koh.code@gmail.com'}
    __collaborators = [{'name': 'JH.Kim', 'contact': None}, {'name': 'KM.Heo', 'contact': None}]
    __contributors = [{'name': None, 'role': 'alpha tester'}]
    __callsign = 'Quantity(+/-)'

    __versiondependency = {}

    __array_priority__ = 12000
    _n_samples = None  # Number of samples for uncertainty distribution
    _n_samples_defaultvalue = ValueU._n_samples_defaultvalue  # Default value of __n_samples
    # Sync with ValueU's n_samplesif n_samples is None

    def __init__(self, center=None, std=None, n_samples=None):
        # self.__id = uuid.uuid4()  # time.perf_counter_ns()

        if std is None:
            std = np.nan * u.dimensionless_unscaled
        if center is None:
            center = np.nan * u.dimensionless_unscaled
        if n_samples is None:
            if QuantityU._n_samples is None:
                QuantityU._n_samples = QuantityU._n_samples_defaultvalue  # Default number of samples for uncertainty distribution
        else:
            if QuantityU._n_samples is None:
                QuantityU._n_samples = n_samples
            elif QuantityU._n_samples == n_samples:
                pass
            else:
                raise ValueError(f'number of sample \"n_samples\" already set to {QuantityU._n_samples}, cannot be changed to {n_samples}.')
        self._comparison_criterion_by_center = True
        self._comparison_criterion_threshold = None
        self.enforced_positive = None
        self.enforced_negative = None

        ### initialize
        self.unit = u.dimensionless_unscaled
        self.value = ValueU(n_samples=self._n_samples)
        self.distribution = unc.Distribution([np.nan]) * self.unit

        ### recognize value
        produced_distribution = self._produce_distribution(center=center, std=std)

        self._digit_round = 5
        self._digit_stringformat = 8

        return None

    def _sync_info(self):
        self._n_samples = self.distribution.distribution.shape[-1]
        # assert self._n_samples == self.distribution.distribution.shape[-1], 'The shape of the distribution does not match the static number of samples.'

        """
        [***ToDo**_] (25-08-20) - 값의 분포를 음수 또는 양수로 강제하는 클래스 변수 구현 필요, None으로 임시조치
        """
        self.enforced_positive = None
        self.enforced_negative = None

        self.unit = self.center.unit
        self.value = ValueU(n_samples=self._n_samples).set_manual(center=self.center.value, distribution=unc.Distribution(self.distribution.distribution.value))

        return self

    def set_manual(self, center=None, distribution: unc.Distribution = None):
        if isinstance(center, unc.Distribution):
            raise TypeError(f'The input argument \"center\" should not be an instance of {unc.Distribution}.')
        if not isinstance(distribution, unc.Distribution):
            raise TypeError(f'The input argument \"distribution\" should be an instance of {unc.Distribution}.')

        if center is None:
            warnings.warn(
                message=f'{self.__callsign.ljust(10)} : Center value not provided; automatically set to the median of the distribution.',
                category=UserWarning,
                stacklevel=2
            )
            traceback.print_stack(limit=2)
            center = distribution.pdf_median()

        center_temp = center if isinstance(center, u.Quantity) else center * u.dimensionless_unscaled
        distribution_temp = distribution if isinstance(distribution, u.Quantity) else distribution * u.dimensionless_unscaled

        assert center_temp.unit.is_equivalent(distribution_temp.unit),\
            'The unit of the center value must be equivalent to the unit of the distribution.'

        self.center = center_temp
        self.distribution = distribution_temp

        dummyvalue_synchronized = self._sync_info()

        return self

    def __produce_distribution_symmetric(self, center=None, std=None):
        """
        Private Method
        Produce a symmetric distribution object 'self.distribution' from the input regulated information with unit.
        usage :
        $ >>> self.__produce_distribution_symmetric(center=10, std=1)
        """
        assert center.unit == std.unit, f'Input argument \"std\" unit {std.unit} is not equivalent to the center value unit {center.unit}.'
        self.center, self.unit = center, center.unit

        distribution_produced = unc.normal(center=self.center, std=std, n_samples=self._n_samples)

        self.distribution = distribution_produced.to(self.unit)

    def __produce_distribution_asymmetric(self, center=None, stds: np.ndarray = None):
        """
        Private Method
        Produce an asymmetric distribution object 'self.distribution' from the input regulated information with unit.
        usage :
        $ >>> self.__produce_distribution_asymmetric(center=10, std=np.array([1, 2]))
        """
        assert center.unit == stds.unit, f'Input argument \"stds\" unit {stds.unit} is not equivalent to the center value unit {center.unit}.'
        self.center, self.unit = center, center.unit

        distribution_produced_primary = unc.normal(center=0 * self.unit, std=stds[1], n_samples=self._n_samples
        )
        distribution_produced_secondary = unc.Distribution(
            np.where(
                distribution_produced_primary.distribution < 0,
                distribution_produced_primary.distribution * np.abs(stds[0] / stds[1]),
                distribution_produced_primary.distribution
            )
        )
        distribution_produced = (self.center + distribution_produced_secondary)

        self.distribution = distribution_produced.to(self.unit)

    def _produce_distribution(self, center, std: np.ndarray):
        """
        Protected Method
        categorize and process the input standard deviation
        impossible to handle an input variable that is not structured as a shape twice the size of the central value
        impossible to handle an input variable that cannot be processed as a numpy ndarray object
        transport processed dispersion range to 'self.__produce_distribution_asymmetric' or 'self.__produce_distribution_symmetric'
        usage :
        $ >>> v = ValueU(10)
        $ ... print(repr(v))
        $ ValueU(10, (nan, nan))
        $ >>> v._set_error_relative([-1, 2])
        $ ValueU(5, (-1, +2))
        """

        if isinstance(std, np.ndarray):
            if std.shape == (2,):
                ### Case (a-1) std= array([-number, +number])
                if isinstance(center, u.quantity.Quantity):
                    if isinstance(std, u.quantity.Quantity):
                        if center.unit.is_equivalent(std.unit):
                            self.__produce_distribution_asymmetric(center=center, stds=std.to(center.unit))
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" unit {std.unit} is not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_asymmetric(center=center, stds=std * center.unit)
                else:
                    if isinstance(std, u.quantity.Quantity):
                        self.__produce_distribution_asymmetric(center=center * std.unit, stds=std)
                    else:
                        self.__produce_distribution_asymmetric(center=center * u.dimensionless_unscaled, stds=std * u.dimensionless_unscaled)
            elif std.shape == (1,):
                ### Case (a-2) std= array([number])
                if isinstance(center, u.quantity.Quantity):
                    if isinstance(std, u.quantity.Quantity):
                        if center.unit.is_equivalent(std.unit):
                            self.__produce_distribution_symmetric(center=center, std=std[0].to(center.unit))
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" unit {std.unit} is not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_symmetric(center=center, std=std[0] * center.unit)
                else:
                    if isinstance(std, u.quantity.Quantity):
                        self.__produce_distribution_symmetric(center=center * std.unit, std=std[0])
                    else:
                        self.__produce_distribution_symmetric(center=center * u.dimensionless_unscaled, std=std[0] * u.dimensionless_unscaled)
            elif np.prod(std.shape) / np.prod(np.array(center).shape) == 2.:
                ### Case (a-3) std= [[-number1, +number2, ...], [+number1, +number2, ...]]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not std.shape == ((2,) + np.array(center).shape):
                    raise ValueError(f'Input argument \"stddev\" shape not matched with two times repeated shape of the center value')
                if isinstance(center, u.quantity.Quantity):
                    if isinstance(std, u.quantity.Quantity):
                        if center.unit.is_equivalent(std.unit):
                            self.__produce_distribution_asymmetric(center=center, stds=([std.value[0], std.value[1]] * std.unit).to(center.unit))
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" unit {std.unit} is not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_asymmetric(center=center, stds=[std[0], std[1]] * center.unit)
                else:
                    if isinstance(std, u.quantity.Quantity):
                        self.__produce_distribution_asymmetric(center=center * std.unit, stds=[std.value[0], std.value[1]] * std.unit)
                    else:
                        self.__produce_distribution_asymmetric(center=center * u.dimensionless_unscaled, stds=[std[0], std[1]] * u.dimensionless_unscaled)
            elif np.prod(std.shape) / np.prod(np.array(center).shape) == 1.:
                ### Case (a-4) std= [-number1, +number2, ...]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not std.shape == np.array(center).shape:
                    raise ValueError(f'Input argument \"stddev\" shape not matched with the center value')
                if isinstance(center, u.quantity.Quantity):
                    if isinstance(std, u.quantity.Quantity):
                        if center.unit.is_equivalent(std.unit):
                            self.__produce_distribution_symmetric(center=center, std=std.to(center.unit))
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" unit {std.unit} is not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_symmetric(center=center, std=std * center.unit)
                else:
                    if isinstance(std, u.quantity.Quantity):
                        self.__produce_distribution_symmetric(center=center * std.unit, std=std)
                    else:
                        self.__produce_distribution_symmetric(center=center * u.dimensionless_unscaled, std=std * u.dimensionless_unscaled)
            else:
                raise ValueError(f'Input argument \"std\" wrong - should be a number pair (ndarray) or the same structure as the center value')
        elif isinstance(std, list) or isinstance(std, tuple):
            if len(std) == 2:
                ### Case (b-1) std= [-number, +number]
                std_isquantity = [isinstance(element, u.quantity.Quantity) for element in std]
                if isinstance(center, u.quantity.Quantity):
                    if std_isquantity[0] and std_isquantity[1]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center, stds=[std[0].to(center.unit).value, std[1].to(center.unit).value] * center.unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[0]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center, stds=[std[0].to(center.unit).value, std[1]] * center.unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[1]:
                        if center.unit.is_equivalent(std[1].unit):
                            self.__produce_distribution_asymmetric(center=center, stds=[std[0], std[1].to(center.unit).value] * center.unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[1]}, not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_asymmetric(center=center, stds=std * center.unit)
                else:
                    if std_isquantity[0] and std_isquantity[1]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center * std[0].unit, stds=[std[0].value, std[1].value] * std[0].unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[0]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center * std[0].unit, stds=[std[0].value, std[1]] * std[0].unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[1]:
                        if center.unit.is_equivalent(std[1].unit):
                            self.__produce_distribution_asymmetric(center=center * std[1].unit, stds=[std[0], std[1].value] * std[1].unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[1]}, not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_asymmetric(center=center * u.dimensionless_unscaled, stds=std * u.dimensionless_unscaled)
            elif len(std) == 1:
                ### Case (b-2) std= [number]
                if isinstance(center, u.quantity.Quantity):
                    if isinstance(std[0], u.quantity.Quantity):
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_symmetric(center=center, std=std[0].to(center.unit))
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" unit {std[0].unit} is not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_symmetric(center=center, std=std[0] * center.unit)
                else:
                    if isinstance(std[0], u.quantity.Quantity):
                        self.__produce_distribution_symmetric(center=center * std[0].unit, std=std[0])
                    else:
                        self.__produce_distribution_symmetric(center=center * u.dimensionless_unscaled, std=std[0] * u.dimensionless_unscaled)
            elif np.prod(np.array(std).shape) / np.prod(np.array(self.center).shape) == 2.:
                ### Case (b-3) std= [[-number1, +number2, ...], [+number1, +number2, ...]]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not np.array(std).shape == ((2,) + np.array(self.center).shape):
                    raise ValueError(f'Input argument \"stddev\" shape not matched with two times repeated shape of the center value')
                std_isquantity = [isinstance(element, u.quantity.Quantity) for element in std]
                if isinstance(center, u.quantity.Quantity):
                    if std_isquantity[0] and std_isquantity[1]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center, stds=[std[0].to(center.unit).value, std[1].to(center.unit).value] * center.unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[0]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center, stds=[std[0].to(center.unit).value, std[1]] * center.unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[1]:
                        if center.unit.is_equivalent(std[1].unit):
                            self.__produce_distribution_asymmetric(center=center, stds=[std[0], std[1].to(center.unit).value] * center.unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[1]}, not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_asymmetric(center=center, stds=std * center.unit)
                else:
                    if std_isquantity[0] and std_isquantity[1]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center * std[0].unit, stds=[std[0].value, std[1].value] * std[0].unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[0]:
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_asymmetric(center=center * std[0].unit, stds=[std[0].value, std[1]] * std[0].unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[0]}, not equivalent to the center value unit {center.unit}.')
                    elif std_isquantity[1]:
                        if center.unit.is_equivalent(std[1].unit):
                            self.__produce_distribution_asymmetric(center=center * std[1].unit, stds=[std[0], std[1].value] * std[1].unit)
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" has an unit {std.unit[1]}, not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_asymmetric(center=center * u.dimensionless_unscaled, stds=std * u.dimensionless_unscaled)
            elif np.prod(np.array(std).shape) / np.prod(np.array(self.center).shape) == 1.:
                ### Case (b-4) std= [-number1, +number2, ...]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not np.array(std).shape == np.array(self.center).shape:
                    raise ValueError(f'Input argument \"stddev\" shape not matched with the center value')

                if isinstance(center, u.quantity.Quantity):
                    if isinstance(std[0], u.quantity.Quantity):
                        if center.unit.is_equivalent(std[0].unit):
                            self.__produce_distribution_symmetric(center=center, stds=std[0].to(center.unit))
                        else:
                            raise u.core.UnitsError(f'Input argument \"stddev\" unit {std[0].unit} is not equivalent to the center value unit {center.unit}.')
                    else:
                        self.__produce_distribution_symmetric(center=center, stds=std[0] * center.unit)
                else:
                    if isinstance(std[0], u.quantity.Quantity):
                        self.__produce_distribution_symmetric(center=center * std[0].unit, stds=std[0])
                    else:
                        self.__produce_distribution_symmetric(center=center * u.dimensionless_unscaled, stds=std[0] * u.dimensionless_unscaled)
            else:
                raise ValueError(f'Input argument \"std\" wrong - should be a number pair (list) or the same structure as the center value')
        elif isinstance(std, int) or isinstance(std, float):
            ### Case (c) std= number
            if isinstance(center, u.quantity.Quantity):
                if isinstance(std, u.quantity.Quantity):
                    self.__produce_distribution_symmetric(center=center, std=std.to(center.unit))
                else:
                    self.__produce_distribution_symmetric(center=center, std=std * center.unit)
            else:
                if isinstance(std, u.quantity.Quantity):
                    self.__produce_distribution_symmetric(center=center * std.unit, std=std)
                else:
                    self.__produce_distribution_symmetric(center=center * u.dimensionless_unscaled, std=std * u.dimensionless_unscaled)
        else:
            raise ValueError(f'Input argument \"std\" wrong - should be a number pair or the same structure as the center value')

        dummyvalue_synchronized = self._sync_info()

        return self

    def resample(self, n_samples=None):
        dummyvalue_synchronized = self._sync_info()

        self_resampled = self.__class__().set_manual(
            center=self.center,
            distribution=unc.Distribution(self.distribution.distribution[(np.random.random(n_samples) * self._n_samples).astype('int')])
        ).set_digit(
            digit_round=self._digit_round,
            digit_stringformat=self._digit_stringformat,
        )

        return self_resampled

    def _sync_nsamples(self, other):
        """
        [Describe] - 다른 ValueU 인스턴스와 n_samples를 동기화합니다.
        만약 다른 인스턴스의 n_samples가 None이라면, 현재 인스턴스의 n_samples를 사용합니다.
        """
        assert 'n_samples' in dir(other), f'Not valid type {type(other)} of {other} for operation method \"{inspect.getframeinfo(inspect.currentframe()).function}\"'
        raise NotImplementedError('***ToDo*** Resampling method is not implemented yet.')

        n_samples_self = self._sync_info()._n_samples
        n_samples_other = other._sync_info()._n_samples

        if n_samples_self > n_samples_other:
            result_resampled = self.resample(n_samples_other)
        elif n_samples_self < n_samples_other:
            if n_samples_self / n_samples_other == 5:
                result_resampled = self.resample(n_samples_other)
            else:
                raise NotImplementedError('***ToDo*** The method of resampling between ambiguous number of distribution is not implemented yet.')
        else:
            result_resampled = self.copy()

        return result_resampled

    def copy(self):
        self_copied = self.__class__().set_manual(
            center=self.center,
            distribution=self.distribution,
        ).set_digit(
            digit_round=self._digit_round,
            digit_stringformat=self._digit_stringformat,
        )

        return self_copied

    def to(self, unit=None):
        """
        Method for unit decomposition
        calculate instance variables by decomposing their unit into its irreducible parts.
        to support users control the object, by same purpose and manner with 'astropy.units.quantity.Quantity.decompose()'
        usage (exactly same with astropy.units.quantity.Quantity.decompose()):
        $ >>> q = QuantityU(3.26 * u.lyr, 0.5)
        $ ... print(repr(q))
        $ QuantityU(3.26 * u.lyr, (-0.5, +0.5))
        $ >>> print(repr(q.to(u.pc)))
        $ QuantityU(0.99952 * u.pc, (-0.1533, +0.1533))
        """
        if isinstance(unit, u.UnitBase) and unit is not None:
            result = self.__class__().set_manual(
                center=self.center.to(unit),
                distribution=self.distribution.to(unit)
            ).set_digit(
                digit_round=self._digit_round,
                digit_stringformat=self._digit_stringformat
            )
        else:
            raise u.core.UnitsError(f'Input argument \"{unit}\" is not identified as type {u.UnitBase}')

        return result

    def decompose(self):
        """
        Method for unit decomposition
        calculate instance variables by decomposing their unit into its irreducible parts.
        to support users control the object, by same purpose and manner with 'astropy.units.quantity.Quantity.decompose()'
        usage (exactly same with astropy.units.quantity.Quantity.decompose()):
        $ >>> q = QuantityU(1e-10 * u.lyr / (25 * u.km / u.second))
        $ ... print(repr(q))
        $ QuantityU(0.0 * u.lyr * u.s / u.km, (nan, nan))
        $ >>> print(repr(q.decompose()))
        $ QuantityU(37.84292 * u.s, (nan, nan))
        """
        result = self.__class__().set_manual(
            center=self.center.decompose(),
            distribution=self.distribution.decompose()
        ).set_digit(
            digit_round=self._digit_round,
            digit_stringformat=self._digit_stringformat
        )

        return result

    def set_comparison_mode(self, central:bool=False, conservative:bool=False, optimistic:bool=False, percentage:int=None):
        """
        [***ToDo*__] (25-01-24) - 단일문으로 작성시 어테이션 에러 발생할때 도무지 알 수 없는 이유로 스레드가 종료되지 않는 스레딩 에러 발생,
        python3.10/threading.py, line 1567, lock.acquire() \n KeyboardInterrupt:
        assert 열에서 하는 일을 바깥으로 빼내어 일단 안정적으로 작동, 임시방편인지 해결팩인지 확인 필요.
        """
        number_of_true_in_arguments: int = np.sum((central, conservative, optimistic, not percentage is None))
        error_message = f'Only one of these parameters can be set: central (True), conservative (True), optimistic (True), or percentage (\033[3mfloat value\033[0m) for this method ({self.__class__.__name__}.{inspect.getframeinfo(inspect.currentframe()).function})'
        # error_message = f'It is invalid to provide multiple parameters as \'True\' among {["central", "conservative", "upper", "lower"]} for the method {self.__class__.__name__}.{inspect.getframeinfo(inspect.currentframe()).function}.'
        assert number_of_true_in_arguments == 1, error_message

        result = self.copy()
        if central:
            result._comparison_criterion_by_center = True
        else:
            result._comparison_criterion_by_center = False
            if conservative:
                result._comparison_criterion_threshold = 0.9973
            elif optimistic:
                result._comparison_criterion_threshold = 0.6827
            elif percentage is not None:
                result._comparison_criterion_threshold = percentage
            else:
                result._comparison_criterion_by_center = True

        return result

    def __getstate__(self):
        stateinfo_sleeping = {
            'center': self.center,
            'distribution': self.distribution.distribution,
            'digits': [self._digit_round, self._digit_stringformat],
        }

        return stateinfo_sleeping

    def __setstate__(self, stateinfo):
        self_wakeing = self.set_manual(
            center=stateinfo['center'],
            distribution=unc.Distribution(stateinfo['distribution']),
        ).set_digit(
            digit_round=stateinfo['digits'][0],
            digit_stringformat=stateinfo['digits'][1],
        )



    def __add__(self, other):  ## self + other
        """
        [Describe] - 가산연산에서 self.unit과 other.unit의 physical type이 다르면 연산 불가능하다.
        self.unit과 other.unit이 상호 호환되지 않는 physical type인 경우를 별도 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.
        """
        if isinstance(other, self.__class__):
            result = self.__class__().set_manual(
                center=self.center + other.center,
                distribution=self.distribution + other.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        elif isinstance(other, ValueU):
            # 위의 if와 합칠 수 있으나, 향후 유지보수를 위해 존치. 아마 이게 더 빠를 수도 있음
            result = self.__class__().set_manual(
                center=self.center + other.center,
                distribution=self.distribution + other.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        elif isinstance(other, u.quantity.Quantity):
            # else에서 같은 작업을 하기 때문에 필요하지 않으나, 향후 유지보수를 위해 존치
            result = self.__class__().set_manual(
                center=self.center + other,
                distribution=self.distribution + other,
            ).set_digit(
                digit_round=self._digit_round,
                digit_stringformat=self._digit_stringformat,
            )
        else:
            result = self.__class__().set_manual(
                center=self.center + other,
                distribution=self.distribution + other,
            ).set_digit(
                digit_round=self._digit_round,
                digit_stringformat=self._digit_stringformat,
            )

        return result

    def __radd__(self, other):  ## other + self
        return self.__add__(other)

    """
    [Describe] - 비슷한 작동을 하는 __add__를 부호만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __sub__(self, other):  ## self - other
    #     """
    #     [___ToDo*__] (25-02-03) - 어차피 부호만 다르고 계산 접근방식이 같다면 별개 내용을 구현하기보단 __neg__와 __add__를 이용하도록 구현하는게 나을까?
    #     만약 그렇게 하기로 결정한다면, __add__에서 인수를 반드시 매번 독립변수로 취급되도록 설계되어야만 한다.
    #     어쨋든 현재 설계로는 __neg__와 __add__를 이용해 가감연산을 전적으로 __add__에 의지하는 것이 가능할 것으로 보이지만,
    #     이 제안이 좋은 구현인지, 논리적으로 정확한 구현인지 아닌지는 더 고민해봐야 하는 문제임.
    #     이러한 문제는 ValueU.__sub__ 에서도 동일함
    #
    #     [Describe] - 가감연산에서 self.unit과 other.unit의 physical type이 다르면 연산 불가능하다.
    #     self.unit과 other.unit이 상호 호환되지 않는 physical type인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.
    #     """
    #     if isinstance(other, self.__class__):
    #         result = self.__class__().set_manual(
    #             center=self.center - other.center,
    #             distribution=self.distribution - other.distribution,
    #         ).set_digit(
    #             digit_round=max(self._digit_round, other._digit_round),
    #             digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
    #         )
    #     elif isinstance(other, ValueU):
    #         # 위의 if와 합칠 수 있으나, 향후 유지보수를 위해 존치. 아마 이게 더 빠를 수도 있음
    #         result = self.__class__().set_manual(
    #             center=self.center - other.center,
    #             distribution=self.distribution.distribution - other.distribution,
    #         ).set_digit(
    #             digit_round=max(self._digit_round, other._digit_round),
    #             digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
    #         )
    #     elif isinstance(other, u.quantity.Quantity):
    #         # else에서 같은 작업을 하기 때문에 필요하지 않으나, 향후 유지보수를 위해 존치
    #         result = self.__class__().set_manual(
    #             center=self.center - other,
    #             distribution=self.distribution - other,
    #         ).set_digit(
    #             digit_round=self._digit_round,
    #             digit_stringformat=self._digit_stringformat,
    #         )
    #     else:
    #         result = self.__class__().set_manual(
    #             center=self.center - other,
    #             distribution=self.distribution - other,
    #         ).set_digit(
    #             digit_round=self._digit_round,
    #             digit_stringformat=self._digit_stringformat,
    #         )
    #
    #     return result

    def __neg__(self):  ## -self
        result = self.__class__().set_manual(center=-self.center, distribution=-self.distribution,).set_digit(self._digit_round, self._digit_stringformat,)
        return result

    def __sub__(self, other):  ## self - other
        return self.__add__(other.__neg__())

    def __rsub__(self, other):  ## other - self
        return self.__neg__().__add__(other)

    def __abs__(self):  ## abs(self)
        if self.center < 0:
            return self.__neg__()
        else:
            return self.copy()

    def __mul__(self, other):  ## self * other
        if isinstance(other, self.__class__):
            result = self.__class__().set_manual(
                center=self.center * other.center,
                distribution=self.distribution * other.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        elif isinstance(other, ValueU):
            # 위의 if와 합칠 수 있으나, 향후 유지보수를 위해 존치. 아마 이게 더 빠를 수도 있음
            result = self.__class__().set_manual(
                center=self.center * other.center,
                distribution=self.distribution * other.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        else:
            result = self.__class__().set_manual(
                center=self.center * other,
                distribution=self.distribution * other,
            ).set_digit(
                digit_round=self._digit_round,
                digit_stringformat=self._digit_stringformat,
            )

        return result

    def __rmul__(self, other):  ## other * self
        return self * other

    """
    [Describe] - 비슷한 작동을 하는 __mull__를 지수만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __truediv__(self, other):
    #     if isinstance(other, self.__class__):
    #         result = self.__class__().set_manual(
    #             center=self.center / other.center,
    #             distribution=self.distribution / other.distribution,
    #         ).set_digit(
    #             digit_round=max(self._digit_round, other._digit_round),
    #             digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
    #         )
    #     elif isinstance(other, ValueU):
    #         # 위의 if와 합칠 수 있으나, 향후 유지보수를 위해 존치. 아마 이게 더 빠를 수도 있음
    #         result = self.__class__().set_manual(
    #             center=self.center / other.center,
    #             distribution=self.distribution / other.distribution,
    #         ).set_digit(
    #             digit_round=max(self._digit_round, other._digit_round),
    #             digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
    #         )
    #     else:
    #         result = self.__class__().set_manual(
    #             center=self.center / other,
    #             distribution=self.distribution / other,
    #         ).set_digit(
    #             digit_round=self._digit_round,
    #             digit_stringformat=self._digit_stringformat,
    #         )
    #
    #     return result

    def __truediv__(self, other):
        return self.__mul__(other.__pow__(-1))

    def __rtruediv__(self, other):
        return self.__pow__(-1).__mul__(other)

    def __pow__(self, other):
        """
        [Describe] - 지수연산에서 other는 단위가 없거나 단위가 dimensionless_unscaled 이어야 한다.
        other가 '지수연산이 불가능한 단위를 가진 객체'인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 에러가 발생하도록 의도함.
        띠리서 other은 반드시 numeric하거나, 단위가 dimensionless_unscaled 이어야 한다.
        """
        if isinstance(other, self.__class__):
            result = self.__class__().set_manual(
                center=self.center ** other.center,
                distribution=self.distribution ** other.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        elif isinstance(other, ValueU):
            # 위의 if와 합칠 수 있으나, 향후 유지보수를 위해 존치. 아마 이게 더 빠를 수도 있음
            result = self.__class__().set_manual(
                center=self.center ** other.center,
                distribution=self.distribution ** other.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        else:
            result = self.__class__().set_manual(
                center=self.center ** other,
                distribution=self.distribution ** other,
            ).set_digit(
                digit_round=self._digit_round,
                digit_stringformat=self._digit_stringformat,
            )

        return result

    def __rpow__(self, other):  ## from other ** self
        """
        [Describe] - 역지수연산에서 self는 단위가 dimensionless인 units.quantity.Quantity의 인스턴스여야 한다.
        따라서 Value.__rpow__()에 해당 케이스를 처리하는 별도의 기능을 구현하지 않고, 부적절한 연산을 시도할 경우 에러가 발생하도록 의도.
        """
        if isinstance(other, self.__class__):
            result = self.__class__().set_manual(
                center=other.center ** self.center,
                distribution=other.distribution ** self.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        elif isinstance(other, ValueU):
            # 위의 if와 합칠 수 있으나, 향후 유지보수를 위해 존치. 아마 이게 더 빠를 수도 있음
            result = self.__class__().set_manual(
                center=other.center ** self.center,
                distribution=other.distribution ** self.distribution,
            ).set_digit(
                digit_round=max(self._digit_round, other._digit_round),
                digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
            )
        else:
            result = self.__class__().set_manual(
                center=other ** self.center,
                distribution=other ** self.distribution,
            ).set_digit(
                digit_round=self._digit_round,
                digit_stringformat=self._digit_stringformat,
            )

        return result



    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.center == other.center and np.all(self.distribution.distribution == other.distribution.distribution)
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            assert self._comparison_criterion_by_center == other._comparison_criterion_by_center and self._comparison_criterion_threshold == other._comparison_criterion_threshold, 'Comparison criteria of two ValueU instances are different. Please set the same comparison criteria using the method \"set_comparison_mode\" before comparison operation.'
            if self._comparison_criterion_by_center:
                comparison = self.center < other.center
            else:
                comparison = np.average(self.distribution.distribution < other.distribution.distribution) > self._comparison_criterion_threshold
        else:
            if self._comparison_criterion_by_center:
                comparison = self.center < other
            else:
                comparison = np.average(self.distribution.distribution < other) > self._comparison_criterion_threshold
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            assert self._comparison_criterion_by_center == other._comparison_criterion_by_center and self._comparison_criterion_threshold == other._comparison_criterion_threshold, 'Comparison criteria of two ValueU instances are different. Please set the same comparison criteria using the method \"set_comparison_mode\" before comparison operation.'
            if self._comparison_criterion_by_center:
                comparison = self.center > other.center
            else:
                comparison = np.average(self.distribution.distribution > other.distribution.distribution) > self._comparison_criterion_threshold
        else:
            if self._comparison_criterion_by_center:
                comparison = self.center > other
            else:
                comparison = np.average(self.distribution.distribution > other) > self._comparison_criterion_threshold
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison

    def __le__(self, other):
        if isinstance(other, self.__class__):
            assert self._comparison_criterion_by_center == other._comparison_criterion_by_center and self._comparison_criterion_threshold == other._comparison_criterion_threshold, 'Comparison criteria of two ValueU instances are different. Please set the same comparison criteria using the method \"set_comparison_mode\" before comparison operation.'
            if self._comparison_criterion_by_center:
                comparison = self.center <= other.center
            else:
                comparison = np.average(self.distribution.distribution <= other.distribution.distribution) > self._comparison_criterion_threshold
        else:
            if self._comparison_criterion_by_center:
                comparison = self.center <= other
            else:
                comparison = np.average(self.distribution.distribution <= other) > self._comparison_criterion_threshold
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            assert self._comparison_criterion_by_center == other._comparison_criterion_by_center and self._comparison_criterion_threshold == other._comparison_criterion_threshold, 'Comparison criteria of two ValueU instances are different. Please set the same comparison criteria using the method \"set_comparison_mode\" before comparison operation.'
            if self._comparison_criterion_by_center:
                comparison = self.center >= other.center
            else:
                comparison = np.average(self.distribution.distribution >= other.distribution.distribution) > self._comparison_criterion_threshold
        else:
            if self._comparison_criterion_by_center:
                comparison = self.center >= other
            else:
                comparison = np.average(self.distribution.distribution >= other) > self._comparison_criterion_threshold
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison



    def __int__(self):
        return self.center.astype('int')

    def __round__(self, rounddigit: int):
        """
        $ >>> q = QuantityU(3.141592653589793 * u.lyr, 0.5)
        $ ... print(repr(round(q, 3)))
        $ QuantityU(3.142 * u.lyr, (-0.5, +0.5))
        """
        result_rounded = self.copy().set_manual(
            center=np.round(self.center, rounddigit),
            distribution=self.distribution
        ).set_digit(
            digit_round=rounddigit,
            digit_stringformat=self._digit_stringformat
        )

        return result_rounded



    def set_digit(self, digit_round=3, digit_stringformat=5):
        if isinstance(digit_round, int):
            self._digit_round = digit_round
        else:
            raise TypeError(f'Input argument \'digit_round\' for \"{__name__}\" type wrong - have not to be {int}')

        if isinstance(digit_stringformat, int):
            self._digit_stringformat = digit_stringformat
        else:
            raise TypeError(f'Input argument \'digit_stringformat\' for \"{__name__}\" type wrong - have not to be {int}')

        self.value.set_digit(digit_round=digit_round, digit_stringformat=digit_stringformat)

        return self

    def help(self):
        pydoc = PyDocument(120)
        print(f'\n{"#" * pydoc.width}\n')

        print(
            f'\033[1m\033[3m\033[4m\033[7m{self.__class__.__name__}\033[0m\033[4m: \033[1m{self.__fullname} (Class) '
            f''.ljust(pydoc.width + 4 * 7 - len(str(self.__class__.__version))) + str(self.__class__.__version) + '\033[0m')
        print(f'last updated at {self.__lastupdate.strftime("%Y-%m-%d")}'.rjust(pydoc.width))

        print(f'\n\033[1m\033[4m{"Introduction:".ljust(25)}\033[0m')
        print(pydoc.f(
            f' {self.__class__.__name__} is a Python class designed to manage variables with uncertainty and physical units.'
            f' It offers versatile functions for manipulating, calculating, and representing values along with their errors, which may not follow a normal distribution.'
            f' {self.__class__.__name__} is an upper-compatible extension of {ValueU.__name__}, adding unit control and representation.'
            f' This package processes results under the assumption of independent variables (zero covariance between uncertainties).'
            f' Dependencies include \'NumPy\', \'Astropy\', and standard Python libraries (e.g., \'os\', \'sys\', \'inspect\', \'datetime\').'
            f' Testing and inspection were performed using \033[1mPython 3.10.14\033[0m, \033[1mNumPy 1.26.4\033[0m, and \033[1mAstropy 6.1.3\033[0m.'
            f' While performance was as anticipated in this environment, results may differ in other settings.'
            f' Additional testing is required to ensure consistent behavior across different configurations.'
        ))
        print('\n        \u2013 How to declare/generate an instance:')
        print(
            f'            $ >>> # import sys, os\n'
            f'            $ ... # sys.path.append(r\'{os.path.dirname(os.path.dirname(__file__))}\')  # *For alpha tester\n'
            f'            $ >>> from {os.path.basename(os.path.dirname(__file__))} import {self.__class__.__name__}\n'
            f'            $ >>> my_first_uncertain_quantity = {self.__class__.__name__}(center=15 * u.m, std=3)\n'
        )
        print(pydoc.f(
            f' The \'__init__()\' method accepts \'central\', \'stddev\', and \'limit\' as input parameters.'
            f' The \'stddev\' can accept array-like objects (lists, tuples, numpy.ndarrays) to represent asymmetric errors.'
            f' A single standard deviation value can be provided if the lower and upper errors are symmetric.'
            f' On the other hand, \'limit\' should accept an array-like input value.'
            f' Note that \'stddev\' and \'limit\' cannot be used simultaneously.'
        ))
        print(' The full set of parameters is:\n')
        print(f'    \u2013 \033[1mCentral\033[0m [float]: \033[4mMean\033[0m value (or representative/\033[4mcentral\033[0m value) with associated unit, serving as the base unit for\n                       other properties.')
        print(f'    \u2013 \033[1mStddev\033[0m [float/float-arr]: \033[4mStandard deviation\033[0m(s) representing relative uncertainty(s) from the central value')
        print(f'    \u2013 \033[1mLimit\033[0m [float-arr]: \033[4mAbsolute range\033[0m(array-like) of uncertainty (lower and upper limits)')
        print('')
        print(pydoc.f(
            f'If no keywords are specified, the first parameter is regarded as the central value and the second as the standard deviation.'
            f' \033[4mWe recommend that users avoid using protected methods\033[0m.'
            f' Although we do not restrict users from accessing protected methods like \'_set_central()\' and modifying object contents, \033[4mthese methods are not designed for user access\033[0m.'
        ))

        print(f'\n\033[1m\033[4m{"Application:".ljust(25)}\033[0m')
        print(f'\033[1m\u2022\033[0mMathematical Operation\033[0m')
        print(pydoc.f(
            f' {self.__class__.__name__} propagates uncertainty by assuming that each side of the uncertainty follows half of a normal distributions, represented by a single uncertainty value for a side.'
            f' It currently supports uncertainty propagation for addition, subtraction, multiplication, division, and exponentiation.'
            f' Future development will expand support to include more functions and operations.'
            , tab=1))
        print('\n            \u2013 Example 1 of Application : Addition of Symmetric Uncertainty')
        q1, q2 = self.__class__(72 * u.m, 3), self.__class__(800 * u.cm, 400)
        print(f'                $ >>> q1, q2 = {repr(q1)}, {repr(q2)}\n'
              f'                $ >>> print(\'q1 + q2  = \', str(q1 + q2), \' = \', repr(q1 + q2))\n'
              f'                $ q1 + q2  =  {str(q1 + q2)}  =  {repr(q1 + q2)}\n')
        print('\n            \u2013 Example 2 of Application : Addition of Asymmetric Uncertainty')
        q1, q2 = self.__class__(72 * u.m, (-3, +12)), self.__class__(800 * u.cm, (-400, +500))
        print(f'                $ >>> q1, q2 = {repr(q1)}, {repr(q2)}\n'
              f'                $ >>> print(\'q1 + q2  = \', str(q1 + q2), \' = \', repr(q1 + q2))\n'
              f'                $ q1 + q2  =  {str(q1 + q2)}  =  {repr(q1 + q2)}\n')
        print(f'\033[1m\u2022\033[0mUnit Conversion\033[0m')
        print('    ***writing...***')
        print('\n            \u2013 Example 3 of Application : Unit Conversion')
        q1 = self.__class__(274 * u.mm, (-3, +5))
        print(f'                $ >>> q1 = {repr(q1)}\n                $ >>> print(\'q1 in meter  = \', str(q1.to(u.m)))\n                $ q1 in meter  =  {str(q1.to(u.m))}\n')
        print('\n            \u2013 Example 3 of Application : Unit Decomposition')
        import astropy.constants as const
        q3 = self.__class__(4582 * u.km, 10)
        print(f'                $ >>> import astropy.constants as const\n                $ >>> q3 = {repr(q3)}\n                $ >>> print(\'q3 in frequancy      = \', str((const.c / q3).decompose()))\n                $ q3 in frequancy  =  {str((const.c / q3).decompose())}\n')
        print('\033[1m\u2022\033[0mComparison\033[0m')
        print(pydoc.f(
            f' To use comparison operators (<, >, <=, >=) for evaluating for {self.__class__.__name__} objects, you must first establish the comparison criteria by calling the \'{self.compare_by.__name__}()\' method.'
            f' This method accepts four keyword arguments: \'central\', \'conservative\', \'upper\', and \'lower\', which are boolean objects.'
            f' Set the corresponding keyword argument to True to enable a specific comparison criterion.'
            f' Once activated, the selected criterion will govern subsequent comparison operations.'
        , tab=1))
        print('    *\033[1mNote\033[0m: \033[4mThis current approach is under review, and future discussions may lead to major changes in its method.\033[0m')
        print('     Each keyword argument specifies the comparison criteria as follows:\n')
        print(f'        \u2013 \033[1mCentral\033[0m [bool]: Compares the \033[4mcentral\033[0m values of each {self.__class__.__name__} objects. This is often the default behavior')
        print(f'        \u2013 \033[1mConservative\033[0m [bool]: Compares in a \033[4mworst-case\033[0m manner. Returns True only when one value is clearly larger/smal-\n                               ler; otherwise, False. \'{self.__lt__.__name__}()\' being False does not guarantee \'{self.__gt__.__name__}()\' is True.')
        print(f'        \u2013 \033[1mUpper\033[0m [bool]: Compares the \033[4mupper\033[0m bounds of the uncertainty ranges of each {self.__class__.__name__} objects')
        print(f'        \u2013 \033[1mLower\033[0m [bool]: Compares the \033[4mlower\033[0m bounds of the uncertainty ranges of each {self.__class__.__name__} objects')
        print('\n            \u2013 Example 4 of Application : Comparison in Various Approaches')
        q3, q4 = self.__class__(90 * u.cm, 50), self.__class__(100 * u.cm, 10)
        print(
            f'                $ >>> q3, q4 = {repr(q3)}, {repr(q4)}\n'
            f'\n                $ >>> if q3.{q3.compare_by.__name__}(central=True) < q4.{q4.compare_by.__name__}(central=True):  # by central value\n                $ ...     print(\'q3 < q4 by central value\')'
            f'\n                $ ... elif q3.{q3.compare_by.__name__}(central=True) > q4.{q4.compare_by.__name__}(central=True):\n                $ ...     print(\'q3 > q4 by central value\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('q3 < q4 by central value' if q3.compare_by(central=True) < q4.compare_by(central=True) else 'q3 > q4 by central value' if q3.compare_by(central=True) > q4.compare_by(central=True) else 'unable to compare by central value') + '\n')
        print(
            f'                $ >>> if q3.{q3.compare_by.__name__}(conservative=True) < q4.{q4.compare_by.__name__}(conservative=True):  # conservative approach\n                $ ...     print(\'q3 < q4 in conservative approach\')'
            f'\n                $ ... elif q3.{q3.compare_by.__name__}(conservative=True) > q4.{q4.compare_by.__name__}(conservative=True):\n                $ ...     print(\'q3 > q4 in conservative approach\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare in conservative approach\')')
        print('                $ ' + ('q3 < q4 in conservative approach' if q3.compare_by(conservative=True) < q4.compare_by(conservative=True) else 'q3 > q4 in conservative approach' if q3.compare_by(conservative=True) > q4.compare_by(conservative=True) else 'unable to compare in conservative approach') + '\n')
        print(
            f'                $ >>> if q3.{q3.compare_by.__name__}(upper=True) < q4.{q4.compare_by.__name__}(upper=True):  # by upper error\n                $ ...     print(\'q3 < q4 by upper limit\')'
            f'\n                $ ... elif q3.{q3.compare_by.__name__}(upper=True) > q4.{q4.compare_by.__name__}(upper=True):\n                $ ...     print(\'q3 > q4 by upper limit\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('q3 < q4 by upper limit' if q3.compare_by(upper=True) < q4.compare_by(upper=True) else 'q3 > q4 by upper limit' if q3.compare_by(upper=True) > q4.compare_by(upper=True) else 'unable to compare by central value') + '\n')
        print(pydoc.f(
            f' In contrast to the previously described comparison methods, \033[4mthe == operator performs a strict equality check.\033[0m'
            f' It returns True only when both the center and uncertainty values are identical.'
        , tab=1))
        print('')
        print('\033[1m\u2022\033[0mAdditional Functions\033[0m')
        print(pydoc.f(
            f' The \'{self.copy.__name__}()\' method creates a new {self.__class__.__name__} object replicating the original.'
            f' The copied object retains the same central value and uncertainty information as the original.'
            f' This enables you to work with a copy without affecting the original object.'
            , tab=1))
        print(pydoc.f(
            f' The \'{self.errorflip.__name__}()\' method returns a new {self.__class__.__name__} object where the upper and lower limits (or errors) have been swapped.'
            f' This effectively reverses the asymmetry of the uncertainty.'
            f' The central value remains unchanged.'
            f' This can be useful for certain types of analysis or for exploring the effects of error asymmetry.'
            , tab=1))
        print('\n            \u2013 Example 5 of Application : Equal-to Operator')
        q5 = self.__class__(1897 * u.yr, (-1, 10))
        print(f'                $ >>> q5 = {repr(q5)}\n                $ >>> print(repr(q5.{q5.copy.__name__}()), \'==\' if q5.{q5.copy.__name__}() == q5.{q5.errorflip.__name__}() else \'!=\', repr(q5.{q5.errorflip.__name__}()))')
        print(f'                $ {repr(q5.copy())} {"=" if q5.copy() == q5.errorflip() else "!="} {repr(q5.errorflip())}')
        print('')
        print('\033[1m\u2022\033[0mFormatting\033[0m')
        print(pydoc.f(
            f' The \'{self.set_digit.__name__}\' method allows you to customize how the object is displayed.'
            f' A first parameter, \'digit_round\', controls the number of decimal places for rounding (default: 5 digit), and \'digit_stringformat\' sets the total output width (default: 8 spaces).'
            f' For example, \".{self.set_digit.__name__}(digit_round=3, digit_stringformat=10)\" would round to 3 decimal places and use a width of 10 characters.'
        , tab=1))
        print('\n            \u2013 Example 6 of Application : Output Formatting')
        print(f'                $ >>> import numpy as np\n                $ ... import astropy.units as u\n                $ >>> q6 = {self.__class__.__name__}(np.pi * u.hour, (-np.pi * 0.011, np.pi * 0.013))')
        q6 = self.__class__(np.pi * u.hour, (-np.pi * 0.011, np.pi * 0.013))
        print(f'                $ >>> print(\'formatted q6   : \', q6.{self.set_digit.__name__}(7, 13))\n                $ ... print(\'ex-formatted q6: \', q6.{self.set_digit.__name__}(10, 13))\n                $ formatted q6   : {str(q6.set_digit(7, 13))}\n                $ ex-formatted q6: {str(q6.set_digit(10, 13))}')

        print(f'\n\033[1m\033[4m{"Warning:".ljust(25)}\033[0m')
        print(pydoc.f(
            ' This class assumes that all operations involve \033[1mIndependent Variables\033[0m.'
            ' If your data contains correlated variables (i.e., non-zero covariance), the results of this class\'s operations may be unreliable.'
            ' \033[1m\033[4mDo not use this class with correlated value without thoroughly validating the results.\033[0m\n\n'
            ' The operations in this package are designed to propagate errors based on normal distribution theory, treating errors in each variable independently.'
            ' However, due to the complexities of error propagation, some operations may not be mathematically or logically sound.'
            ' We are actively working to identify and address these potential issues through ongoing testing and review.\n\n'
            ' While some NumPy methods, such as \'sum()\', \'diff()\', \'prod()\', and interactions with `numpy.ndarray`, \033[4mappear to function, they have \033[1mnot been fully validated\033[0m.'
            ' \033[1m\033[4mExercise extreme caution\033[0m when using these methods, and do not rely on their output without careful verification.'
            ' Full support for \'numpy.ndarray\' is planned for future development.\n\n'
            ' We are dedicated to improving the accuracy and reliability of this package.'
            ' If you encounter results that differ from other packages, or if you suspect an incorrect or inappropriate operation, please submit a detailed bug report to the primary developer.'
            ' Your feedback is crucial for identifying and resolving any remaining issues.'
            ' We appreciate your collaboration in making this package more robust.'
        ))

        print(f'\n\033[1m\033[4m{"Credit:".ljust(25)}\033[0m')
        print('\033[1m\u2022\033[0mDevelopers\033[0m')
        developers = [f'    {"Main Developer ".ljust(50, "-")}: {self.__developer["name"]} ({self.__developer["contact"]})']
        for collaborator in self.__collaborators:
            if collaborator["contact"] is None:
                developers.append(f'    {"Collaborate Developer ".ljust(50, "-")}: {collaborator["name"]}')
            else:
                developers.append(f'    {"Collaborate Developer ".ljust(50, "-")}: {collaborator["name"]} ({collaborator["contact"]})')
        for contributor in self.__contributors:
            developers.append(f'    {"Contributor ".ljust(50, "-")}: {contributor["name"]} ({contributor["role"]})')
        print('\n'.join(developers) + '\n')
        print('\033[1m\u2022\033[0mHistory\033[0m')
        histories = [
            {'contents': 'First Development of Varu', 'period': '2349'},
            {'contents': 'First Separated Design of ValueU / QuantityU', 'period': '2406'},
            {'contents': 'Test for Operator Magic Method', 'period': '2412'},
            {'contents': 'Code Commenting', 'period': '2412'},
            {'contents': 'Operator Magic Method Restructuring', 'period': '2507'},
            {'contents': 'Minor hotfix (__rtruediv__ error)', 'period': '2509'},
            {'contents': 'Minor hotfix (system path error in help message)', 'period': '2509'},
            {'contents': 'Help Message Implements', 'period': '2509'},
            {'contents': 'Minor hotfix (__array_priority__)', 'period': '2510'},
            {'contents': 'Minor hotfix (absolute/relative selection in __init__)', 'period': '2510'},
            {'contents': 'Minor hotfix (inherit digit parameter)', 'period': '2510'},
            {'contents': 'Major upgrade (engine upgrade from a conceptual to a practical implementation)', 'period': '2535'},
        ]
        for history_part in histories:
            print(f'    {(history_part["contents"] + " ").ljust(50, "-")}: {history_part["period"]}')

        print(f'\n{"#" * pydoc.width}\n{f"Now, you can start {self.__class__.__name__}".rjust(pydoc.width)}')

        return True

    def __str__(self, connection=''):
        notation_central, notations_error = self.value.get_strnotation()

        if notations_error[0][1:] == notations_error[1][1:]:
            if notations_error[0] == 'np.nan' and notations_error[1] == 'np.nan':
                notation_error = f'  {notations_error[-1].ljust(self._digit_stringformat * 2 + 1)}'
            else:
                notation_error = f' ±{notations_error[0][1:].ljust(self._digit_stringformat * 2 + 1)}'
        else:
            notation_error = f' {notations_error[0].ljust(self._digit_stringformat)}, {notations_error[-1].ljust(self._digit_stringformat)}'

        if self.unit is u.dimensionless_unscaled:
            notation_final = (
                f'{notation_central.ljust(self._digit_stringformat)}'
                f' '
                f'({notation_error})'
            )
        else:
            notation_final = (
                f'{notation_central.ljust(self._digit_stringformat)}'
                f' '
                f'({notation_error})'
                f' [{self.unit}]'
            )

        return notation_final

    def __repr__(self):
        notation_central, notations_error = self.value.get_strnotation()

        if notations_error[0][1:] == notations_error[-1][1:]:
            if notations_error[0] == 'np.nan' and notations_error[1] == 'np.nan':
                notation_error = 'np.nan'
            else:
                notation_error = f'{notations_error[0][1:]}'
        else:
            notation_error = f'({notations_error[0]}, {notations_error[-1]})'

        if self.unit is u.dimensionless_unscaled:
            notation_unit = ''
        else:
            notation_unit_elements = []
            for operator, part in zip(('*', '/'), self.unit.to_string().split(' / ')):
                if part[0] == '(' and part[-1] == ')':
                    part = part[1:-1]
                for unitelement in part.split(' '):
                    if unitelement != '1':

                        unitelement_powerbase = unitelement
                        unitelement_powerexponent = '1'

                        indices_notnum = [index for index, char in enumerate(unitelement) if not char.isnumeric()]
                        if unitelement[-1].isnumeric():
                            unitelement_powerbase = unitelement[:indices_notnum[-1] + 1]
                            unitelement_powerexponent = unitelement[indices_notnum[-1] + 1:]

                        if '(' in unitelement and ')' in unitelement:
                            unitelement_powerexponent_expected = unitelement[unitelement.find('(') + 1:unitelement.find(')')]
                            splitedcomp = unitelement_powerexponent_expected.split('/')
                            if len(splitedcomp) == 2 and splitedcomp[0].isnumeric() and splitedcomp[1].isnumeric():
                                unitelement_powerbase = unitelement[:unitelement.find('(')]
                                unitelement_powerexponent = f'({unitelement_powerexponent_expected})'

                        if unitelement_powerexponent == '1':
                            notation_unit_elements.append(f' {operator} u.{unitelement_powerbase}')
                        else:
                            notation_unit_elements.append(f' {operator} u.{unitelement_powerbase} ** {unitelement_powerexponent}')

            notation_unit = ''.join(notation_unit_elements)

        notation_final = (
            f'{self.__class__.__name__}({notation_central}{notation_unit},'
            f' '
            f'{notation_error})')

        return notation_final



if __name__ == '__main__':
    QuantityU().help()
