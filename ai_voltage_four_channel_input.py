import nidaqmx
from nidaqmx.constants import TerminalConfiguration
import matplotlib.pyplot as plt
import numpy as np


with nidaqmx.Task() as task:
    # Assume that you have 2 analog input channels.
    task.ai_channels.add_ai_voltage_chan("Dev3/ai0:3", terminal_config=TerminalConfiguration.RSE)

    data = task.read(number_of_samples_per_channel=1000)

plt.figure()
fig, axs = plt.subplots(4)
fig.suptitle('AI0~3')
axs[0].plot(data[0])
axs[1].plot(data[1])
axs[2].plot(data[2])
axs[3].plot(data[3])
