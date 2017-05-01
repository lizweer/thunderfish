"""
Compute and plot powerspectra and spectrograms for a given minimum frequency resolution.

next_power_of_two(): Round an integer up to the next power of two.
nfff_overlap():      Compute nfft and overlap based on a requested minimum frequency resolution
                     and overlap fraction.
                
psd():                  Compute power spectrum with a given frequency resolution.
decibel():              Transform power to decibel.
power():                Transform decibel to power.
plot_decibel_psd():     Plot power spectrum in decibel.
multi_resolution_psd(): Performs the steps to calculate a powerspectrum.
spectrogram():          Spectrogram of a given frequency resolution and overlap fraction.
"""

import numpy as np
import scipy.signal as scps

try:
    import matplotlib.mlab as mlab
except ImportError:
    pass


def next_power_of_two(n):
    """The next integer power of two.
    
    Parameters
    ----------
    n: int or float
        A positive number.

    Returns
    -------
    m: int
        The next integer power of two equal or larger than `n`.
    """
    return int(2 ** np.floor(np.log(n) / np.log(2.0) + 1.0-1e-8))


def nfft_noverlap(freq_resolution, samplerate, overlap_frac, min_nfft=16):
    """The required number of points for an FFT to achieve a minimum frequency resolution
    and the number of overlapping data points.

    Parameters
    ----------
    freq_resolution: float
        The minimum required frequency resolution in Hertz.
    samplerate: float
        The sampling rate of the data in Hertz.
    overlap_frac: float
        The fraction the FFT windows should overlap.
    min_nfft: int
        The smallest value of nfft to be used.

    Returns
    -------
    nfft: int
        The number of FFT points.
    noverlap: int
        The number of overlapping FFT points.
    """
    nfft = next_power_of_two(samplerate / freq_resolution)
    if nfft < min_nfft:
        nfft = min_nfft
    noverlap = int(nfft * overlap_frac)
    return nfft, noverlap


def psd(data, samplerate, fresolution, min_nfft=16, detrend=mlab.detrend_none,
        window=mlab.window_hanning, overlap_frac=0.5, pad_to=None,
        sides='default', scale_by_freq=None):
    """Power spectrum density of a given frequency resolution.

    NFFT is computed from the requested frequency resolution and the samplerate.
    
    data: 1-D array
        Data array you want to calculate a psd of.
    samplerate: float
        Sampling rate of the data in Hertz.
    fresolution: float
        Frequency resolution of the psd in Hertz.
    overlap_frac: float
        Fraction of overlap for the fft windows.
    See numpy.psd for the remaining parameter.

    Returns
    -------
    psd: 2-D array
        Power and frequency.
    """

    nfft, noverlap = nfft_noverlap(fresolution, samplerate, overlap_frac, min_nfft=min_nfft)
    power, freqs = mlab.psd(data, NFFT=nfft, noverlap=noverlap, Fs=samplerate, detrend=detrend, window=window,
                            pad_to=pad_to, sides=sides, scale_by_freq=scale_by_freq)
    return np.asarray([np.squeeze(power), freqs])   # squeeze is necessary when nfft is to large with respect to the data


def decibel(power, ref_power=1.0, min_power=1e-20):
    """
    Transform power to decibel relative to ref_power.
    ```
    decibel = 10 * log10(power/ref_power)
    ```

    Parameters
    ----------
    power: array
        Power values of the power spectrum or spectrogram.
    ref_power: float
        Reference power for computing decibel. If set to `None` the maximum power is used.
    min_power: float
        Power values smaller than `min_power` are set to `np.nan`.

    Returns
    -------
    decibel_psd: array
        Power values in decibel.
    """
    if ref_power is None:
        ref_power = np.max(power)
    decibel_psd = power.copy()
    decibel_psd[power < min_power] = np.nan
    decibel_psd[power >= min_power] = 10.0 * np.log10(decibel_psd[power >= min_power]/ref_power)
    return decibel_psd


def power(decibel, ref_power=1.0):
    """
    Transform decibel back to power relative to ref_power.
    ```
    power = ref_power * 10**(0.1 * decibel)
    ```
    
    Parameters
    ----------
    decibel: array
        Decibel values of the power spectrum or spectrogram.
    ref_power: float
        Reference power for computing power.

    Returns
    -------
    power: array
        Power values of the power spectrum or spectrogram.
    """
    return ref_power * 10.0 ** (0.1 * decibel)


def plot_decibel_psd(ax, freqs, power, ref_power=1.0, min_power=1e-20, max_freq=2000.0, **kwargs):
    """
    Plot the powerspectum in decibel relative to ref_power.

    Parameters
    ----------
    ax:
        Axis for plot.
    freqs: 1-D array
        Frequency array of the power spectrum.
    power: 1-D array
        Power values of the power spectrum.
    ref_power: float
        Reference power for computing decibel. If set to `None` the maximum power is used.
    min_power: float
        Power values smaller than `min_power` are set to `np.nan`.
    max_freq: float
        Limits of frequency axis are set to `(0, max_freq)` if `max_freq` is greater than zero
    kwargs:
        Plot parameter that are passed on to the `plot()` function.
    """
     
    decibel_psd = decibel(power, ref_power=ref_power, min_power=min_power)
    ax.plot(freqs, decibel_psd, **kwargs)
    ax.set_xlabel('Frequency [Hz]')
    if max_freq > 0.0:
        ax.set_xlim(0, max_freq)
    else:
        max_freq = freqs[-1]
    pmin = np.nanmin(decibel_psd[freqs < max_freq])
    pmin = np.floor(pmin / 10.0) * 10.0
    pmax = np.nanmax(decibel_psd[freqs < max_freq])
    pmax = np.ceil(pmax / 10.0) * 10.0
    ax.set_ylim(pmin, pmax)
    ax.set_ylabel('Power [dB]')


def multi_resolution_psd(data, samplerate, fresolution=0.5,
                         detrend=mlab.detrend_none, window=mlab.window_hanning,
                         overlap=0.5, pad_to=None, sides='default',
                         scale_by_freq=None, min_nfft=16):
    """Compute powerspectrum with a given frequency resolution.

    Two other functions are called to first calculate the nfft value and second calculate the powerspectrum. The given
    frequencyresolution can be a float or a list/array of floats.

    Parameters
    ----------
    data: 1-D array
        Data array you want to calculate a psd of.
    samplerate: float
        Sampling rate of the data in Hertz.
    fresolution: float or 1-D array
        Frequency resolutions for one or multiple psds in Hertz.
    overlap: float
        Fraction of overlap for the fft windows.
    For information on further arguments see `numpy.psd` documentation.

    Returns
    -------
    multi_psd_data: 3-D or 2-D array
        If the power spectrum is calculated for one frequency resolution
        a 2-D array with the single power spectrum is returned (`psd_data[power, freq]`).
        If the power sepctrum is calculated for multiple frequency resolutions
        a list of 2-D array is returned (`psd_data[frequency_resolution][power, freq]`).
    """
    return_list = True
    if not hasattr(fresolution, '__len__'):
        return_list = False
        fresolution = [fresolution]

    multi_psd_data = []
    for fres in fresolution:
        psd_data = psd(data, samplerate, fres, min_nfft, detrend, window, overlap, pad_to, sides, scale_by_freq)
        multi_psd_data.append(psd_data)

    if not return_list:
        multi_psd_data = multi_psd_data[0]

    return multi_psd_data


def spectrogram(data, samplerate, fresolution=0.5, detrend=mlab.detrend_none, window=mlab.window_hanning,
                overlap_frac=0.5, pad_to=None, sides='default', scale_by_freq=None, min_nfft=16):
    """
    Spectrogram of a given frequency resolution.

    Parameters
    ----------
    data: array
        Data for the spectrogram.
    samplerate: float
        Samplerate of data in Hertz.
    fresolution: float
        Frequency resolution for the spectrogram.
    overlap_frac: float
        Overlap of the nffts (0 = no overlap; 1 = total overlap).

    Returns
    -------
    spectrum: 2d array
        Contains for every timestamp the power of the frequencies listed in the array `freqs`.
    freqs: array
        Frequencies of the spectrogram.
    time: array
        Time of the nfft windows.
    """

    nfft, noverlap = nfft_noverlap(fresolution, samplerate, overlap_frac, min_nfft=min_nfft)

    spectrum, freqs, time = mlab.specgram(data, NFFT=nfft, Fs=samplerate, detrend=detrend, window=window,
                                          noverlap=noverlap, pad_to=pad_to, sides=sides, scale_by_freq=scale_by_freq)
    return spectrum, freqs, time


if __name__ == '__main__':
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        pass

    print('Computes powerspectrum of a created signal of two wavefish (300 and 450 Hz)')
    print('')
    print('Usage:')
    print('  python powerspectrum.py')
    print('')

    fundamentals = [300, 450]  # Hz
    samplerate = 100000.0      # Hz
    time = np.arange(0.0, 8.0, 1.0/samplerate)
    data = np.sin(2*np.pi*fundamentals[0]*time) + 0.5*np.sin(2*np.pi*fundamentals[1]*time)

    psd_data = multi_resolution_psd(data, samplerate, fresolution=[0.5, 1])

    fig, ax = plt.subplots()
    plot_decibel_psd(ax, psd_data[0][1], psd_data[0][0], lw=2)
    plot_decibel_psd(ax, psd_data[1][1], psd_data[1][0], lw=2)
    plt.show()
