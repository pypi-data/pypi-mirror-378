from scipy.ndimage import gaussian_filter1d
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import spatial_maps.maps as mapp

def return_CH(probe_path:str = r"Q:\sachuriga\Sachuriga_Python/quattrocolo-nwb4fp/ASSY-236-F.prb", x_input, y_input):

    import pandas as pd
    import ast
    import pandas as pd

    # File path
    #file_path = r"Q:\sachuriga\Sachuriga_Python/quattrocolo-nwb4fp/ASSY-236-F.prb"

    # Read the file and parse the dictionary
    with open(probe_path, 'r') as file:
        # If the file starts with "channel_groups =", strip it
        content = file.read().replace("channel_groups =", "").strip()
        channel_groups = ast.literal_eval(content)

    # Now channel_groups contains the dictionary
    print("Loaded channel_groups:", channel_groups)

    # Assuming channel_groups is loaded from Step 1
    data = []
    for group_id, group_data in channel_groups.items():
        channels = group_data['channels']
        geometry = group_data['geometry']
        for channel in channels:
            x, y = geometry[channel]
            data.append({
                'group_id': group_id,
                'channel_id': channel,
                'x': x,
                'y': y
            })

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Sort by group_id and channel_id for clarity (optional)
    df = df.sort_values(by=['group_id', 'channel_id']).reset_index(drop=True)

    # Function to find the nearest channel_id given x and y coordinates
    def find_nearest_channel_id(x, y, dataframe):
        # Calculate Euclidean distance from input (x, y) to all points in the DataFrame
        distances = np.sqrt((dataframe['x'] - x)**2 + (dataframe['y'] - y)**2)
        # Find the index of the minimum distance
        nearest_idx = distances.idxmin()
        # Return the channel_id at that index
        return dataframe.loc[nearest_idx, 'channel_id'], distances[nearest_idx]

    channel_id, distance = find_nearest_channel_id(x_input, y_input, df)
    print(f"Nearest Channel ID for (x={x_input}, y={y_input}) is: {channel_id}")
    print(f"Distance to nearest point: {distance}")

    # Optionally print the full DataFrame for reference
    print("\nFull DataFrame:")
    print(df)
    return channel_id

def pos2speed(t,x,y,filter_speed=True,min_speed=0.05):
    delta_X = np.diff(x)
    delta_Y = np.diff(y)
    sampling_intervals = np.diff(t)
    average_sampling_interval = np.median(sampling_intervals)
    interval =round(average_sampling_interval, 4)
    samplingrate = 1/interval
    n = samplingrate * 0.025
    truncate = 4.0  # 默认值
    # 计算 sigma
    sigma = (n - 1) / (2 * truncate)

    # Calculate distances between points
    delta_S = np.sqrt(delta_X**2 + delta_Y**2)
    speeds = delta_S*samplingrate
    speeds = np.insert(speeds, 0, 0)
    smoothed_speed = gaussian_filter1d(speeds, sigma=sigma, truncate=truncate)

    if filter_speed==True:
        #smoothed_speed = gaussian_filter1d(speeds, sigma=sigma)
        mask = (speeds>=min_speed)
        filtered_smoothed_speed = smoothed_speed[mask]
        filtered_speeds = speeds[mask]
        valid_mask = (speeds>=0)


    xx=x
    yy=y
    tt=t
    x1 = xx[mask]
    y1= yy[mask]
    t1 = tt[mask]

    combined_array = np.column_stack((t[valid_mask], x[valid_mask], y[valid_mask]))
    raw_pos = np.column_stack((t1, x1, y1))
    return raw_pos,combined_array, mask, speeds[valid_mask],smoothed_speed[valid_mask], filtered_speeds

def speed_filtered_spikes(spikes_time, t, mask : list = []):
    # Calculate the extended time bins based on median differences
    median_diff = np.median(np.diff(t[1:]))
    t_ = np.append(t[1:], t[1:][-1] + median_diff)

    # Compute the histogram of spikes across these bins
    spikes_in_bin, _ = np.histogram(spikes_time, t_)

    # If a mask is provided, use it; otherwise return all spikes
    if len(mask) > 0.05:
        spk = spikes_in_bin[mask]
    else:
        spk = spikes_in_bin

    return spk

def load_speed_fromNWB(data):
    scaler = MinMaxScaler()
    # Fit and transform the data
    pos = data
    t = data.as_dataframe().index
    scaler = MinMaxScaler(feature_range=(0, 1))
    x = scaler.fit_transform(np.array(pos['x']).reshape(-1, 1)).flatten()
    y = scaler.fit_transform(np.array(pos['y']).reshape(-1, 1)).flatten()

    return np.column_stack((t, x, y))


def load_units_fromNWB(data, unit_num: int = 0):
    units = data
    spikes_time = np.array(units[unit_num].as_series().index)

    return spikes_time

def get_filed_num(matrix):
    # Collect all nonzero values
    distinct_values = set()
    for row in matrix:
        for val in row:
            if val > 0:
                distinct_values.add(val)
    return [v for v in distinct_values]

#def spikes2phase(theta_phase,t,spikestime):
