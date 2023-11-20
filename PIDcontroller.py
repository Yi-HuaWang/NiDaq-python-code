from nidaqmx.task import Task 
from nidaqmx import constants 
from nidaqmx.stream_readers import (AnalogSingleChannelReader, AnalogMultiChannelReader)
from nidaqmx.stream_writers import (AnalogSingleChannelWriter, AnalogMultiChannelWriter)
import numpy as np
from simple_pid import PID
pid = PID(0, 100, 0, setpoint=0)


samp_rate = 1000000
num_samp = 2
num_step = 15
# configuring ao task

ao_task =Task()
ao_task.ao_channels.add_ao_voltage_chan('/Dev3/ao0')
ao_task.timing.cfg_samp_clk_timing(rate = samp_rate, source = "ai/sampleclock", samps_per_chan = 1, sample_mode=constants.AcquisitionType.FINITE)
# ao_task.write(np.zeros(1000)) # just give a voltage 0 to output


# configuring ai task

ai_task = Task()

ai_task.ai_channels.add_ai_voltage_chan(physical_channel = '/Dev3/ai0')
ai_task.timing.cfg_samp_clk_timing(rate = samp_rate,  samps_per_chan = num_samp, sample_mode=constants.AcquisitionType.CONTINUOUS)
# run the task

writer = AnalogSingleChannelWriter(ao_task.out_stream, auto_start=False)
reader = AnalogSingleChannelReader(ai_task.in_stream)
ao_task.start()
ai_task.start()

values_read = np.zeros(num_samp, dtype=np.float64)




# ai_task.wait_until_done()
# ao_task.wait_until_done()
# data = ai_task.read(number_of_samples_per_channel = 1000)
i = 0
while True:
    reader.read_many_sample(values_read, number_of_samples_per_channel=num_samp, timeout=2)
    v = values_read[num_samp-1]
    control = pid(v)
    writer.write_one_sample(control, timeout=2)
    print(data)
    print(i)
    i += 1
    if i > num_step:
        break



# Assume we have a system we want to control in controlled_system
# v = controlled_system.update(0)

# while True:
#     # Compute new output from the PID according to the systems current value
#     control = pid(v)
    
#     # Feed the PID output to the system and get its current value
#     v = controlled_system.update(control)

ai_task.close()
ao_task.close()
