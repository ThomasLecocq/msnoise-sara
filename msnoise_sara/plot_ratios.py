import os
import numpy as np
import scipy.signal
from obspy.core import read


def main(sta1, sta2, filterid, comp, smooth, show, outfile):
    pair = "%s_%s" % (sta1, sta2)
    data = read(os.path.join('SARA','RATIO', pair, "*"))
    data.merge(fill_value=1)
    if smooth != 1:
        data[0].data = np.convolve(scipy.signal.boxcar(smooth), data[0].data, "same")

    data.plot(method="full")
