from math import exp, pi, cos, sin, sqrt, atan2, fabs, ceil

# Parameters: Formant frequency, formant bandwidth, sampling frequency


class Resonator:
    def __init__(self, F_n, B_n, F_s):
        self.formfreq = F_n
        self.bandw = B_n
        self.samplfreq = F_s
        self.samplperiod = 1/self.samplfreq

        self.desc = "Resonator"
        self.B_co = 2 * exp(-(pi * self.bandw * self.samplperiod)) * cos(2 * pi * self.formfreq * self.samplperiod)
        self.C_co = -(exp(-2 * pi * self.bandw * self.samplperiod))
        self.A_co = 1 - self.B_co - self.C_co

    def getAmpResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_x = [x for x in freqrange]
        AR_y = [fabs(self.A_co) / sqrt(((1 - self.C_co) * cos(2 * pi * freq * self.samplperiod) - self.B_co) ** 2 + ((1 + self.C_co) * sin(2 * pi * freq * self.samplperiod)) ** 2) for freq in freqrange]

        return AR_x, AR_y

    def getPhaseResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        PR_x = [x for x in freqrange]
        PR_y = [-atan2((1 + self.C_co) * sin(2 * pi * freq * self.samplperiod), (1 - self.C_co) * cos(2 * pi * freq * self.samplperiod) - self.B_co) for freq in freqrange]

        return PR_x, PR_y

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

        output_y = []

        for n in range(len(input_x)):
            try:
                in_minus_1 = input_y[n - 1]
            except IndexError:
                in_minus_1 = 0
            try:
                out_minus_1 = output_y[n - 1]
            except IndexError:
                out_minus_1 = 0
            try:
                out_minus_2 = output_y[n - 2]
            except IndexError:
                out_minus_2 = 0

            output_y.append((self.A_co * in_minus_1) + (self.B_co * out_minus_1) + (self.C_co * out_minus_2))

            output_x = input_x

        return output_x, output_y


class PreEmphasis:
    def __init__(self, F_s, F_c):
        self.samplfreq = F_s
        self.samplperiod = 1/self.samplfreq
        self.cutoff = F_c

        self.desc = "Preemphasis"
        self.B_co = exp(-(2 * pi * self.cutoff * self.samplperiod))
        self.A_co = 1 - self.B_co

    def getAmpResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_x = [x for x in freqrange]
        AR_y = [sqrt(1 + (self.B_co ** 2) - (2 * self.B_co * cos(2 * pi * freq * self.samplperiod))) / fabs(self.A_co) for freq in freqrange]

        return AR_x, AR_y

    def getPhaseResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        PR_x = [x for x in freqrange]
        PR_y = [atan2(self.B_co * sin(2 * pi * freq * self.samplperiod), 1 - self.B_co * cos(2 * pi * freq * self.samplperiod)) for freq in freqrange]

        return PR_x, PR_y

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

        output_y = []

        for n in range(len(input_x)):
            try:
                in_minus_1 = input_y[n - 1]
            except IndexError:
                in_minus_1 = 0

            output_y.append((1 / self.A_co) * (input_y[n] - (self.B_co * in_minus_1)))

            output_x = input_x

        return output_x, output_y


class Differentiator:
    def __init__(self, F_s):
        self.samplfreq = F_s
        self.samplperiod = 1/self.samplfreq

        self.desc = "Differentiator"

    def getAmpResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_x = [x for x in freqrange]
        AR_y = [sqrt(2 * (1 - cos(2 * pi * freq * self.samplperiod))) / self.samplperiod for freq in freqrange]

        return AR_x, AR_y

    def getPhaseResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        PR_x = [x for x in freqrange]
        PR_y = [atan2(sin(2 * pi * freq * self.samplperiod), 1 - cos(2 * pi * freq * self.samplperiod)) for freq in freqrange]

        return PR_x, PR_y

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

        output_y = []

        for n in range(len(input_x)):
            try:
                in_minus_1 = input_y[n - 1]
            except IndexError:
                in_minus_1 = 0

            output_y.append(1/self.samplperiod * (input_y[n] - in_minus_1))

        output_x = input_x

        return output_x, output_y


class LowPass:
    def __init__(self, F_s, F_c):
        self.cutoff = F_c
        self.samplfreq = F_s
        self.samplperiod = 1/self.samplfreq

        self.desc = "Low pass filter"
        self.B_co = exp(-(2 * pi * self.cutoff * self.samplperiod))
        self.A_co = 1 - self.B_co

    def getAmpResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        AR_x = [x for x in freqrange]
        AR_y = [fabs(self.A_co) / sqrt(1 + (self.B_co ** 2) - (2 * self.B_co * cos(2 * pi * freq * self.samplperiod))) for freq in freqrange]

        return AR_x, AR_y

    def getPhaseResp(self, freqstep=10, maxfreq=10000):
        freqrange = range(0, maxfreq, freqstep)

        PR_x = [x for x in freqrange]
        PR_y = [-atan2(self.B_co * sin(2 * pi * freq * self.samplperiod), 1 - (self.B_co * cos(2 * pi * freq * self.samplperiod))) for freq in freqrange]

        return PR_x, PR_y

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

        output_y = []

        for n in range(len(input_x)):
            try:
                out_minus_1 = output_y[n - 1]
            except IndexError:
                out_minus_1 = 0

            output_y.append((self.A_co * input_y[n]) + (self.B_co * out_minus_1))

        output_x = input_x

        return output_x, output_y
