import pytest
import numpy as np
import pandas as pd

from anomalydetection.custom_exceptions import NoRangeDefinedError, WrongInputDataType
from anomalydetection.detectors import RangeDetector, DiffRangeDetector, AnomalyDetectionPipeline, PeakDetector, \
    HampelDetector
from tests.data_generation import create_random_walk_with_outliers


@pytest.fixture
def data_series():
    n_steps = 100
    time_series_with_outliers, outlier_indices, random_walk = create_random_walk_with_outliers(n_steps)
    time = pd.date_range(start='2020', periods=n_steps, freq='1H')
    return pd.Series(time_series_with_outliers, index=time), outlier_indices, pd.Series(random_walk, index=time)


@pytest.fixture
def range_data():
    normal_data = np.array([0, np.nan, 1, 0, 2, np.nan, 3.14, 4])
    abnormal_data = np.array([-1, np.nan, 2, np.nan, 1, 0, 4, 10])
    expected_anomalies = np.array([True, False, False, False, False, False, True, True])
    assert len(expected_anomalies) == len(abnormal_data)
    return normal_data, abnormal_data, expected_anomalies


@pytest.fixture
def range_data_series(range_data):
    normal_data, abnormal_data, expected_anomalies = range_data
    time = pd.date_range(start='2020', periods=len(normal_data), freq='1H')
    return pd.Series(normal_data, index=time), pd.Series(abnormal_data, index=time), expected_anomalies


def test_base_detector_exceptions(range_data, range_data_series):
    data, _, _ = range_data
    data_series, _, _ = range_data_series

    detector = RangeDetector()
    pytest.raises(NoRangeDefinedError, detector.detect, data_series)
    pytest.raises(WrongInputDataType, detector.fit, data)


def test_range_detector(range_data_series):
    data, _, _ = range_data_series

    detector = RangeDetector(0, 2)
    anomalies = detector.detect(data)
    expected_anomalies = [False, False, False, False, False, False, True, True]
    assert len(anomalies) == len(data)
    assert sum(anomalies) == 2
    assert all(expected_anomalies == anomalies)


def test_range_detector_autoset(range_data_series):
    data, _, _ = range_data_series

    anomalies = RangeDetector(min_value=3).detect(data)
    assert sum(anomalies) == 4

    anomalies = RangeDetector(max_value=3).detect(data)
    assert sum(anomalies) == 2


def test_range_detector_pipeline(range_data_series):
    normal_data, abnormal_data, expected_anomalies = range_data_series
    anomaly_detector = AnomalyDetectionPipeline([RangeDetector(), DiffRangeDetector()])

    anomaly_detector.fit(normal_data)
    detected_anomalies = anomaly_detector.detect(abnormal_data)
    assert all(detected_anomalies == expected_anomalies)

    detected_anomalies = anomaly_detector.detect_detailed(abnormal_data)
    assert all(detected_anomalies.is_anomaly == expected_anomalies)


def test_peak_detector(range_data_series):
    data, _, _ = range_data_series

    detector = PeakDetector(3, 0.1)
    anomalies = detector.detect(data)

    assert len(anomalies) == len(data)
    assert sum(anomalies) == 1


def test_hampel_detector(data_series):
    data_with_anomalies, expected_anomalies_indices, _ = data_series
    detector = HampelDetector()
    anomalies = detector.detect(data_with_anomalies)
    anomalies_indices = np.array(np.where(anomalies)).flatten()
    # Validate if the found anomalies are also in the expected anomaly set
    # NB Not necessarily all of them
    assert all(i in expected_anomalies_indices for i in anomalies_indices)


def test_hampel_numba_detector(data_series):
    data_with_anomalies, expected_anomalies_indices, _ = data_series
    detector = HampelDetector(use_numba=True)
    anomalies = detector.detect(data_with_anomalies)
    anomalies_indices = np.array(np.where(anomalies)).flatten()
    # Validate if the found anomalies are also in the expected anomaly set
    # NB Not necessarily all of them
    assert all(i in expected_anomalies_indices for i in anomalies_indices)
