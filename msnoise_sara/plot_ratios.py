import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from msnoise.api import connect, get_station_pairs
from obspy.core import read


def main(smooth, show, outfile):
    db = connect()
    fig = plt.figure()
    for sta1, sta2 in get_station_pairs(db):
        sta1 = "%s.%s" % (sta1.net, sta1.sta)
        sta2 = "%s.%s" % (sta2.net, sta2.sta)
        pair = "%s_%s" % (sta1, sta2)
        try:
            st = read(os.path.join('SARA','RATIO', pair, "*"))
        except:
            print("No data for %s" % pair)
            continue
        st.merge(fill_value=np.nan)
        t = pd.date_range(st[0].stats.starttime.datetime,
                          periods=st[0].stats.npts,
                          freq="%ims" % (st[0].stats.delta * 1000))
        s = pd.Series(data=st[0].data, index=t, dtype=st[0].data.dtype)
        s = s.resample('1T').median()
        s.to_csv("%s.csv"%pair)
        if smooth != 1:
            s = s.rolling(window=smooth, min_periods=1, center=True).median()
        plt.plot(s.index, s, lw=1.0, label='%s' % pair)
    plt.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    if outfile:
        plt.savefig(outfile)
    if show:
        plt.show()

