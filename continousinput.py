# Import dependencies
import matplotlib.pyplot as plt
import numpy as np
import h5py

import nidaqmx
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx import constants

import threading
import pickle
from datetime import datetime
import scipy.io
import gc
gc.collect()
# Parameters
sampling_freq_in = 1000  # in Hz
buffer_in_size = 1000
pretrigger_samples = 10
bufsize_callback = 600
buffer_in_size_cfg = round(buffer_in_size * 1)  # clock configuration
chans_in = 1  #number of active channels
refresh_rate_plot = 10  # in Hz
crop = 5  # number of seconds to drop at acquisition start before saving
my_filename = 'DAQ_test'  # with full path if target folder different from current folder (do not leave trailing /)
analog_device_name = "Dev1/ai0"  # device name (see NI MAX)
digital_device_name = "/Dev1/PFI0"  # device name (see NI MAX)



data = np.zeros((1))  #this will fill the first column with zeros

# Definitions of basic functions
def ask_user():
    global running
    input("Press ENTER stop acquisition.")
    running = False


def cfg_read_task(acquisition):  # uses above parameters
    acquisition.ai_channels.add_ai_voltage_chan(analog_device_name)  # has to match with chans_in
    acquisition.triggers.start_trigger.cfg_dig_edge_start_trig(digital_device_name, trigger_edge = constants.Edge.FALLING)
    acquisition.timing.cfg_samp_clk_timing(rate=sampling_freq_in, sample_mode=constants.AcquisitionType.FINITE,
                                           samps_per_chan=buffer_in_size_cfg)

def reading_task_callback(task_idx, event_type, num_samples, callback_data):  # bufsize_callback is passed to num_samples
    global data
    global buffer_in
    if running:
        buffer_in = np.zeros((num_samples))
        stream_in.read_many_sample(buffer_in, num_samples, timeout=30)
        data = np.append(data, buffer_in)  # appends buffered data to total variable data
        data = np.append(data, 10)  # appends buffered data to total variable data

    return 0  # Absolutely needed for this callback to be well defined (see nidaqmx doc).

# Configure and setup the tasks
task_in = nidaqmx.Task()
cfg_read_task(task_in)
stream_in = AnalogSingleChannelReader(task_in.in_stream)
task_in.register_every_n_samples_acquired_into_buffer_event(bufsize_callback, reading_task_callback)

# Start threading to prompt user to stop
thread_user = threading.Thread(target=ask_user)
thread_user.start()

# Main loop
running = True
time_start = datetime.now()

task_in.start()

# Plot a visual feedback for the user's mental health
f, (ax1) = plt.subplots(1, 1, sharex='all', sharey='none')
while running:  # make this adapt to number of channels automatically

    ax1.clear()

    ax1.plot(data[-sampling_freq_in * 10:].T)  # 5 seconds rolling window

    # Label and axis formatting
    ax1.set_ylabel('voltage [V]')
    xticks = np.arange(0, data[-sampling_freq_in * 10:].size, sampling_freq_in)
    xticklabels = np.arange(0, xticks.size, 1)
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xticklabels)
    plt.show()
    plt.pause(1/refresh_rate_plot)  # required for dynamic plot to work (if too low, nulling performance bad)


# Close task to clear connection once done
task_in.stop()
task_in.close()
duration = datetime.now() - time_start


# Final save data and metadata ... first in python reloadable format:
filename = my_filename
with open(filename, 'wb') as f:
    pickle.dump(data, f)

# Some messages at the end
num_samples_acquired = data[:].size
print("\n")
print("acquisition ended.\n")
print("Acquisition duration: {}.".format(duration))
print("Acquired samples: {}.".format(num_samples_acquired - 1))


# Final plot of whole time course the acquisition
plt.close('all')
f_tot, (ax1) = plt.subplots(1, 1, sharex='all', sharey='none')
ax1.plot(data[10:].T)  # note the exclusion of the first 10 iterations (automatically zoomed in plot)
# Label formatting ...
ax1.set_xlabel('time [s]')
ax1.set_ylabel('voltage [V]')
xticks = np.arange(data[ :].size, sampling_freq_in)
xticklabels = np.arange(0, xticks.size, 1)
ax1.set_xticks(xticks)
ax1.set_xticklabels(xticklabels)
plt.show()
