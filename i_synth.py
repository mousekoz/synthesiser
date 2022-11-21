from filters import Resonator
from filter_bank import Cascade, Parallel
import data_plots as dp

# Parameters: Formant frequency, formant bandwidth, sampling frequency
resonator1 = Resonator(310, 45, 10000)
resonator2 = Resonator(2020, 200, 10000)
resonator3 = Resonator(2960, 400, 10000)
resonator4 = Resonator(4000, 150, 10000)
resonator5 = Resonator(5000, 150, 10000)

cascade = Cascade(resonator1, resonator2, resonator3, resonator4, resonator5)
parallel = Parallel(resonator1, resonator2, resonator3, resonator4, resonator5)

dp.response_plot(cascade, parallel, resp='amp')
dp.response_plot(cascade, parallel, resp='phase')
dp.waveform_plot(cascade)
dp.waveform_plot(parallel)
