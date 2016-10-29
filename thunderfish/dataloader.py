import os.path
import glob
import numpy as np
import audioio as aio


def relacs_samplerate_unit(filename, channel=0):
    """
    Opens the corresponding stimuli.dat file and reads the sampling rate and unit.

    Parameters
    ----------
    filename: string
        path to a relacs data directory, a file in a relacs data directory,
        or a relacs trace-*.raw files.
    channel: int
        the channel (trace) number, if filename does not specify a trace-*.raw file.

    Returns
    -------
    samplerate: float
        the sampling rate in Hertz
    unit: string
        the unit of the trace, can be empty if not found

    Raises
    ------
    IOError/FileNotFoundError:
        If the stimuli.dat file does not exist.
    ValueError:
        stimuli.dat file does not contain sampling rate.
    """

    trace = channel+1
    relacs_dir = filename
    # check for relacs data directory:
    if not os.path.isdir(filename):
        relacs_dir = os.path.dirname(filename)
        bn = os.path.basename(filename)
        if (len(bn) > 5 and bn[0:5] == 'trace' and bn[-4:] == '.raw'):
            trace = int(bn[6:].replace('.raw', ''))

    # retreive sampling rate and unit from stimuli.dat file:
    samplerate = None
    unit = ""
    stimuli_file = os.path.join(relacs_dir, 'stimuli.dat')
    with open(stimuli_file, 'r') as sf:
        for line in sf:
            if len(line) == 0 or line[0] != '#':
                break
            if "unit%d" % trace in line:
                unit = line.split(':')[1].strip()
            if "sampling rate%d" % trace in line:
                value = line.split(':')[1].strip()
                samplerate = float(value.replace('Hz',''))

    if samplerate is not None:
        return samplerate, unit
    raise ValueError('could not retrieve sampling rate from ' + stimuli_file)


def relacs_metadata(filename):
    """
    Reads header of a relacs *.dat file.

    Parameters
    ----------
    filename: string
        a relacs *.dat file.

    Returns
    -------
    data: dict
        dictionary with the content of the file header.
        
    Raises
    ------
    IOError/FileNotFoundError:
        If filename cannot be opened.
    """
    
    data = {}
    with open(filename, 'r') as sf:
        for line in sf:
            if len(line) == 0 or line[0] != '#':
                break
            words = line.split(':')
            if len(words) >= 2:
                key = words[0].strip('# ')
                value = ':'.join(words[1:]).strip()
                data[key] = value
    return data


def check_relacs(filepathes):
    """
    Check whether filepathes are relacs files.

    Parameters
    ----------
    filepathes: string or list of strings
        path to a relacs data directory, a file in a relacs data directory,
        or relacs trace-*.raw files.

    Returns
    -------
    If filepathes is a single path, then returns True if it is a file in
    a valid relacs data directory.
    If filepathes are more than one path, then returns True if filepathes
    are trace-*.raw files in a valid relacs data directory.
    """

    path = filepathes
    # filepathes must be trace-*.raw:
    if type(filepathes) is list:
        if len(filepathes) > 1:
            for file in filepathes:
                bn = os.path.basename(file)
                if len(bn) <= 5 or bn[0:5] != 'trace' or bn[-4:] != '.raw':
                    return False
        path = filepathes[0]
    # relacs data directory:
    relacs_dir = path
    if not os.path.isdir(path):
        relacs_dir = os.path.dirname(path)
    # check for a valid relacs data directory:
    if (os.path.isfile(os.path.join(relacs_dir, 'stimuli.dat')) and
        os.path.isfile(os.path.join(relacs_dir, 'trace-1.raw'))):
        return True
    else:
        return False
    

def load_relacs(filepathes, channel=-1, verbose=0):
    """
    Load traces (trace-*.raw files) that have been recorded with relacs (www.relacs.net).

    Parameters
    ----------
    filepathes: string or list of string
        path to a relacs data directory, a relacs stimuli.dat file, a relacs info.dat file,
        or relacs trace-*.raw files.
    channel: int
        The data channel. If negative all channels are selected.
    verbose: int
        if > 0 show detailed error/warning messages

    Returns
    -------
    data: 1-D or 2-D array
        If channel is negative or more than one trace file is specified,
        a 2-D array with data of all channels is returned,
        where first dimension is time and second dimension is channel number.
        Otherwise an 1-D array with the data of that channel is returned.
    samplerate: float
        the sampling rate of the data in Hz
    unit: string
        the unit of the data

    Raises
    ------
    ValueError:
        - Invalid name for relacs trace-*.raw file.
        - Sampling rates of traces differ.
        - Unit of traces differ.
    """
    
    # fix pathes:
    if type(filepathes) is not list:
        filepathes = [filepathes]
    if len(filepathes) == 1:
        if os.path.isdir(filepathes[0]):
            if channel < 0:
                filepathes = glob.glob(os.path.join(filepathes[0], 'trace-*.raw'))
            else:
                filepathes[0] = os.path.join(filepathes[0], 'trace-%d.raw' % channel)
        else:
            bn = os.path.basename(filepathes[0])
            if len(bn) <= 5 or bn[0:5] != 'trace' or bn[-4:] != '.raw':
                if channel < 0:
                    filepathes = glob.glob(os.path.join(os.path.dirname(filepathes[0]),
                                                        'trace-*.raw'))
                else:
                    filepathes[0] = os.path.join(os.path.dirname(filepathes[0]),
                                                 'trace-%d.raw' % channel)
    else:
        channel = -1
                
    # load trace*.raw files:
    nchannels = len(filepathes)
    data = None
    nrows = 0
    samplerate = None
    unit = ""
    for n, path in enumerate(filepathes):
        bn = os.path.basename(path)
        if len(bn) <= 5 or bn[0:5] != 'trace' or bn[-4:] != '.raw':
            raise ValueError('invalid name %s of relacs trace file', path)
        x = np.fromfile(path, np.float32)
        if verbose > 0:
            print( 'loaded %s' % path)
        if data is None:
            nrows = len(x)-2
            data = np.empty((nrows, nchannels))
        data[:,n] = x[:nrows]
        # retrieve sampling rate and unit:
        rate, us = relacs_samplerate_unit(path)
        if samplerate is None:
            samplerate = rate
        elif rate != samplerate:
            raise ValueError('sampling rates of traces differ')
        if len(unit) == 0:
            unit = us
        elif us != unit:
            raise ValueError('unit of traces differ')
    if channel < 0:
        return data, samplerate, unit
    else:
        return data[:, 0], samplerate, unit


def check_pickle(filepath):
    """
    Check if filepath is a pickle file.
    
    Returns
    -------
    True, if fielpath is a pickle file.
    """
    ext = os.path.splitext(filepath)[1]
    return ext == 'pkl'


def load_pickle(filename, channel=-1, verbose=0):
    """
    Load Joerg's pickle files.

    Parameters
    ----------
    filepath: string
        The full path and name of the file to load.
    channel: int
        The data channel. If negative all channels are selected.
    verbose: int
        if > 0 show detailed error/warning messages

    Returns
    -------
    data: 1-D or 2-D array
        If channel is negative, a 2-D array with data of all channels is returned,
        where first dimension is time and second dimension is channel number.
        Otherwise an 1-D array with the data of that channel is returned.
    samplerate: float
        The sampling rate of the data in Hz.
    unit: string
        The unit of the data.
    """
    import pickle
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    if verbose > 0:
        print( 'loaded %s' % filename)
    time = data['time_trace']
    samplerate = 1000.0 / (time[1] - time[0])
    if channel >= 0:
        if channel >= data.shape[1]:
            raise IndexError('Invaliid channel number %d requested' % channel)
        data = data[:, channel]
        return data['raw_data'][:, channel], samplerate, 'mV'
    return data['raw_data'], samplerate, 'mV'


def load_data(filepath, channel=-1, verbose=0):
    """
    Call this function to load time-series data from a file.

    Parameters
    ----------
    filepath: string or list of strings
        The full path and name of the file to load. For some file
        formats several files can be provided.
    channel: int
        The data channel. If negative all channels are selected.
    verbose: int
        if > 0 show detailed error/warning messages

    Returns
    -------
    data: 1-D or 2-D array
        If channel is negative, a 2-D array with data of all channels is returned,
        where first dimension is time and second dimension is channel number.
        Otherwise an 1-D array with the data of that channel is returned.
    samplerate: float
        the sampling rate of the data in Hz
    unit: string
        the unit of the data

    Raise
    -----
    ValueError:
        Input argument filepath is empty string or list.
    IndexError:
        Invalid channel requested.
    """
    
    # check values:
    data = np.array([])
    samplerate = 0.0
    unit = ''
    if len(filepath) == 0:
        raise ValueError('input argument filepath is empty string or list.')

    # load data:
    if check_relacs(filepath):
        return load_relacs(filepath, channel, verbose)
    else:
        if type(filepath) is list:
            filepath = filepath[0]
        if check_pickle(filepath):
            return load_pickle(filepath, channel, verbose)
        else:
            data, samplerate = aio.load_audio(filepath, verbose)
            if channel >= 0:
                if channel >= data.shape[1]:
                    raise IndexError('Invaliid channel number %d requested' % channel)
                data = data[:, channel]
            unit = 'a.u.'
        return data, samplerate, unit


class DataLoader(aio.AudioLoader):
    """
    """

    def __init__(self, filepath=None, channel=-1, buffersize=10.0, backsize=0.0, verbose=0):
        """Initialize the DataLoader instance. If filepath is not None open the file.

        Args:
          filepath (string): name of the file
          channel (int): the single channel to be worked on
          buffersize (float): size of internal buffer in seconds
          backsize (float): part of the buffer to be loaded before the requested start index in seconds
          verbose (int): if >0 show detailed error/warning messages
        """
        super(DataLoader, self).__init__(filepath, buffersize, backsize, verbose)
        if channel > self.channels:
            channel = self.channels - 1
        self.channel = channel
        self.unit = 'a.u.'

    def __getitem__(self, key):
        if channel >= 0:
            if type(key) is tuple:
                raise IndexError
            return super(DataLoader, self).__getitem__((key, self.channel))
        else:
            return super(DataLoader, self).__getitem__(key)
 
    def __next__(self):
        if channel >= 0:
            return super(DataLoader, self).__next__()[self.channel]
        else:
            return super(DataLoader, self).__next__()
 
    def open(self, filepath, channel=0, buffersize=10.0, backsize=0.0, verbose=0):
        """Open data file for reading.

        Args:
          filepath (string): name of the file
          channel (int): the single channel to be worked on
          buffersize (float): size of internal buffer in seconds
          backsize (float): part of the buffer to be loaded before the requested start index in seconds
          verbose (int): if >0 show detailed error/warning messages
        """
        if type(filepath) is list:
            filepath = filepath[0]
        super(DataLoader, self).open(filepath, buffersize, backsize, verbose)
        if channel > self.channels:
            channel = self.channels - 1
        self.channel = channel
        if self.channel >= 0:
            self.shape = (self.frames,)
        else:
            self.shape = (self.frames, self.channels)
        self.unit = 'a.u.'
        return self


open_data = DataLoader

if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    
    print("Checking dataloader module ...")
    print('')
    print('Usage:')
    print('  python dataloader.py [-p] [-c <channel>] <datafile> <channel>')
    print('  -p: plot data')
    print('')

    n = 1
    plot = False
    if len(sys.argv) > n and sys.argv[n] == '-p':
        plot = True
        n += 1
    channel = 0
    if len(sys.argv) > n+1 and sys.argv[n] == '-c':
        channel = int(sys.argv[n+1])
        n += 2
    filepath = sys.argv[n:]
        
    print("try load_data:")
    data, samplerate, unit = load_data(filepath, channel, 2)
    if plot:
        if channel < 0:
            time = np.arange(len(data)) / samplerate
            for c in range(data.shape[1]):
                plt.plot(time, data[:, c])
        else:
            plt.plot(np.arange(len(data)) / samplerate, data)
        plt.xlabel('Time [s]')
        plt.ylabel('[' + unit + ']')
        plt.show()

    print('')
    print("try DataLoader for channel=%d:" % channel)
    with open_data(filepath, channel, 2.0, 1.0, 1) as data:
        print('samplerate: %g' % data.samplerate)
        print('frames: %d %d' % (len(data), data.shape[0]))
        nframes = int(1.0 * data.samplerate)
        # forward:
        for i in range(0, len(data), nframes):
            print('forward %d-%d' % (i, i + nframes))
            if channel < 0:
                x = data[i:i + nframes, 0]
            else:
                x = data[i:i + nframes]
            if plot:
                plt.plot((i + np.arange(len(x))) / data.samplerate, x)
                plt.xlabel('Time [s]')
                plt.ylabel('[' + data.unit + ']')
                plt.show()
        # and backwards:
        for i in reversed(range(0, len(data), nframes)):
            print('backward %d-%d' % (i, i + nframes))
            if channel < 0:
                x = data[i:i + nframes, 0]
            else:
                x = data[i:i + nframes]
            if plot:
                plt.plot((i + np.arange(len(x))) / data.samplerate, x)
                plt.xlabel('Time [s]')
                plt.ylabel('[' + data.unit + ']')
                plt.show()
                
