import numpy as np


class TrendDetection:
    def __init__(self):
        self.messages = {
            'negative': {
                'sentence': "it's getting bad after the ",
                'prefix': " but I'm sorry ",
                'dir': 'Almost every episode is worse than the previous one.'
            },
            'positive': {
                'sentence': "it's getting good after the ",
                'prefix': " but don't worry ",
                'dir': 'Almost every episode is better than the previous one.'
            },
            'stable': {
                'sentence': 'same rating in almost every episode.'
            }
        }

    @staticmethod
    def find_breakpoints(data):
        """
        Find change points

        :param list data: episode ratings
        :return: change points or stable
        :rtype: list or str
        """
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

            # ld: last difference
            ld = abs(data[i] - data[i - 1])
            differences.append(ld)

            if i < 5 or i > len(data) - 5:
                continue

            # please see trend notebook for more information
            # about conditions
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

    def assign_cluster(self, data, info):
        """
        Find cluster of series

        :param list data: episode ratings
        :param list info: episodes
        :return: cluster and specific message of cluster
        :rtype: tuple
        """
        breakpoints = self.find_breakpoints(data)
        count = len(data)

        # linear increase or linear decrease or stable
        if isinstance(breakpoints, str):
            return breakpoints, self.messages[breakpoints]['dir']

        d = {
            'negative': 0,
            'positive': 0
        }
        last_index = 0
        message = ''

        # number of episodes in positive trend
        # number of episodes in negative trend
        # create message by change points
        for i, j in enumerate(breakpoints):
            index, status = j
            not_status = 'positive' if status == 'negative' else 'negative'
            ex = self.messages[status]['sentence'] + info[index]

            if i == 0:
                last_index = index
            elif i > 0:
                ex = self.messages[status]['prefix'] + \
                     self.messages[status]['sentence'] + \
                     info[index]

            d[not_status] += index - last_index
            if i == len(breakpoints) - 1:
                d[status] += count - index

            last_index = index
            message += ex

        if d['positive'] / count > .5:
            last_status = 'generally_positive'
        elif d['negative'] / count > .5:
            last_status = 'generally_negative'
        else:
            last_status = 'generally_stable'

        return last_status, message + '.'
