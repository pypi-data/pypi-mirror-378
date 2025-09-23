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
from numba.np.ufunc.workqueue import synchronize

from .temptoolclass_version import HeadVer
from .temptoolclass_pydocument import PyDocument

class ValueU:
    __fullname = 'Value tagged with Uncertainty'
    __firstwritten = dt.datetime.strptime('2023-09-06', '%Y-%m-%d')
    __lastupdate = dt.datetime.strptime('2025-08-26', '%Y-%m-%d')
    __version = HeadVer(0, __lastupdate, 0)
    __developer = {'name': 'DH.Koh', 'contact': 'donghyeok.koh.code@gmail.com'}
    __collaborators = [{'name': 'JH.Kim', 'contact': None}, {'name': 'KM.Heo', 'contact': None}]
    __contributors = [{'name': None, 'role': None}]
    __callsign = 'Value(+/-)'

    __versiondependency = {}

    __array_priority__ = 11000
    _n_samples = None  # Number of samples for uncertainty distribution
    _n_samples_defaultvalue = 10000  # Default value of __n_samples

    def __init__(self, center=None, std=None, n_samples=None):
        # self.__id = uuid.uuid4()  # time.perf_counter_ns()

        if std is None:
            std = np.nan
        if center is None:
            center = np.nan
        if n_samples is None:
            if ValueU._n_samples is None:
                ValueU._n_samples = ValueU._n_samples_defaultvalue  # Default number of samples for uncertainty distribution
        else:
            if ValueU._n_samples is None:
                ValueU._n_samples = n_samples
            elif ValueU._n_samples == n_samples:
                pass
            else:
                raise ValueError(f'number of sample \"n_samples\" already set to {ValueU._n_samples}, cannot be changed to {n_samples}.')
        self._comparison_criterion_by_center = True
        self._comparison_criterion_threshold = None
        self.enforced_positive = None
        self.enforced_negative = None

        ### initialize
        self.distribution = unc.Distribution([np.nan])

        ### recognize value
        produced_distribution = self._produce_distribution(center=center, std=std)

        self._digit_round = 5
        self._digit_stringformat = 8

        return None

    def _sync_info(self):
        self._n_samples = self.distribution.distribution.shape[-1]
        # assert self._n_samples == self.distribution.distribution.shape[-1], 'The shape of the distribution does not match the static number of samples.'

        """
        [***ToDo**_] (25-08-14) - 값의 분포를 음수 또는 양수로 강제하는 클래스 변수 구현 필요, None으로 임시조치
        """
        self.enforced_positive = None
        self.enforced_negative = None

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

        self.center = center
        self.distribution = distribution

        dummyvalue_synchronized = self._sync_info()

        return self

    def __produce_distribution_symmetric(self, center, std):
        """
        Private Method
        Produce a symmetric distribution object 'self.distribution' from the input regulated information.
        usage :
        $ >>> self.__produce_distribution_symmetric(center=10, std=1)
        """
        self.center = center

        distribution_produced = unc.normal(center=self.center, std=std, n_samples=self._n_samples)

        self.distribution = distribution_produced

    def __produce_distribution_asymmetric(self, center, stds: np.ndarray):
        """
        Private Method
        Produce an asymmetric distribution object 'self.distribution' from the input regulated information.
        usage :
        $ >>> self.__produce_distribution_asymmetric(center=10, std=np.array([1, 2]))
        """
        self.center = center

        distribution_produced_primary = unc.normal(center=0, std=stds[1], n_samples=self._n_samples)
        distribution_produced_secondary = unc.Distribution(
            np.where(
                distribution_produced_primary.distribution < 0,
                distribution_produced_primary.distribution * np.abs(stds[0] / stds[1]),
                distribution_produced_primary.distribution
            )
        )
        distribution_produced = (self.center + distribution_produced_secondary)

        self.distribution = distribution_produced

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
                self.__produce_distribution_asymmetric(center=center, stds=std)
            elif std.shape == (1,):
                ### Case (a-2) std= array([number])
                self.__produce_distribution_symmetric(center=center, std=std[0])
            elif np.prod(std.shape) / np.prod(center.shape) == 2.:
                ### Case (a-3) std= [[-number1, +number2, ...], [+number1, +number2, ...]]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not std.shape == ((2,) + np.array(center).shape):
                    raise ValueError(f'Input argument \"stddev\" shape not matched with two times repeated shape of the center value')
                self.__produce_distribution_asymmetric(center=center, stds=np.array([std[0], std[1]]))
            elif np.prod(std.shape) / np.prod(center.shape) == 1.:
                ### Case (a-4) std= [-number1, +number2, ...]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not std.shape == np.array(center).shape:
                    raise ValueError(f'Input argument \"stddev\" shape not matched with the center value')
                self.__produce_distribution_symmetric(center=center, std=std)
            else:
                raise ValueError(f'Input argument \"std\" wrong - should be a number pair (ndarray) or the same structure as the center value')
        elif isinstance(std, list) or isinstance(std, tuple):
            if len(std) == 2:
                ### Case (b-1) std= [-number, +number]
                self.__produce_distribution_asymmetric(center=center, stds=np.array(std))
            elif len(std) == 1:
                ### Case (b-2) std= [number]
                self.__produce_distribution_symmetric(center=center, std=std[0])
            elif np.prod(np.array(std).shape) / np.prod(np.array(center).shape) == 2.:
                ### Case (b-3) std= [[-number1, +number2, ...], [+number1, +number2, ...]]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not np.array(std).shape == ((2,) + np.array(center).shape):
                    raise ValueError(f'Input argument \"stddev\" shape not matched with two times repeated shape of the center value')
                self.__produce_distribution_asymmetric(center=center, stds=np.array([np.array(std)[0], np.array(std)[1]]))
            elif np.prod(np.array(std).shape) / np.prod(np.array(center).shape) == 1.:
                ### Case (b-4) std= [-number1, +number2, ...]
                """[Describe] - self.center가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
                if not np.array(std).shape == np.array(center).shape:
                    raise ValueError(f'Input argument \"stddev\" shape not matched with the center value')
                self.__produce_distribution_symmetric(center=center, std=std)
            else:
                raise ValueError(f'Input argument \"std\" wrong - should be a number pair (list) or the same structure as the center value')
        elif isinstance(std, int) or isinstance(std, float):
            ### Case (c) std= number
            self.__produce_distribution_symmetric(center=center, std=std)
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


    def __add__(self, other):  ## from self + other
        """
        [Describe] - 가산연산에서 other가 QuantityU의 인스턴스라면 other.__radd__를 호출하여 처리하고,
        이때 other가 Quantity의 인스턴스인 경우에는 other.unit이 astropy.units.dimensionless_unscaled이지 않으면 연산 불가능하다.
        이러한 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.

        [__*ToDo___] (24-_-_) - QuantityU와 ValueU간의 상호작용이 있고, QuantityU에서도 ValueU 클래스를 사용하고 있다.
        따라서 순환참조가 되지 않도록 하려면 QuantityU를 이렇게 메소드 내에서 호출하여 사용하는 것이 맞는지 확인 필요.
        """
        from .quantityu import QuantityU
        if isinstance(other, QuantityU):  ### Case for ValueU + QuantityU
            result = other.__radd__(self)
        else:
            if isinstance(other, self.__class__):
                result = self.__class__().set_manual(
                    center=self.center + other.center,
                    distribution=self.distribution + other.distribution,
                ).set_digit(
                    digit_round=max(self._digit_round, other._digit_round),
                    digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
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
    # def __sub__(self, other):
    #     """
    #     [___ToDo*__] (25-02-03) - 어차피 부호만 다르고 계산 접근방식이 같다면 별개 내용을 구현하기보단 __neg__와 __add__를 이용하도록 구현하는게 나을까?
    #     만약 그렇게 하기로 결정한다면, __add__에서 인수를 반드시 매번 독립변수로 취급되도록 설계되어야만 한다.
    #     어쨋든 현재 설계로는 __neg__와 __add__를 이용해 가감연산을 전적으로 __add__에 의지하는 것이 가능할 것으로 보이지만,
    #     이 제안이 좋은 구현인지, 논리적으로 정확한 구현인지 아닌지는 더 고민해봐야 하는 문제임.
    #     이러한 문제는 QuantityU.__sub__ 에서도 동일함
    #
    #     [Describe] - 가감연산에서 other가 QuantityU의 인스턴스라면 other.__radd__를 호출하여 처리하고,
    #     만약 other가 Quantity의 인스턴스일때는 other.unit이 astropy.units.dimensionless_unscaled이지 않으면 연산 불가능하다.
    #     이러한 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.
    #     """
    #     from .quantityu import QuantityU
    #     if isinstance(other, QuantityU):  ### Case for ValueU + QuantityU
    #         result = other.__radd__(self)
    #     else:
    #         if isinstance(other, self.__class__):
    #             result = self.__class__().set_manual(
    #                 center=self.center - other.center,
    #                 distribution=self.distribution - other.distribution,
    #             ).set_digit(
    #                 digit_round=max(self._digit_round, other._digit_round),
    #                 digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
    #             )
    #         else:
    #             result = self.__class__().set_manual(
    #                 center=self.center - other,
    #                 distribution=self.distribution - other),
    #             ).set_digit(
    #                 digit_round=self._digit_round,
    #                 digit_stringformat=self._digit_stringformat,
    #             )
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
        """
        [Describe] - 승법연산에서 other가 QuantityU의 인스턴스라면 other.__rmul__를 호출하여 처리하고,
        이때 other가 Quantity의 인스턴스인 경우에는 other.unit이 astropy.units.dimensionless_unscaled이지 않으면 연산 불가능하다.
        이러한 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.

        [__*ToDo___] (24--) - QuantityU와 ValueU간의 상호작용이 있고, QuantityU에서도 ValueU 클래스를 사용하고 있다.
        따라서 순환참조가 되지 않도록 하려면 QuantityU를 이렇게 메소드 내에서 호출하여 사용하는 것이 맞는지 확인 필요.
        """
        from .quantityu import QuantityU
        if isinstance(other, QuantityU):  ### Case(c) ValueU * QuantityU
            result = other.__rmul__(self)
        else:
            if isinstance(other, u.UnitBase):  ### Case(d) ValueU * Units
                ## [Describe] - 승법연산에서 other가 astropy.units에서 제공하는 인스턴스라면, QuantityU 객체로 반환한다.
                result = QuantityU(n_samples=self._n_samples).set_manual(
                    center=self.center * other,
                    distribution=self.distribution * other,
                ).set_digit(
                    digit_round=self._digit_round,
                    digit_stringformat=self._digit_stringformat,
                )
            else:
                if isinstance(other, self.__class__):
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

    def __rmul__(self, other):  ## from other * self
        return self.__mul__(other)

    """
    [Describe] - 비슷한 작동을 하는 __mull__를 지수만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __truediv__(self, other):
    #     from .quantityu import QuantityU
    #     if isinstance(other, QuantityU):  ### Case(a) ValueU / QuantityU
    #         result = other * (self ** (-1))
    #     else:
    #         if isinstance(other, u.UnitBase):  ### Case(d) ValueU / Units
    #             ## [Describe] - 승법연산에서 other가 astropy.units에서 제공하는 인스턴스라면, QuantityU 객체로 반환한다.
    #             result = QuantityU().set_manual(
    #                 center=self.center / other,
    #                 distribution=self.distribution / other,
    #             ).set_digit(
    #                 digit_round=self._digit_round,
    #                 digit_stringformat=self._digit_stringformat,
    #             )
    #         else:
    #             if isinstance(other, self.__class__):
    #                 result = self.__class__().set_manual(
    #                     center=self.center / other.center,
    #                     distribution=self.distribution / other.distribution,
    #                 ).set_digit(
    #                     digit_round=max(self._digit_round, other._digit_round),
    #                     digit_stringformat=max(self._digit_stringformat, other._digit_stringformat),
    #                 )
    #             else:
    #                 result = self.__class__().set_manual(
    #                     center=self.center / other,
    #                     distribution=self.distribution / other),
    #                 ).set_digit(
    #                     digit_round=self._digit_round,
    #                     digit_stringformat=self._digit_stringformat,
    #                 )
    #
    #     return result

    def __truediv__(self, other):
        return self.__mul__(other.__pow__(-1))

    def __rtruediv__(self, other):
        return self.__pow__(-1).__mul__(other)

    def __pow__(self, other):  ## from self ** other
        """
        [Describe] - 지수연산에서 other는 단위가 없거나 단위가 dimensionless_unscaled 이어야 한다.
        other가 '지수연산이 불가능한 단위를 가진 객체'인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 에러가 발생하도록 의도함.
        띠리서 other은 반드시 numeric하거나, 단위가 dimensionless_unscaled 이어야 한다.
        """
        from .quantityu import QuantityU
        if isinstance(other, QuantityU):  ### Case(c) ValueU ** QuantityU
            result = other.__rpow__(self)
        else:
            if isinstance(other, self.__class__):
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
        from .quantityu import QuantityU
        """
        [Describe] - other가 QuantityU의 인스턴스일 경우, QuantityU ** ValueU 연산은 QuantityU.__pow__()에서 처리할 것이다.
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
        $ >>> v = ValueU(3.141592653589793, 0.5)
        $ ... print(repr(round(v, 3)))
        $ ValueU(3.142, (-0.5, +0.5))
        """
        result_rounded = self.copy().set_manual(
            center=np.round(self.center, rounddigit),
            distribution=self.distribution
        ).set_digit(
            digit_round=rounddigit,
            digit_stringformat=self._digit_stringformat
        )

        return result_rounded



    def set_digit(self, digit_round=5, digit_stringformat=10):
        if isinstance(digit_round, int):
            self._digit_round = digit_round
        else:
            raise TypeError(f'Input argument \'digit_round\' for \"{__name__}\" type wrong - must be instance of {int}')

        if isinstance(digit_stringformat, int):
            self._digit_stringformat = digit_stringformat
        else:
            raise TypeError(f'Input argument \'digit_stringformat\' for \"{__name__}\" type wrong - must be instance of {int}')

        return self

    def get_numnotation(self, digit_round=None):
        if digit_round == None:
            digit_round = self._digit_round

        rounded_central = np.round(self.center, digit_round)

        if np.isnan(rounded_central):
            notation_central = np.nan
        elif int(rounded_central) == float(rounded_central):
            notation_central = rounded_central.astype("int")
        else:
            notation_central = rounded_central

        # if np.sum(~np.isnan(self.distribution.distribution)) > 0:
        deviation = (self.distribution.distribution - rounded_central)
        deviation_positive = deviation[np.where(deviation > 0)[0]]
        deviation_negative = deviation[np.where(deviation < 0)[0]]

        uncertainty_upper = np.sqrt(np.nanmean(deviation_positive ** 2)) if np.sum(~np.isnan(deviation_positive)) > 0 else 0 if deviation_positive.shape[0] == 0 else np.nan
        uncertainty_lower = np.sqrt(np.nanmean(deviation_negative ** 2)) if np.sum(~np.isnan(deviation_negative)) > 0 else 0 if deviation_negative.shape[0] == 0 else np.nan

        notations_error = [uncertainty_lower, uncertainty_upper]

        return notation_central, notations_error

    def get_strnotation(self, digit_round=None):
        if digit_round == None:
            digit_round = self._digit_round

        rounded_central = np.round(self.center, digit_round)

        if np.isnan(rounded_central):
            notation_central = 'np.nan'
        elif int(rounded_central) == float(rounded_central):
            notation_central = f'{rounded_central.astype("int")}'
        else:
            notation_central = f'{rounded_central}'

        # if np.sum(~np.isnan(self.distribution.distribution)) > 0:
        deviation = (self.distribution.distribution - rounded_central)
        deviation_positive = deviation[np.where(deviation > 0)[0]]
        deviation_negative = deviation[np.where(deviation < 0)[0]]

        uncertainty_upper = np.sqrt(np.nanmean(deviation_positive ** 2)) if np.sum(~np.isnan(deviation_positive)) > 0 else 0 if deviation_positive.shape[0] == 0 else np.nan
        uncertainty_lower = np.sqrt(np.nanmean(deviation_negative ** 2)) if np.sum(~np.isnan(deviation_negative)) > 0 else 0 if deviation_negative.shape[0] == 0 else np.nan

        notations_error = []
        for error_sign, error_relative in zip([-1, 1], [uncertainty_lower, uncertainty_upper]):
            if not np.isnan(error_relative):
                rounded_error_relative = np.round(error_relative, digit_round)
                if int(rounded_error_relative) == float(rounded_error_relative):
                    notation_value = rounded_error_relative.astype("int")
                else:
                    notation_value = rounded_error_relative
                if error_sign == -1:
                    sign = '-'
                else:
                    sign = '+'
                notations_error.append(f'{sign}{np.abs(notation_value)}')
            else:
                notations_error.append('np.nan')  # to-do : how to show in the error is nan
        # else:
        #     notations_error = ['nan', 'nan']

        return notation_central, notations_error

    def help(self):
        pydoc = PyDocument(120)
        print(f'\n{"#" * pydoc.width}\n')

        print(
            f'\033[1m\033[3m\033[4m\033[7m{self.__class__.__name__}\033[0m\033[4m: \033[1m{self.__fullname} (Class) '
            f''.ljust(pydoc.width + 4 * 7 - len(str(self.__class__.__version))) + str(self.__class__.__version) + '\033[0m')
        print(f'last updated at {self.__lastupdate.strftime("%Y-%m-%d")}'.rjust(pydoc.width))

        print(f'\n\033[1m\033[4m{"Introduction:".ljust(25)}\033[0m')
        print(pydoc.f(
            f' {self.__class__.__name__} is a Python class for managing values and their associated uncertainties.'
            f' It stores, computes with, and represents these values not through traditional error propagation, but by modeling uncertainty as a distribution of sample values.)'
            f' This implementation assumes an initial normal distribution based on the provided standard deviations.'
        ))
        print(pydoc.f(
            f' Fundamentally based on the {unc.__name__} package, {self.__class__.__name__} extends it with several key convenience features.'
            f' These enhancements, updated in August 2025, include \033[1mpickling\033[0m, robust preservation of the central value through operations, and more intuitive string representations.'
        ))
        print(pydoc.f(
            f' When using this class, it\'s important to be aware of a few key points.'
            f' The underlying samples of a {self.__class__.__name__} instance are treated as dependent when used in multiple operations, which differs from the independent variable assumption in analytical error propagation.'
            f' Additionally, the sampling method can lead to significant memory consumption, especially with a high number of samples, so careful management of memory and sample size is recommended for extensive use.'
            f' The package requires `NumPy` and `Astropy` and was developed and tested on macOS Ventura; performance may vary on other systems pending further testing.'
        ))
        print('\n        \u2013 How to declare/generate an instance:')
        print(
            f'            $ >>> from {os.path.basename(os.path.dirname(__file__))} import {self.__class__.__name__}\n'
            f'            $ >>> my_first_uncertain_value = {self.__class__.__name__}(center=15, strd=3)\n'
        )
        print(pydoc.f(
            f' A new {self.__class__.__name__} instance is created by providing parameters such as `center`, `std`, and `n_samples`.'
            f' The `center` parameter takes a numeric value (int, float) as the central value of the distribution.'
            f' If omitted, it defaults to \033[1mnp.nan\033[0m.'
            f' The `std` parameter defines the standard deviation of the uncertainty.'
            f' You can provide a single number for a \033[1msymmetric\033[0m uncertainty (e.g., `std=0.1` implies ±0.1), or a two-element array-like object (e.g., `[-0.2, 0.3]`) for an \033[1masymmetric\033[0m uncertainty.'
            f' An asymmetric uncertainty is modeled by combining the left half of one normal distribution and the right half of another, each defined with a different standard deviation.'
            f' If this parameter is omitted, it defaults to \033[1m0\033[0m.'
            f' The `n_samples` parameter specifies the number of random samples used to represent the uncertainty distribution.'
            f' \033[1mImportant\033[0m: `n_samples` is a class-level setting.'
            f' All instances of {self.__class__.__name__} must share the same number of samples to ensure that Numpy calculations between them are mathematically valid.'
            f' Attempting to create a new instance with a different `n_samples` value than existing instances will raise an error.'
        ))
        print(' The full set of parameters is:\n')
        print(f'    \u2013 \033[1mcenter\033[0m [float]: \033[4mMean\033[0m value (or representative/\033[4mcentral\033[0m value) the representing probabilistic center')
        print(f'    \u2013 \033[1mstd\033[0m [float/float-arr]: \033[4mStandard deviation\033[0m(s) representing relative uncertainty(ies) from the central value')
        print(f'    \u2013 \033[1mn_samples\033[0m [unsigned int]: \033[4mNumber of samples\033[0m of uncertain distribution (by default, {self.__n_samples_defaultvalue})')
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
        v1, v2 = self.__class__(72, 3), self.__class__(83, 4)
        print(f'                $ >>> v1, v2 = {repr(v1)}, {repr(v2)}\n                $ >>> print(\'v1 + v2  = \', str(v1 + v2), \' = \', repr(v1 + v2))\n                $ v1 + v2  =  {str(v1 + v2)}  =  {repr(v1 + v2)}')
        print('\n            \u2013 Example 2 of Application : Addition of Asymmetric Uncertainty')
        v1, v2 = self.__class__(72, (-3, +5)), self.__class__(83, (-4, +12))
        print(f'                $ >>> v1, v2 = {repr(v1)}, {repr(v2)}\n                $ >>> print(\'v1 + v2  = \', str(v1 + v2), \' = \', repr(v1 + v2))\n                $ v1 + v2  =  {str(v1 + v2)}  =  {repr(v1 + v2)}\n')
        print('\033[1m\u2022\033[0mPromotion\033[0m')
        from .quantityu import QuantityU
        print(pydoc.f(
            f' {self.__class__.__name__} objects are designed to be compatible with {" ".join([word[0].upper() + word[1:] for word in str(u.__name__).split(".")])}.'
            f' Multiplying a {self.__class__.__name__} object by an \'{u.__name__}\' object will promote it to a {QuantityU.__name__} object, which provides additional features for working with units.'
            f' See the {QuantityU.__name__} documentation for a complete description of its capabilities.'
        , tab=1))
        print('\n            \u2013 Example 3 of Application : Multiply with Unit Object')
        q = v1 * u.m  # It is now promoted as QuantityU, not ValueU anymore.
        print(
            f'                $ >>> q = v1 * u.m  # It is now promoted as QuantityU, not {self.__class__.__name__} anymore.\n                $ >>> print(\'q  = \', str(q), \' = \', repr(q))\n                $ q  =  {str(q)}  =  {repr(q)}\n'
            f'                $ >>> print(type(q))\n                $ {QuantityU}\n')
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
        v3, v4 = self.__class__(90, 50), self.__class__(100, 10)
        print(
            f'                $ >>> v3, v4 = {repr(v3)}, {repr(v4)}\n'
            f'\n                $ >>> if v3.{v3.compare_by.__name__}(central=True) < v4.{v4.compare_by.__name__}(central=True):  # by central value\n                $ ...     print(\'v3 < v4 by central value\')'
            f'\n                $ ... elif v3.{v3.compare_by.__name__}(central=True) > v4.{v4.compare_by.__name__}(central=True):\n                $ ...     print(\'v3 > v4 by central value\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('v3 < v4 by central value' if v3.compare_by(central=True) < v4.compare_by(central=True) else 'v3 > v4 by central value' if v3.compare_by(central=True) > v4.compare_by(central=True) else 'unable to compare by central value') + '\n')
        print(
            f'                $ >>> if v3.{v3.compare_by.__name__}(conservative=True) < v4.{v4.compare_by.__name__}(conservative=True):  # conservative approach\n                $ ...     print(\'v3 < v4 in conservative approach\')'
            f'\n                $ ... elif v3.{v3.compare_by.__name__}(conservative=True) > v4.{v4.compare_by.__name__}(conservative=True):\n                $ ...     print(\'v3 > v4 in conservative approach\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare in conservative approach\')')
        print('                $ ' + ('v3 < v4 in conservative approach' if v3.compare_by(conservative=True) < v4.compare_by(conservative=True) else 'v3 > v4 in conservative approach' if v3.compare_by(conservative=True) > v4.compare_by(conservative=True) else 'unable to compare in conservative approach') + '\n')
        print(
            f'                $ >>> if v3.{v3.compare_by.__name__}(upper=True) < v4.{v4.compare_by.__name__}(upper=True):  # by upper error\n                $ ...     print(\'v3 < v4 by upper limit\')'
            f'\n                $ ... elif v3.{v3.compare_by.__name__}(upper=True) > v4.{v4.compare_by.__name__}(upper=True):\n                $ ...     print(\'v3 > v4 by upper limit\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('v3 < v4 by upper limit' if v3.compare_by(upper=True) < v4.compare_by(upper=True) else 'v3 > v4 by upper limit' if v3.compare_by(upper=True) > v4.compare_by(upper=True) else 'unable to compare by central value') + '\n')
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
        v5 = self.__class__(1897, (-1, 10))
        print(f'                $ >>> v5 = {repr(v5)}\n                $ >>> print(repr(v5.{v5.copy.__name__}()), \'==\' if v5.{v5.copy.__name__}() == v5.{v5.errorflip.__name__}() else \'!=\', repr(v5.{v5.errorflip.__name__}()))')
        print(f'                $ {repr(v5.copy())} {"=" if v5.copy() == v5.errorflip() else "!="} {repr(v5.errorflip())}\n')
        print('\033[1m\u2022\033[0mFormatting\033[0m')
        print(pydoc.f(
            f' The \'{self.set_digit.__name__}\' method allows you to customize how the object is displayed.'
            f' A first parameter, \'digit_round\', controls the number of decimal places for rounding (default: 5 digit), and \'digit_stringformat\' sets the total output width (default: 8 spaces).'
            f' For example, \".{self.set_digit.__name__}(digit_round=3, digit_stringformat=10)\" would round to 3 decimal places and use a width of 10 characters.'
            f' Users can access the formatted representation via \'{self.get_strnotation.__name__}\'.'
            f' However, the \'{self.__str__.__name__}()\' and \'{self.__repr__.__name__}()\' functions already use these settings.'
            f' Therefore, users rarely need to call \'get_notation()\' directly.'
        , tab=1))
        print('\n            \u2013 Example 6 of Application : Output Formatting')
        print(f'                $ >>> import numpy as np\n                $ >>> v6 = {self.__class__.__name__}(np.pi, (-np.pi * 0.011, np.pi * 0.013))')
        v6 = self.__class__(np.pi, (-np.pi * 0.011, np.pi * 0.013))
        print(f'                $ >>> print(\'formatted v6   : \', v6.{self.set_digit.__name__}(7, 13))\n                $ ... print(\'ex-formatted v6: \', v6.{self.set_digit.__name__}(10, 13))\n                $ formatted v6   : {str(v6.set_digit(7, 13))}\n                $ ex-formatted v6: {str(v6.set_digit(10, 13))}')

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
            {'contents': 'Help Message Implements', 'period': '2508'},
            {'contents': 'Minor hotfix (__rtruediv__ error)', 'period': '2509'},
            {'contents': 'Minor hotfix (__rper__ error)', 'period': '2509'},
            {'contents': 'Minor hotfix (system path error in help message)', 'period': '2509'},
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
        notation_central, notations_error = self.get_strnotation()

        if notations_error[0][1:] == notations_error[-1][1:]:
            if notations_error[0] == 'np.nan' and notations_error[1] == 'np.nan':
                notation_error = f'  {notations_error[-1].ljust(self._digit_stringformat * 2 + 1)}'
            else:
                notation_error = f' ±{notations_error[0][1:].ljust(self._digit_stringformat * 2 + 1)}'
        else:
            notation_error = f' {notations_error[0].ljust(self._digit_stringformat)}, {notations_error[-1].ljust(self._digit_stringformat)}'

        notation_final = (
            f'{notation_central.ljust(self._digit_stringformat)}'
            f' '
            f'({notation_error})'
        )

        return notation_final

    def __repr__(self):
        notation_central, notations_error = self.get_strnotation()

        if notations_error[0][1:] == notations_error[-1][1:]:
            if notations_error[0] == 'np.nan' and notations_error[1] == 'np.nan':
                notation_error = 'np.nan'
            else:
                notation_error = f'{notations_error[0][1:]}'
        else:
            notation_error = f'({notations_error[0]}, {notations_error[-1]})'

        notation_final = (
            f'{self.__class__.__name__}({notation_central},'
            f' '
            f'{notation_error})')

        return notation_final



if __name__ == '__main__':
    ValueU().help()
