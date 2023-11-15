import nidaqmx
# This is an object that manage the samples stream acquisition
from nidaqmx import stream_readers
import numpy as np
import matplotlib.pyplot as plt
import time

# This var is initialized during task creation and is needed by your callback
nidaq_reader: stream_readers.AnalogMultiChannelReader = None


def do_something_with_data(data):
    # Just for convenience
    plt.plot(data)
    plt.xlabel('time [samples]')
    plt.ylabel('voltage [V]')
    plt.grid()
    plt.show()
    

def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
    try:
        # Allocate your numpy array (I'm assuming just one channel!)
        data = np.empty((number_of_samples,))
        # Now read the acquired samples
        number_of_samples_read = nidaq_reader.read_many_sample(data, number_of_samples)
    except Exception as e:
        print(f'Something went wrong reading samples: {e}')
    else:
        do_something_with_data(data)
    finally:
        # Always needed by nidaqmx to return 0!
        return 0

def hardwareFiniteVoltage():
      sampleRate = 2E5   # Sample Rate in Hz
      secsToAcquire = 1    # Number of seconds over which to acquire data
      numberOfSamples = int(secsToAcquire * sampleRate)
      
      pretrigger_samples = 10000
      print('Acquiring %d data points' % numberOfSamples)
      with nidaqmx.Task('hardwareFiniteVoltage') as task:
         task.ai_channels.add_ai_voltage_chan('Dev1/ai0')
         task.timing.cfg_samp_clk_timing(sampleRate,samps_per_chan=numberOfSamples, 
         sample_mode=nidaqmx.constants.AcquisitionType(10178))
         
         task.triggers.reference_trigger.cfg_anlg_edge_ref_trig(
         'Dev1/ai0',pretrigger_samples,trigger_level=0.1)
         
         # Here you register your callback into nidaqmx event loop
         task.register_every_n_samples_acquired_into_buffer_event(numberOfSamples, callback)
         
         # Initialize the stream_readers nidaq_reader to be used by your callback to get your actual data
         global nidaq_reader
         nidaq_reader = stream_readers.AnalogSingleChannelReader(task.in_stream)
                                    
         task.start()




if __name__ == '__main__':
      hardwareFiniteVoltage()
      
      while True:
        # Event loop. Don't use `pass`! It will saturate the CPU
        time.sleep(0.001)
