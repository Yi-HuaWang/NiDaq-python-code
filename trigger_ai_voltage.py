import nidaqmx
import nidaqmx.constants as cst
import matplotlib.pyplot as plt
import numpy as np
from nidaqmx.stream_readers import AnalogSingleChannelReader

sample_time = 0.05  # units = seconds
s_freq = 100000
num_samples = int(sample_time*s_freq)
print(num_samples)

dt = 1/s_freq
diffTerminal = cst.TerminalConfiguration.RSE
Volts = cst.VoltageUnits.VOLTS
sampleMode = cst.AcquisitionType.FINITE
maxValue = 5
minValue = -5


task = nidaqmx.Task()


task.ai_channels.add_ai_voltage_chan("Dev3/ai0:1", terminal_config=diffTerminal,
max_val=maxValue, min_val=minValue, units = Volts)#name_to_assign_to_channel="mySignal",
task.ai_channels.ai_impedance = cst.Impedance1.FIFTY_OHMS

task.timing.cfg_samp_clk_timing(s_freq, sample_mode=sampleMode, samps_per_chan=num_samples)

task.triggers.start_trigger.cfg_dig_edge_start_trig("PFI0", trigger_edge=cst.Edge.FALLING)
# task.triggers.start_trigger.retriggerable = True

data = np.zeros((num_samples,), dtype=np.float64)
data1 = np.zeros((num_samples,), dtype=np.float64)

# comulativeData = np.zeros((24*num_samples,),dtype=np.float64)

reader = AnalogSingleChannelReader(task.in_stream)

task.control(cst.TaskMode.TASK_COMMIT)
task.start()
print('Wainting for trigger')

for ii in range(0,1):
    #task.start()
    reader.read_many_sample(data, number_of_samples_per_channel=num_samples,timeout=30)
    # comulativeData[ii*num_samples:(ii+1)*num_samples] = data
    #task.stop()
reader.read_many_sample(data, data1, number_of_samples_per_channel=num_samples,timeout=30)

task.stop()
task.close()
print('Acquisition Finished')
plt.figure()
plt.plot(data)
# plt.plot(comulativeData)
plt.show()
