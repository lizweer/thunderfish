# thunderfish

Automatically detect and analyze all EOD waveforms in a short recording.


## Authors

The [Neuroethology-lab](https://uni-tuebingen.de/en/faculties/faculty-of-science/departments/biology/institutes/neurobiology/lehrbereiche/neuroethology/) at the Institute of Neuroscience at the University of T&uuml;bingen:

- Jan Benda
- J&ouml;rg Henninger (harmonic groups)
- Juan Sehuanes (best window)
- Till Raab (annotation)
- Liz Weerdmeester (pulse clustering)


## Principles of operation

The sole task of `thunderfish` is to automatically detect and analyze
all EOD waveforms in a short recording. A short recording is
typically no longer than about 30 s. The recordings are made either
with a fishfinder (a stick with two electrodes used to find electric
fish in the field) or standaradized head-tail recordings in a little
tank.

1. A segement best suited for further waveform analysis is identified
   in the recording (bestwindow module). In this segement the
   amplitude of the recording is largest while at the same time most
   stable and not clipped.
2. A powerspectrum of a given frequency resolution is computed
   (powerspectrum module) and potential EOD frequencies of wave-type
   fish are detected in this power spectrum based on their harmonic
   structure (harmonics module).
3. EODs of pulse-type fish are detected and clustered according to
   their width, amplitude, and shape.
4. For each pulse and wave-type fish detected in the recording an
   averaged waveform is computed and its properties are analyzed
   (eodanalysis module)

The files generated by `thunderfish` on EOD waveform properties can be
summarized in single files by means of the [*collectfish*](collectfish.md) script
and then analyzed and explored with the [*eodexplorer*](eodexplorer.md).


## Command line arguments

```sh
thunderfish --help
```
returns
```plain
usage: thunderfish [-h] [--version] [-v] [-V] [-c] [--channel CHANNEL] [-a]
                   [-S] [-j [JOBS]] [-s]
                   [-f {dat,ascii,csv,rtai,md,tex,html,py}] [-p] [-P rtpwse]
                   [-m PDFFILE] [-l [MINFREQ]] [-o OUTPATH] [-k] [-b]
                   [file [file ...]]

Analyze EOD waveforms of weakly electric fish.

positional arguments:
  file                  name of a file with time series data of an EOD
                        recording

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v                    verbosity level. Increase by specifying -v multiple
                        times, or like -vvv
  -V                    level for debugging plots. Increase by specifying -V
                        multiple times, or like -VVV
  -c                    save configuration to file thunderfish.cfg after
                        reading all configuration files
  --channel CHANNEL     channel to be analyzed (defaults to first channel)
  -a                    plot all EOD waveforms
  -S                    plot spectra for all EOD waveforms
  -j [JOBS]             number of jobs run in parallel. Without argument use
                        all CPU cores.
  -s                    save analysis results to files
  -f {dat,ascii,csv,rtai,md,tex,html,py}
                        file format used for saving analysis results, defaults
                        to the format specified in the configuration file or
                        "dat"
  -p                    save output plot of each recording as pdf file
  -P rtpwse             save subplots as separate pdf files: r) recording with
                        best window, t) data trace with detected pulse fish,
                        p) power spectrum with detected wave fish, w/W) mean
                        EOD waveform, s/S) EOD spectrum, e/E) EOD waveform and
                        spectra. Capital letters produce a single multipage
                        pdf containing plots of all detected fish
  -m PDFFILE            save all plots of all recordings in a multi pages pdf
                        file. Disables parallel jobs.
  -l [MINFREQ]          logarithmic frequency axis in power spectrum with
                        optional minimum frequency (defaults to 100 Hz)
  -o OUTPATH            path where to store results and figures (defaults to
                        current working directory)
  -k                    keep path of input file when saving analysis files,
                        i.e. append path of input file to OUTPATH
  -b                    show the cost function of the best window algorithm

version 1.9.1 by Benda-Lab (2015-2020)

examples:
- analyze the single file data.wav interactively:
  > thunderfish data.wav
- automatically analyze all wav files in the current working directory and save analysis results and plot to files:
  > thunderfish -s -p *.wav
- analyze all wav files in the river1/ directory, use all CPUs, and write files directly to "results/":
  > thunderfish -j -s -p -o results/ river1/*.wav
- analyze all wav files in the river1/ directory and write files to "results/river1/":
  > thunderfish -s -p -o results/ -k river1/*.wav
- write configuration file:
  > thunderfish -c
```


## Configuration file

Many parameters of the algorithms used by thunderfish can be set via a
configuration file.

Generate the configuration file by executing
```
thunderfish -c
```
This first reads in all configuration files found (see below) and then writes
the file `thunderfish.cfg` into the current working directory.

Whenever you run thunderfish it searches for configuration files in 

1. the current working directory 
2. the directory of each input file
3. the parent directories of each input file, up to three levels up.

Best practice is to move the configuration file at the root of the file tree
where data files of a recording session are stored.

Use the `-vv` switch to see which configuration files are loaded:
```
thunderfish -vv data.wav
```

Open the configuration file in your favourite editor and edit the settings.
Each parameter is briefly explained in the comment preceding the parameter.


### Important configuration parameter

The list of configuration parameter is overwhelming and most of them
you do not need to touch at all. Here is a list of the few that matter
(in the rder as they appear in the configuration file):

- `frequencyResolution`: this sets the nnft parameter for computing
  the power spectrum such to achieve the requested resolution in
  frequency. The longer your analysis window the smaller you can set the
  resultion (not smaller then the inverse analysis window).

- `numberPSDWindows`: If larger than one then only fish that are
  present in all windows are reported. If you have very stationary data 
  (from a restrained fish, not from a fishfinder) you may set this to one.

- `lowThresholdFactor`, `highThresholdFactor`: play around with these
  numbers if not all wavefish are detected or if too many peaks are
  detected in the power spectrum.

- `mainsFreq`: Set it to the frequency of your mains power supply
  (50 or 60 Hz) or to zero if you have hum-free recordings.

- `maxRelativePower`: Usually, the higher the harmonics the less power
  it has. In order to discard signals whose power does not decay set this
  -10 or -20 dB.  

- `maxGroups`: Set to 1 if you know that only a single fish is in your
  recording.

- `minDataAmplitude`, `maxDataAmplitude`: If the maximum voltage range
  your recording device differs from -1 to 1 (default for WAV files),
  set these two parameter to the limits, so that clipped recordings
  are detected as such.

- `bestWindowSize`: How much of the data should be used for analysis.
  If you have stationary data (from a restrained fish, not from a
  fishfinder) you may want to use the full recording by setting this
  to zero. Otherwise thunderfish searches for the most stationary data
  segment of the requested length.

- `pulseWidthPercentile`: If low frequency pulse fish are missed then
  reduce this number.

- `eodMaxEODs`: The average waveform is estimated by averaging over at
  maximum this number of EODs. If wavefish change their frequency then
  you do not want to set this number too high (10 to 100 is enough for
  reducing noise). If you have several fish on your recording then
  this number needs to be high (1000) to average away the other fish.
  Set it to zero in order to use all EODs in the data segement
  selected for analysis.

- `flipWaveEOD`, `flipPulseEOD`: In case if fishfinder recordings you
  do not know the orientation of the fish relative to your
  electrode. That is you do not know the polarity of your recording.
  Setting this to `auto` flips the sign of the averaged EOD waveform
  to a standardized polarity (wave-type fish: larger peak relative to
  average is positive, pulse-type fish: the first of the two largest
  peaks is positive).

- `fileFormat`: sets the default file format to be used for storing
  the analysis results.


## Summary plot

In the plot you can press

- `q`: Close the plot and show the next one or quit.
- `p`: Play the analyzed section of the reording on the default audio device.
- `o`: Switch on zoom mode. You can draw a rectangle with the mouse to zoom in.
- `Backspace`: Zoom back. 
- `f`: Toggle full screen mode.


## Output files

With the `-s` switch analysis results are saved to files and no
interactive output is generated.

Output files are placed in the current working directory if no path is
specified via the `-o` switch. If the path specified via `-o` does not
exist it is created.

With the `-k` switch the pathes of the input files are appended to the
output path. This allows you to analyse recordings organized in a
nested directory structure in one step and write the files in the same
structure. For example:
```
thunderfish -s -k -o analysis river1/habitatA/*.wav river1/habitatB/*.wav river2/*.wav
```
will store the files in
```
analysis/river1/habitatA/
analysis/river1/habitatB/
analysis/river2/
```
whereas without the `-k` switch all files are stored in
```
analysis/
```

To make use of all the cores of your CPU apply the `-j` switch.

The following files are generated:

- `RECORDING-eodwaveform-N.EXT`: averaged EOD waveform
- `RECORDING-waveeodfs.EXT`: list of all detected EOD frequencies and powers of wave-type fish
- `RECORDING-wavefish.EXT`: list of properties of good EODs of wave-type fish
- `RECORDING-wavespectrum-N.EXT`: for each wave-type fish the Fourier spectrum
- `RECORDING-pulsefish.EXT`: list of properties of good EODs of pulse-type fish
- `RECORDING-pulsepeaks-N.EXT`: for each pulse-type fish properties of peaks and troughs
- `RECORDING-pulsespectrum-N.EXT`: for each pulse-type fish the power spectrum of a single pulse

Filenames are composed of the basename of the input file (`RECORDING`).
Fish detected in the recordings are numbered, starting with 0 (`N`).
The file extension depends on the chosen file format (`EXT`).
The following sections describe the content of the generated files.


### RECORDING-eodwaveform-N.EXT

For each fish the average waveform with standard deviation and fit.

<table>
<thead>
  <tr>
    <th align="left">time</th>
    <th align="left">mean</th>
    <th align="left">std</th>
    <th align="left">fit</th>
  </tr>
  <tr>
    <th align="left">ms</th>
    <th align="left">a.u.</th>
    <th align="left">a.u.</th>
    <th align="left">a.u.</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">-1.746</td>
    <td align="right">-0.34837</td>
    <td align="right">0.01194</td>
    <td align="right">-0.34562</td>
  </tr>
  <tr>
    <td align="right">-1.723</td>
    <td align="right">-0.30700</td>
    <td align="right">0.01199</td>
    <td align="right">-0.30411</td>
  </tr>
  <tr>
    <td align="right">-1.701</td>
    <td align="right">-0.26664</td>
    <td align="right">0.01146</td>
    <td align="right">-0.26383</td>
  </tr>
  <tr>
    <td align="right">-1.678</td>
    <td align="right">-0.22713</td>
    <td align="right">0.01153</td>
    <td align="right">-0.22426</td>
  </tr>
  <tr>
    <td align="right">-1.655</td>
    <td align="right">-0.18706</td>
    <td align="right">0.01187</td>
    <td align="right">-0.18428</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `time` Time in milliseconds.
2. `mean` Averaged waveform in the unit of the input data.
3. `std` Corresponding standard deviation.
4. `fit` A fit to the averaged waveform. In case of a wave fish this is
   a Fourier series, for pulse fish it is an exponential fit to the tail of the last peak.


### RECORDING-waveeodfs.EXT

List of all detected EOD frequencies and powers of wave-type fish.
These might be more than listed in `RECORDING-wavefish.EXT`.

<table>
<thead>
  <tr>
    <th align="left">index</th>
    <th align="left">EODf</th>
    <th align="left">power</th>
  </tr>
  <tr>
    <th align="left">-</th>
    <th align="left">Hz</th>
    <th align="left">dB</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">1</td>
    <td align="right">111.33</td>
    <td align="right">-33.35</td>
  </tr>
  <tr>
    <td align="right">2</td>
    <td align="right">132.81</td>
    <td align="right">-37.86</td>
  </tr>
  <tr>
    <td align="right">0</td>
    <td align="right">580.08</td>
    <td align="right">-22.01</td>
  </tr>
  <tr>
    <td align="right">3</td>
    <td align="right">608.89</td>
    <td align="right">-45.45</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `index` Index of the fish (the number that is also used to number the files).
2. `EODf` EOD frequency in Hertz.
3. `power` Power of this EOD in decibel (sum over all peaks in the power spectrum 
   of the recording).


### RECORDING-wavefish.EXT

Fundamental EOD frequency and other properties of each
wave-type fish detected in the recording.

<table>
<thead>
  <tr>
    <th align="left" colspan="12">waveform</th>
    <th align="left" colspan="9">timing</th>
  </tr>
  <tr>
    <th align="left">index</th>
    <th align="left">EODf</th>
    <th align="left">p-p-amplitude</th>
    <th align="left">power</th>
    <th align="left">thd</th>
    <th align="left">dbdiff</th>
    <th align="left">maxdb</th>
    <th align="left">noise</th>
    <th align="left">rmserror</th>
    <th align="left">clipped</th>
    <th align="left">flipped</th>
    <th align="left">n</th>
    <th align="left">ncrossings</th>
    <th align="left">peakwidth</th>
    <th align="left">troughwidth</th>
    <th align="left">leftpeak</th>
    <th align="left">rightpeak</th>
    <th align="left">lefttrough</th>
    <th align="left">righttrough</th>
    <th align="left">p-p-distance</th>
    <th align="left">reltroughampl</th>
  </tr>
  <tr>
    <th align="left">-</th>
    <th align="left">Hz</th>
    <th align="left">a.u.</th>
    <th align="left">dB</th>
    <th align="left">%</th>
    <th align="left">dB</th>
    <th align="left">dB</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">-</th>
    <th align="left">-</th>
    <th align="left">-</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">%</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">0</td>
    <td align="right">580.08</td>
    <td align="right">0.22755</td>
    <td align="right">-21.28</td>
    <td align="right">149.81</td>
    <td align="right">2.93</td>
    <td align="right">-9.22</td>
    <td align="right">0.3</td>
    <td align="right">0.36</td>
    <td align="right">0.0</td>
    <td align="right">0</td>
    <td align="right">3300</td>
    <td align="right">1</td>
    <td align="right">76.15</td>
    <td align="right">23.85</td>
    <td align="right">69.12</td>
    <td align="right">7.03</td>
    <td align="right">11.10</td>
    <td align="right">12.75</td>
    <td align="right">18.13</td>
    <td align="right">312.11</td>
  </tr>
  <tr>
    <td align="right">1</td>
    <td align="right">111.33</td>
    <td align="right">0.00713</td>
    <td align="right">-50.80</td>
    <td align="right">67.60</td>
    <td align="right">7.18</td>
    <td align="right">-29.48</td>
    <td align="right">34.7</td>
    <td align="right">2.94</td>
    <td align="right">0.0</td>
    <td align="right">0</td>
    <td align="right">888</td>
    <td align="right">2</td>
    <td align="right">44.00</td>
    <td align="right">56.00</td>
    <td align="right">19.50</td>
    <td align="right">24.51</td>
    <td align="right">16.55</td>
    <td align="right">39.45</td>
    <td align="right">41.05</td>
    <td align="right">73.54</td>
  </tr>
  <tr>
    <td align="right">2</td>
    <td align="right">132.81</td>
    <td align="right">0.01029</td>
    <td align="right">-46.47</td>
    <td align="right">46.49</td>
    <td align="right">8.40</td>
    <td align="right">-32.48</td>
    <td align="right">22.0</td>
    <td align="right">1.55</td>
    <td align="right">0.0</td>
    <td align="right">0</td>
    <td align="right">1059</td>
    <td align="right">2</td>
    <td align="right">49.11</td>
    <td align="right">50.89</td>
    <td align="right">25.30</td>
    <td align="right">23.82</td>
    <td align="right">29.72</td>
    <td align="right">21.16</td>
    <td align="right">53.54</td>
    <td align="right">103.40</td>
  </tr>
  <tr>
    <td align="right">3</td>
    <td align="right">608.89</td>
    <td align="right">0.00258</td>
    <td align="right">-59.51</td>
    <td align="right">100.84</td>
    <td align="right">15.01</td>
    <td align="right">-22.24</td>
    <td align="right">40.9</td>
    <td align="right">1.37</td>
    <td align="right">0.0</td>
    <td align="right">0</td>
    <td align="right">4868</td>
    <td align="right">2</td>
    <td align="right">36.29</td>
    <td align="right">63.71</td>
    <td align="right">22.14</td>
    <td align="right">14.15</td>
    <td align="right">42.93</td>
    <td align="right">20.78</td>
    <td align="right">57.08</td>
    <td align="right">91.60</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `index` Index of the fish (the number that is also used to number the files).
2. `EODf` EOD frequency in Hertz.
3. `p-p-amplitude` Peak-to-peak amplitude in the units of the input data.
4. `power` Power of this EOD in decibel.
5. `thd`: Total harmonic distortion, i.e. square root of sum of amplitudes squared
   of harmonics relative to amplitude of fundamental.
6. `dbdiff` Smoothness of power spectrum as standard deviation of differences in decibel power.
7. `maxdb` Maximum power of higher harmonics relative to peak power in decibel.
8. `noise` Root-mean-squared standard error of the averaged EOD waveform relative to the
   peak-to_peak amplitude in percent.
9. `rmserror` Root-mean-squared difference between the averaged EOD waveform and 
   the fit of the Fourier series relative to the peak-to_peak amplitude in percent.
10. `clipped` Percentage of recording that is clipped.
11. `flipped` Whether the waveform was flipped.
12. `n` Number of EODs used for computing the averaged EOD waveform.
13. `ncrossings` Number of zero crossing per EOD period.
14. `peakwidth` Width of the peak at the averaged amplitude relative to EOD period.
15. `troughwidth` Width of the trough at the averaged amplitude relative to EOD period.
16. `leftpeak` Time from positive zero crossing to peak relative to EOD period.
17. `rightpeak` Time from peak to negative zero crossing relative to EOD period.
18. `lefttrough` Time from negative zero crossing to trough relative to EOD period.
19. `righttrough` Time from trough to positive zero crossing relative to EOD period.
20. `p-p-distance` Time between peak and trough relative to EOD period.
21. `reltroughampl` Amplitude of trough relative to peak amplitude.


### RECORDING-wavespectrum-N.EXT

The parameter of the Fourier series fitted to the waveform of a wave-type fish.

<table>
<thead>
  <tr>
    <th align="left">harmonics</th>
    <th align="left">frequency</th>
    <th align="left">amplitude</th>
    <th align="left">relampl</th>
    <th align="left">relpower</th>
    <th align="left">phase</th>
    <th align="left">power</th>
  </tr>
  <tr>
    <th align="left">-</th>
    <th align="left">Hz</th>
    <th align="left">a.u.</th>
    <th align="left">%</th>
    <th align="left">dB</th>
    <th align="left">rad</th>
    <th align="left">a.u.^2/Hz</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">0</td>
    <td align="right">728.16</td>
    <td align="right">0.32610</td>
    <td align="right">100.00</td>
    <td align="right">0.00</td>
    <td align="right">0.0000</td>
    <td align="right">1.0137e-01</td>
  </tr>
  <tr>
    <td align="right">1</td>
    <td align="right">1456.32</td>
    <td align="right">0.22146</td>
    <td align="right">67.91</td>
    <td align="right">-3.36</td>
    <td align="right">2.4706</td>
    <td align="right">4.1881e-02</td>
  </tr>
  <tr>
    <td align="right">2</td>
    <td align="right">2184.48</td>
    <td align="right">0.03215</td>
    <td align="right">9.86</td>
    <td align="right">-20.12</td>
    <td align="right">-1.9333</td>
    <td align="right">7.6623e-04</td>
  </tr>
  <tr>
    <td align="right">3</td>
    <td align="right">2912.63</td>
    <td align="right">0.03733</td>
    <td align="right">11.45</td>
    <td align="right">-18.83</td>
    <td align="right">-0.6807</td>
    <td align="right">8.6311e-04</td>
  </tr>
  <tr>
    <td align="right">4</td>
    <td align="right">3640.79</td>
    <td align="right">0.02039</td>
    <td align="right">6.25</td>
    <td align="right">-24.08</td>
    <td align="right">3.0997</td>
    <td align="right">2.3089e-04</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `harmonics` Index of the harmonics. The first one with index 0 is the fundamental frequency.
2. `frequency` Frequency of the harmonics in Hertz.
3. `amplitude` Amplitude of each harmonics obtained by fitting a Fourier series to the data in the unit of the input data.
4. `relampl` Amplitude of each harmonics relative to the amplitude of the fundamental in percent.
5. `relpower` Power of each harmonics relative to fundamental in decibel.
6. `phase` Phase of each harmonics obtained by fitting a Fourier series to the data in radians ranging from 0 to 2 pi.
7. `power` Power spectral density of the harmonics from the original power spectrum of the data.


### RECORDING-pulsefish.EXT

Properties of each pulse-type fish detected in the recording.

<table>
<thead>
  <tr>
    <th align="left" colspan="16">waveform</th>
    <th align="left" colspan="5">power spectrum</th>
  </tr>
  <tr>
    <th align="left">index</th>
    <th align="left">EODf</th>
    <th align="left">period</th>
    <th align="left">max-ampl</th>
    <th align="left">min-ampl</th>
    <th align="left">p-p-amplitude</th>
    <th align="left">noise</th>
    <th align="left">clipped</th>
    <th align="left">flipped</th>
    <th align="left">tstart</th>
    <th align="left">tend</th>
    <th align="left">width</th>
    <th align="left">tau</th>
    <th align="left">firstpeak</th>
    <th align="left">lastpeak</th>
    <th align="left">n</th>
    <th align="left">peakfreq</th>
    <th align="left">peakpower</th>
    <th align="left">poweratt5</th>
    <th align="left">poweratt50</th>
    <th align="left">lowcutoff</th>
  </tr>
  <tr>
    <th align="left">-</th>
    <th align="left">Hz</th>
    <th align="left">ms</th>
    <th align="left">a.u.</th>
    <th align="left">a.u.</th>
    <th align="left">a.u.</th>
    <th align="left">%</th>
    <th align="left">%</th>
    <th align="left">-</th>
    <th align="left">ms</th>
    <th align="left">ms</th>
    <th align="left">ms</th>
    <th align="left">ms</th>
    <th align="left">-</th>
    <th align="left">-</th>
    <th align="left">-</th>
    <th align="left">Hz</th>
    <th align="left">dB</th>
    <th align="left">dB</th>
    <th align="left">dB</th>
    <th align="left">Hz</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">0</td>
    <td align="right">30.72</td>
    <td align="right">32.55</td>
    <td align="right">0.797</td>
    <td align="right">0.838</td>
    <td align="right">1.635</td>
    <td align="right">0.7</td>
    <td align="right">0.0</td>
    <td align="right">0</td>
    <td align="right">-0.295</td>
    <td align="right">0.884</td>
    <td align="right">1.179</td>
    <td align="right">0.118</td>
    <td align="right">1</td>
    <td align="right">2</td>
    <td align="right">100</td>
    <td align="right">895.98</td>
    <td align="right">-66.31</td>
    <td align="right">-20.14</td>
    <td align="right">-18.71</td>
    <td align="right">159.14</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `index` Index of the fish (the number that is also used to number the files).
2. `EODf` EOD frequency in Hertz.
3. `period` Period between two pulses (1/EODf) in milliseconds.
4. `max-ampl` Amplitude of the largest peak (P1 peak) in the units of the input data.
5. `min-ampl` Amplitude of the largest trough in the units of the input data.
6. `p-p-amplitude` Peak-to-peak amplitude in the units of the input data.
7. `noise` Root-mean-squared standard error of the averaged EOD waveform relative to the
   peak-to_peak amplitude in percent.
8. `clipped` Percentage of recording that is clipped.
9. `flipped` Whether the waveform was flipped.
10. `tstart` Time where the pulse starts relative to P1 in milliseconds.
11. `tend` Time where the pulse ends relative to P1 in milliseconds.
12. `width` Total width of the pulse in milliseconds.
13. `tau` Time constant of the exponential decay of the tail of the pulse in milliseconds.
14. `firstpeak` Index of the first peak in the pulse (i.e. -1 for P-1)
15. `lastpeak` Index of the last peak in the pulse (i.e. 3 for P3)
16. `n` Number of EODs used for computing the averaged EOD waveform.
17. `peakfreq` Frequency at the peak power of the single pulse spectrum in Hertz.
18. `peakpower` Peak power of the single pulse spectrum in decibel.
19. `poweratt5` How much the average power below 5 Hz is attenuated relative to the peak power in decibel.
20. `poweratt50` How much the average power below 50 Hz is attenuated relative to the peak power in decibel.
21. `lowcutoff` Frequency at which the power reached half of the peak power relative to the initial power in Hertz.


### RECORDING-pulsepeaks-N.EXT

Properties of peaks and troughs of a pulse-type fish's EOD.

<table>
<thead>
  <tr>
    <th align="left">P</th>
    <th align="left">time</th>
    <th align="left">amplitude</th>
    <th align="left">relampl</th>
    <th align="left">width</th>
  </tr>
  <tr>
    <th align="left">-</th>
    <th align="left">ms</th>
    <th align="left">a.u.</th>
    <th align="left">%</th>
    <th align="left">ms</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">1</td>
    <td align="right">0.000</td>
    <td align="right">0.78409</td>
    <td align="right">100.00</td>
    <td align="right">0.333</td>
  </tr>
  <tr>
    <td align="right">2</td>
    <td align="right">0.385</td>
    <td align="right">-0.85939</td>
    <td align="right">-109.60</td>
    <td align="right">0.248</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `P` Name of the peak/trough. Peaks and troughs are numbered sequentially. P1 is the 
   largest peak with positive amplitude.
2. `time` Time of the peak/trough relative to P1 in milliseconds.
3. `amplitude` Amplitude of the peak/trough in the unit of the input data.
4. `relampl` Amplitude of the peak/trough relative to the amplitude of P1.
5. `width` Width of the peak/trough at half height in milliseconds. 


### RECORDING-pulsespectrum-N.EXT

The power spectrum of a single EOD pulse of a pulse-type fish:

<table>
<thead>
  <tr>
    <th align="left">frequency</th>
    <th align="left">power</th>
  </tr>
  <tr>
    <th align="left">Hz</th>
    <th align="left">a.u.^2/Hz</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="right">0.00</td>
    <td align="right">4.7637e-10</td>
  </tr>
  <tr>
    <td align="right">0.34</td>
    <td align="right">9.5284e-10</td>
  </tr>
  <tr>
    <td align="right">0.67</td>
    <td align="right">9.5314e-10</td>
  </tr>
  <tr>
    <td align="right">1.01</td>
    <td align="right">9.5363e-10</td>
  </tr>
  <tr>
    <td align="right">1.35</td>
    <td align="right">9.5432e-10</td>
  </tr>
  <tr>
    <td align="right">1.68</td>
    <td align="right">9.5522e-10</td>
  </tr>
</tbody>
</table>

The columns contain:

1. `frequency` Frequency in Hertz.
2. `power` Power spectral density.

