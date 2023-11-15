import nidaqmx
import nidaqmx.constants as cst
import matplotlib.pyplot as plt
import numpy as np

sample_time = 0.05  # units = seconds
s_freq = 1000
num_pusles = 10
num_samples = int(sample_time*s_freq)
print(num_samples)
dt = 1/s_freq
diffTerminal = cst.TerminalConfiguration.RSE
Volts = cst.VoltageUnits.VOLTS
sampleMode_c = cst.AcquisitionType.FINITE
sampleMode_r = cst.AcquisitionType.CONTINUOUS

maxValue = 5
minValue = -5


Reader = nidaqmx.Task()
counter = nidaqmx.Task()

counter.co_channels.add_co_pulse_chan_freq("/Dev3/ctr0", freq = s_freq)
counter.timing.cfg_implicit_timing(sample_mode=sampleMode_c, samps_per_chan=num_samples)
counter.triggers.start_trigger.cfg_dig_edge_start_trig("/Dev3/PFI0", trigger_edge=cst.Edge.RISING)
counter.triggers.start_trigger.retriggerable = True

Reader.ai_channels.add_ai_voltage_chan("/Dev3/ai0", terminal_config=diffTerminal,
max_val=maxValue, min_val=minValue, units = Volts)#name_to_assign_to_channel="mySignal",
Reader.ai_channels.ai_impedance = cst.Impedance1.FIFTY_OHMS

Reader.timing.cfg_samp_clk_timing(s_freq, "/Dev3/PFI12", sample_mode=sampleMode_r, samps_per_chan=num_samples)


comulativeData = np.zeros((num_pusles*num_samples,),dtype=np.float64)

Reader.start()
counter.start()
print('Wainting for trigger')

comulativeData= Reader.read(number_of_samples_per_channel=num_pusles*num_samples, timeout=30)

Reader.stop()
Reader.close()
counter.stop()
counter.close()

print('Acquisition Finished')
plt.figure()
plt.plot(comulativeData)
# plt.plot(comulativeData)
plt.show()
