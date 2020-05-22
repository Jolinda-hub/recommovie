import numpy as np


class TrendDetection:
    def __init__(self):
        pass

    def find_breakpoints(self, data):
        differences = []
        breakpoints = []
        trends = []
        trend = None

        if len(np.unique(data)) == 1:
            return breakpoints

        for i, episode in enumerate(data):
            if i == 0 or i + 1 == len(data):
                continue

            # ma: moving average
            ma = np.mean(data[:i])

            # nma: ma of next episodes
            nma = np.mean(data[i + 1:])

            # dma: ma of differences
            dma = np.mean(differences) if len(differences) > 0 else 0

            ld = abs(data[i] - data[i - 1])
            differences.append(ld)

            if i < 5 or i > len(data) - 5:
                continue

            cond1 = data[i] > ma + dma
            cond2 = nma > ma + 3 * dma
            cond3 = data[i] < ma - dma
            cond4 = nma < ma - 3 * dma
            cond5 = ld > dma
            cond6 = trend != 'positive'
            cond7 = trend != 'negative'

            if cond1 and cond5:
                trends.append('positive')
            elif cond3 and cond5:
                trends.append('negative')

            if cond1 and cond2 and cond6:
                trend = 'positive'
            elif cond3 and cond4 and cond7:
                trend = 'negative'
            else:
                continue

            breakpoints.append((i - 1, trend))

        if len(np.unique(trends)) == 1:
            return np.unique(trends)[0]

        return breakpoints if len(breakpoints) > 0 else 'stable'

    def assign_cluster(self, data):
        trend = self.find_breakpoints(data)
        count = len(data)

        if isinstance(trend, str):
            return trend

        d = {
            'negative': 0,
            'positive': 0
        }
        last_index = 0

        for i, j in enumerate(trend):
            index, status = j
            not_status = 'positive' if status == 'negative' else 'negative'

            if i == 0:
                last_index = index

            d[not_status] += index - last_index
            if i == len(trend) - 1:
                d[status] += count - index

            last_index = index

        if d['positive'] / count > .5:
            return 'generally_positive'
        elif d['negative'] / count > .5:
            return 'generally_negative'

        return 'generally_stable'
