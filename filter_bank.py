import numpy as np
from filters import PreEmphasis, Differentiator, LowPass
from math import ceil

"""
Cascade filter bank

A cascade formant synthesiser using discrete-time
formant resonators connected in series.
"""


class Cascade:
    def __init__(self, *filter_objs, F_s=10000):
        self.filters = filter_objs
        self.samplfreq = F_s
        self.desc = "Cascade"

    # Return amplitude response value
    def getAmpResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_arrays = [r.getAmpResp()[1] for r in self.filters]
        AR_x = [x for x in freqrange]

        AR_total = [1] * len(AR_x)

        for i in range(0, len(AR_arrays)):
            AR_total = list(np.multiply(AR_total, AR_arrays[i]))

        return AR_x, AR_total

    # Return phase response value
    def getPhaseResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        PR_arrays = np.array([r.getPhaseResp(freqstep, maxfreq)[1] for r in self.filters])
        PR_x = [x for x in freqrange]

        PR_total = list(PR_arrays.sum(0))

        return PR_x, PR_total

    # Cascade filter bank

    def generateOutput(self, input=(), infreq=120, timeperiod=1):
        if input:
            input_x, input_y = input
        else:
            sampleperiod = timeperiod * self.samplfreq
            impulse_period = ceil(self.samplfreq/infreq)

            sample = list()
            pulses = list()

            timepoint = 0
            next_impulse = 0

            while timepoint < sampleperiod:
                sample.append(timepoint)
                if timepoint == next_impulse:
                    pulses.append(1)
                    next_impulse = next_impulse + impulse_period
                else:
                    pulses.append(0)

                timepoint += 1

            input_x = sample
            input_y = pulses

        passed_signal = input_x, input_y

        for r in self.filters:
            passed_signal = r.generateOutput(passed_signal, infreq, timeperiod)

        output_x, output_y = passed_signal

        return output_x, output_y


"""
Parallel filter bank

A formant synthesiser using discrete-time
formant resonators connected in parallel.
"""


class Parallel:
    def __init__(self, *filter_objs, F_s=10000):
        self.filters_cascade = filter_objs
        self.filters = filter_objs[:3]
        self.samplfreq = F_s
        self.desc = "Parallel"

        """Connect each resonator to its shaping filter(S) in cascade"""
        shap_res = list()

        for r in self.filters:
            if self.filters.index(r) == 0:
                pre = PreEmphasis(r.samplfreq, 640)
                pre_allpass = PreEmphasis(r.samplfreq, 270)
                low_allpass = LowPass(r.samplfreq, 270)
                shap_res.append(Cascade(pre, pre_allpass, low_allpass, r))

            else:
                diff = Differentiator(r.samplfreq)
                shap_res.append(Cascade(diff, r))

        self.shapedresonators = shap_res

        """Calculate alternating polarity factors"""
        res_polarity = list()

        for r in self.filters:
            if (self.filters.index(r)+1) % 2:
                res_polarity.append(1)
            else:
                res_polarity.append(-1)

        self.res_polarity = res_polarity

        """Calculate gain factors"""
        cas_x, cas_y = Cascade(*self.filters_cascade).getAmpResp()
        cascade_amp = dict(zip(cas_x, cas_y))

        gain_factors = list()

        for i in range(len(self.filters)):
            unshaped = self.filters[i]
            shaped = self.shapedresonators[i]
            res_x, res_y = shaped.getAmpResp()
            res_amps = dict(zip(res_x, res_y))

            gain = cascade_amp[unshaped.formfreq]/res_amps[unshaped.formfreq]
            gain_factors.append(gain)

        self.gain_factors = gain_factors

        # Return amplitude response value
    def getAmpResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_arrays = [self.gain_factors[self.shapedresonators.index(r)] * np.array(r.getAmpResp()[1]) for r in self.shapedresonators]
        PR_arrays = [np.array(r.getPhaseResp()[1]) for r in self.shapedresonators]

        AR_x = [x for x in freqrange]

        amp_cos_phase = np.array([0 for x in freqrange])
        amp_sin_phase = np.array([0 for x in freqrange])

        for i in range(len(self.shapedresonators)):
            amp_r = np.array(AR_arrays[i])
            phase_r = np.array(PR_arrays[i])

            amp_cos_phase = np.add(amp_cos_phase, amp_r * np.cos(phase_r) * self.res_polarity[i])
            amp_sin_phase = np.add(amp_sin_phase, amp_r * np.sin(phase_r) * self.res_polarity[i])

        AR_total = np.sqrt(np.add(np.square(amp_cos_phase), np.square(amp_sin_phase)))

        return AR_x, AR_total

        # Return phase response value
    def getPhaseResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_arrays = [self.gain_factors[self.shapedresonators.index(r)] * np.array(r.getAmpResp()[1]) for r in self.shapedresonators]
        PR_arrays = [r.getPhaseResp()[1] for r in self.shapedresonators]

        PR_x = [x for x in freqrange]

        amp_cos_phase = np.array([0 for x in freqrange])
        amp_sin_phase = np.array([0 for x in freqrange])

        for i in range(0, len(self.shapedresonators)):
            amp_r = np.array(AR_arrays[i])
            phase_r = np.array(PR_arrays[i])

            amp_cos_phase = np.add(amp_cos_phase, amp_r * np.cos(phase_r) * self.res_polarity[i])
            amp_sin_phase = np.add(amp_sin_phase, amp_r * np.sin(phase_r) * self.res_polarity[i])

        PR_total = np.unwrap(np.arctan2(amp_sin_phase, amp_cos_phase))

        return PR_x, PR_total

    def generateOutput(self, input=(), infreq=120, timeperiod=1):
        if input:
            input_x, input_y = input
        else:
            sampleperiod = timeperiod * self.samplfreq
            impulse_period = ceil(self.samplfreq/infreq)

            sample = list()
            pulses = list()

            timepoint = 0
            next_impulse = 0

            while timepoint < sampleperiod:
                sample.append(timepoint)
                if timepoint == next_impulse:
                    pulses.append(1)
                    next_impulse = next_impulse + impulse_period
                else:
                    pulses.append(0)

                timepoint += 1

            input_x = sample
            input_y = pulses

        passed_signal = input_x, input_y

        for r in self.shapedresonators:
            passed_x, passed_y = r.generateOutput(passed_signal, infreq, timeperiod)
            passed_y = list(np.multiply(self.res_polarity[self.shapedresonators.index(r)], passed_y))
            passed_y = list(np.multiply(self.gain_factors[self.shapedresonators.index(r)], passed_y))
            passed_signal = passed_x, passed_y

        output_x, output_y = passed_signal

        return output_x, output_y
