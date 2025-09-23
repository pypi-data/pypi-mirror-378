import glob
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Callable

import scipy.io as sio
import numpy as np
from pandas import date_range, Series

TEST_DATA_TOP_FOLDER = Path('test_data')
PRODUCTION_DATA_TOP_FOLDER = Path('production_data')
FAST_DELIVERY_FOLDER = Path('fast_delivery')
HIGH_FREQUENCY_FOLDER = Path('high_frequency')

ALL_MONTHS_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def create_directory_if_not_exists(path):
    """
    Create a directory if it does not already exist.

    Args:
        path: Path to the directory.
    """

    if not os.path.exists(path):
        os.makedirs(path)


def get_top_level_directory(parent_dir, is_test_mode=False):
    """
    Return top-level data directory, creating if missing.

    Args:
        parent_dir: Base directory.
        is_test_mode: If True, return test-data folder; otherwise production.

    Returns:
        Path object for the resolved directory.
    """

    # Subdirectory of parent_dir where production data is saved.
    if not is_test_mode:
        directory = Path(parent_dir / PRODUCTION_DATA_TOP_FOLDER)
        if directory.is_dir():
            return directory
        else:
            create_directory_if_not_exists(directory)
            return directory

    # Subdirectory of parent_dir where test data is saved.
    else:
        test_directory = Path(parent_dir / TEST_DATA_TOP_FOLDER)
        if test_directory.is_dir():
            return test_directory
        else:
            create_directory_if_not_exists(test_directory)
            return test_directory


def remove_9s(data):
    """
    Replace sentinel 9999 values with NaN.

    Args:
        data: NumPy array of values.

    Returns:
        Array with 9999 replaced by NaN.
    """

    nines_ind = np.where(data == 9999)
    data[nines_ind] = float('nan')

    return data


def get_missing_months(month_list):
    """
    Return list of months missing from a given set.

    Args:
        month_list: List of month integers.

    Returns:
        Sorted list of missing months; empty if none missing.
    """

    missing_months = []
    if ALL_MONTHS_NUMBERS == month_list:
        return missing_months

    missing_months = list(set(ALL_MONTHS_NUMBERS) - set(month_list))
    missing_months.sort()

    return missing_months


def get_hf_mat_files(path: Path, full_name=False):
    """
    Return mapping of sensors to months or filenames for HF .mat files.

    Args:
        path: Directory containing .mat files.
        full_name: If True, return full filenames; otherwise month codes.

    Returns:
        Dict mapping sensor_id -> list of months or filenames.
        {"<sensor_id>": ["01', '02', ...], ...} or {"<sensor_id>": ["<file_name_01>", "<file_name_02>", ...], ...}
    """

    all_mat_files = sorted(glob.glob(str(path) + '/*.mat'))
    sensor_months = {}  # sensors and a list of months they appear in

    for file_name_list in all_mat_files:
        # Assuming that each sensor name is ALWAYS 3 letters long (not sure if a safe assumption).
        sensor_name = file_name_list.split('.mat')[0][-3:]
        if full_name:
            value = file_name_list
        else:
            value = file_name_list.split('.mat')[0][-5:-3]
        # sensors_set.add(sensor_name)
        if sensor_name not in sensor_months:
            sensor_months[sensor_name] = [value]
        else:
            sensor_months[sensor_name].append(value)

    return sensor_months


def datenum2(date):
    """
    Convert numpy datetime64 array to MATLAB-style datenums.

    Args:
        date: Iterable of numpy.datetime64 values.

    Returns:
        List of floats in MATLAB datenum format.
    """

    obj = []
    for d in date:
        obj.append(366 + d.astype(datetime).toordinal() + (
                d.astype(datetime) - datetime.fromordinal(d.astype(datetime).toordinal())).total_seconds() / (
                           24 * 60 * 60))

    return obj


def datenum(d):
    """
    Convert Python datetime to MATLAB-style datenum float.

    Args:
        d: datetime instance.

    Returns:
        Float days since year 0 with fractional days.
    """

    return 366 + d.toordinal() + (d - datetime.fromordinal(d.toordinal())).total_seconds() / (24 * 60 * 60)


def pairwise_diff(lst):
    """
    Return list of pairwise differences (lst[i] - lst[i+1]).

    Args:
        lst: List of numeric values.

    Returns:
        List of differences.
    """

    diff = 0
    result = []
    for i in range(len(lst) - 1):
        # subtracting the alternate numbers
        diff = lst[i] - lst[i + 1]
        result.append(diff)

    return result


def is_valid_files(files: List[str], callback: Callable = None):
    """
    Validate that .dat files belong to same station and are consecutive.

    Args:
        files: List of file paths.
        callback: Optional function called with (success, failures).

    Returns:
        True if valid, False otherwise.
    """

    dates = []  # list[(yy, mm)]
    stations = []  # list[str]
    failures = []

    for file in files:
        base = os.path.basename(file)

        # Station ID from filename.
        stations.append(base[1:5] if base.startswith('s') else base[0:4])

        # Extract trailing YYMM right before file extension; otherwise first YYMM in name.
        m = re.search(r"(\d{4})(?=\.[^.]+$)", base) or re.search(r"(\d{4})", base)
        if not m:
            failures.append({'title': 'Error', 'message': f"Could not parse YYMM from '{base}'."})
            continue

        yy = int(m.group(1)[:2])
        mm = int(m.group(1)[2:4])
        if not (1 <= mm <= 12):
            failures.append({'title': 'Error', 'message': f"Parsed invalid month {mm:02d} from '{base}'."})
            continue

        dates.append((yy, mm))

    if failures:
        if callback:
            callback([], failures)
        return False

    # All files must be same station.
    if stations[1:] != stations[:-1]:
        if callback:
            callback([], [{'title': 'Error', 'message': 'Files selected are not all from the same station.'}])

        return False

    # Consecutive months in the order the user selected (wrap 12->1, yy+1).
    for i in range(len(dates) - 1):
        y1, m1 = dates[i]
        y2, m2 = dates[i + 1]
        exp_y, exp_m = (y1, m1 + 1) if m1 < 12 else ((y1 + 1) % 100, 1)
        if not (y2 == exp_y and m2 == exp_m):
            failures.append({
                'title': 'Error',
                'message': f"The months loaded are not adjacent or not sorted: {y1:02d}{m1:02d} -> {y2:02d}{m2:02d}."
            })

    if callback:
        if failures:
            callback([], failures)
        else:
            callback([{'title': 'Success', 'message': 'Files successfully loaded.'}], [])

    return len(failures) == 0


def find_outliers(t, data, channel_freq, idx_offset=0):
    """
    Find statistical outliers relative to moving average.

    Args:
        t: Time vector.
        data: NumPy array of values.
        channel_freq: Sampling interval in minutes.
        idx_offset: Index offset for concatenated months.

    Returns:
        Tuple of indices where outliers are detected.
    """

    _freq = channel_freq + 'min'

    nines_ind = np.where(data == 9999)
    nonines_data = data.copy()
    nonines_data[nines_ind] = float('nan')

    # Get a date range to create pandas time Series using the sampling frequency of the sensor.
    rng = date_range(t[0], t[-1], freq=_freq)
    ts = Series(nonines_data, rng)

    # Resample the data and linearly interpolate the missing values.
    upsampled = ts.resample(_freq)
    interp = upsampled.interpolate()

    # Calculate a window size for moving average routine so the window
    # size is always 60 minutes long.
    window_size = 60 // int(channel_freq)

    # Calculate moving average including the interolated data
    # moving_average removes big outliers before calculating moving average.
    y_av = moving_average(np.asarray(interp.tolist()), window_size)
    # y_av = self.moving_average(data, 30)
    # missing=np.argwhere(np.isnan(y_av))
    # y_av[missing] = np.nanmean(y_av)

    # Calculate the residual between the actual data and the moving average
    # and then find the data that lies outside of sigma*std.
    residual = nonines_data - y_av
    std = np.nanstd(residual)
    sigma = 3.0

    itemindex = np.where((nonines_data > y_av + (sigma * std)) | (nonines_data < y_av - (sigma * std)))

    # If we are loading multiple months we need to add (offset) the indices of newly found multipliers
    # by an offset, which is equal to the data count for the previous month.
    if len(itemindex[0]) > 0 and idx_offset:
        outlier_indices = (itemindex[0] + idx_offset,)
    else:
        outlier_indices = itemindex

    return outlier_indices


def moving_average(data, window_size):
    """
    Computes moving average using discrete linear convolution of two one dimensional sequences.

    Args:
        data: NumPy array of values.
        window_size: Size of the moving window.

    References:
    ------------
    [1] Wikipedia, "Convolution", http://en.wikipedia.org/wiki/Convolution.
    [2] API Reference: https://docs.scipy.org/doc/numpy/reference/generated/numpy.convolve.html

    Returns:
        NumPy array of smoothed values.
    """

    # REMOVE GLOBAL OUTLIERS FROM MOVING AVERAGE CALCULATION nk
    filtered_data = data.copy()

    my_mean = np.nanmean(filtered_data)
    my_std = np.nanstd(filtered_data)

    itemindex = np.where(((filtered_data > my_mean + 3 * my_std) | (filtered_data < my_mean - 3 * my_std)))
    filtered_data[itemindex] = np.nanmean(filtered_data)

    # Fix boundary effects by adding prepending and appending values to the data.
    head_slice = filtered_data[:window_size // 2]
    if np.isnan(head_slice).all() or len(head_slice) == 0:
        insert_vals = np.full(window_size, np.nan)
    else:
        insert_vals = np.ones(window_size) * np.nanmean(head_slice)
    filtered_data = np.insert(filtered_data, 0, insert_vals)
    filtered_data = np.insert(filtered_data, filtered_data.size,
                              np.ones(window_size) * np.nanmean(filtered_data[-window_size // 2:]))
    window = np.ones(int(window_size)) / float(window_size)

    return np.convolve(filtered_data, window, 'same')[window_size:-window_size]


def get_channel_priority(path: str, station_code: str):
    """
    Return list of primary channels for a station from .din file.

    Args:
        path: Path to .din file.
        station_code: Station code string.

    Returns:
        List of uppercase channel codes.
    """

    with open(path, 'r') as din_file:
        for line in din_file:
            if line[0:3] == station_code:
                channel_priority = [sensors.lower().strip('') for sensors in line[23:47].split(' ')]
                channel_priority = list(filter(None, channel_priority))
                channel_priority = list(map(str.upper, channel_priority))
                break  # stop reading the file once the station code is found

    return channel_priority


def extract_yyyymm_range(file_list):
    """
    Given a list of unpa or ts files, returns a YYYYMM range based on count:

    - If 1 file: both start and end = YYYYMM of that file
    - If 2 files: both start and end = latest YYYYMM
    - If 3 files: both start and end = middle YYYYMM
    - If 4+ files: start = second file, end = second-to-last file

    Args:
        file_list: List of filenames.

    Returns:
        Tuple (start_yyyymm, end_yyyymm).
    """

    if not file_list:
        raise ValueError("At least one file is required to determine a range.")

    current_yy = datetime.now().year % 100

    def extract_yyyymm(filename):
        basename = filename.split('/')[-1].split('.')[0]
        yymm = basename[-4:]
        yy = int(yymm[:2])
        mm = int(yymm[2:])
        century = 20 if yy <= current_yy else 19
        return century * 10000 + yy * 100 + mm

    file_list_sorted = sorted(file_list)

    if len(file_list) == 1:
        target_yyyymm = extract_yyyymm(file_list_sorted[0])
        return target_yyyymm, target_yyyymm
    elif len(file_list) == 2:
        target_yyyymm = extract_yyyymm(file_list_sorted[-1])
        return target_yyyymm, target_yyyymm
    elif len(file_list) == 3:
        target_yyyymm = extract_yyyymm(file_list_sorted[1])
        return target_yyyymm, target_yyyymm
    else:
        start_yyyymm = extract_yyyymm(file_list_sorted[1])
        end_yyyymm   = extract_yyyymm(file_list_sorted[-2])
        return start_yyyymm, end_yyyymm


def extract_yyyymm_range_from_months(months):
    """
    Given a list of Month objects (with resolved 4-digit years), return a (start_yyyymm, end_yyyymm)
    using the same UI rules as the filename-based version:
      - 1 file   : start=end = that month
      - 2 files  : start=end = latest month
      - 3 files  : start=end = middle month
      - 4+ files : start = second month, end = second-to-last month

    Args:
        months: List of Month objects with .year and .month.

    Returns:
        Tuple (start_yyyymm, end_yyyymm).
    """

    if not months:
        raise ValueError("At least one month is required to determine a range.")

    ms = sorted(months, key=lambda m: (m.year, m.month))
    n = len(ms)

    def yyyymm(m): return m.year * 100 + m.month

    if n == 1:
        t = yyyymm(ms[0])
        return t, t
    if n == 2:
        t = yyyymm(ms[-1])
        return t, t
    if n == 3:
        t = yyyymm(ms[1])
        return t, t

    return yyyymm(ms[1]), yyyymm(ms[-2])


def list_station_mat_files(root_dir, station_num_str, temporal_res):
    """
    Return sorted list of .mat files matching station and resolution.

    Args:
        root_dir: Root directory to search.
        station_num_str: Station identifier string.
        temporal_res: Either "daily" or other (treated as hourly).

    Returns:
        List of file paths.
    """

    if temporal_res == "daily":
        prefix = "da"
    else:
        prefix = "th"

    matches = []
    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            if name.startswith(prefix + station_num_str) and name.endswith(".mat"):
                matches.append(os.path.join(dirpath, name))

    return sorted(matches)


def load_and_concatenate_mat_files(mat_files):
    """
    Load and concatenate MATLAB .mat files into arrays.

    Args:
        mat_files: List of .mat file paths.

    Returns:
        Tuple (time_array, sealevel_array) sorted by time.
    """

    all_time = []
    all_sealevel = []

    for f in mat_files:
        data = sio.loadmat(f)
        time = np.ravel(data['time']) 
        sealevel = np.ravel(data['sealevel']) 

        all_time.append(time)
        all_sealevel.append(sealevel)

    # Concatenate into single arrays.
    time_combined = np.concatenate(all_time)
    sealevel_combined = np.concatenate(all_sealevel)

    # Sort by time (important if files are not in order).
    sort_idx = np.argsort(time_combined)

    return time_combined[sort_idx], sealevel_combined[sort_idx]
