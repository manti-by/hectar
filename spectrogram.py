import numpy as np
import scipy.io.wavfile as wav
from matplotlib import pyplot as plt
from numpy.lib import stride_tricks


def short_time_fourier_transform(sig, frame_size, overlap_factor: float = 0.5, window: callable = np.hanning):
    """Short time fourier transform of audio signal"""
    win = window(frame_size)
    hop_size = int(frame_size - np.floor(overlap_factor * frame_size))

    # Zeros at beginning (thus center of 1st window should be for sample nr. 0)
    sample_count = np.append(np.zeros(int(np.floor(frame_size / 2.0))), sig)

    # Cols for windowing
    cols = np.ceil((len(sample_count) - frame_size) / float(hop_size)) + 1

    # Zeros at end (thus samples can be fully covered by frames)
    sample_count = np.append(sample_count, np.zeros(frame_size))

    frames = stride_tricks.as_strided(
        sample_count,
        shape=(int(cols), frame_size),
        strides=(sample_count.strides[0] * hop_size, sample_count.strides[0]),
    ).copy()
    frames *= win

    return np.fft.rfft(frames)


def log_scale_frequency(spec, sr: int = 44100, factor: float = 20.0):
    """Scale frequency axis logarithmically"""
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins - 1) / max(scale)
    scale = np.unique(np.round(scale))

    # Create spectrogram with new freq bins
    new_spec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            new_spec[:, i] = np.sum(spec[:, int(scale[i]):], axis=1)
        else:
            new_spec[:, i] = np.sum(spec[:, int(scale[i]): int(scale[i + 1])], axis=1)

    # List center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1.0 / sr)[: freqbins + 1])
    frequencies = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            frequencies += [np.mean(allfreqs[int(scale[i]) :])]
        else:
            frequencies += [np.mean(allfreqs[int(scale[i]) : int(scale[i + 1])])]

    return new_spec, frequencies, timebins, freqbins


if __name__ == "__main__":
    binsize = 2**10
    samplerate, samples = wav.read("examples/in.wav")
    s = short_time_fourier_transform(samples, binsize)

    s_show, freq, time_bins, freq_bins = log_scale_frequency(s, factor=1.0, sr=samplerate)
    ims = 20.0 * np.log10(np.abs(s_show) / 10e-6)  # Amplitude to Decibel
    plt.figure(figsize=(15, 7.5))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap="jet", interpolation="none")
    plt.colorbar()

    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.xlim([0, time_bins - 1])
    plt.ylim([0, freq_bins])

    x_locs = np.float32(np.linspace(0, time_bins - 1, 5))
    plt.xticks(
        x_locs,
        [f"{x}.02f" for x in ((x_locs * len(samples) / time_bins) + (0.5 * binsize)) / samplerate],
    )
    y_locs = np.int16(np.round(np.linspace(0, freq_bins - 1, 10)))
    plt.yticks(y_locs, ["%.02f" % freq[i] for i in y_locs])

    plt.show()
    plt.clf()
