import matplotlib.pyplot as plt
import numpy as np


def response_plot(*filters, resp, logplot=True, title=''):

    fig, ax = plt.subplots()

    if resp == 'amp':
        #title = 'Amplitude Response - ' + title

        for f in filters:
            x, y = f.getAmpResp()
            x = np.array(x) / 1000

            if logplot:
                ylabel = 'Amplitude (dB)'
                y = 20 * np.log(y)
            else:
                ylabel = 'Amplitude'

            plt.plot(x, y, label=f.desc, linewidth=0.8)

    elif resp == 'phase':
        ylabel = 'Phase (rad)'
        #title = "Phase Response - " + title

        for f in filters:
            x, y = f.getPhaseResp()
            x = np.array(x) / 1000
            plt.plot(x, y, label=f.desc, linewidth=0.8)

    plt.title(title)
    plt.xlabel('Frequency (kHz)')
    plt.ylabel(ylabel)

    ax.set_xlim(0, 5)

    plt.grid()
    plt.legend()
    plt.show()


def waveform_plot(filter, title=''):
    sf = filter.samplfreq
    fig, ax = plt.subplots()

    x, y = filter.generateOutput()

    x = np.array(x)/sf * 1000
    y = np.array(y)
    print(y)

    scaling = 32767/np.amax(y)
    y = scaling * y

    #title = filter.desc + " Output Signal - " + title
    plt.title(title)

    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude')

    plt.plot(x, y, linewidth=0.5)

    ax.set_xlim(0, 25)
    plt.grid()
    plt.show()
