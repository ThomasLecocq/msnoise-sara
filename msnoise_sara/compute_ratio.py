import time

import bottleneck as bn
from obspy.core import Stream, Trace, read
from msnoise.api import *
from .api import get_sara_param

def main():
    db = connect()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('*** Starting: Compute SARA_RATIO ***')

    while is_next_job(db, jobtype='SARA_RATIO'):
        t0 = time.time()
        jobs = get_next_job(db, jobtype='SARA_RATIO')
        stations = []
        pairs = []
        refs = []

        for job in jobs:
            refs.append(job.ref)
            pairs.append(job.pair)
            netsta1, netsta2 = job.pair.split(':')
            stations.append(netsta1)
            stations.append(netsta2)
            goal_day = job.day

        stations = np.unique(stations)

        logging.info("New SARA Job: %s (%i pairs with %i stations)" %
                     (goal_day, len(pairs), len(stations)))

        logging.debug("Preloading all envelopes and applying site and sensitivity")
        all = {}
        for station in stations:
            tmp = get_sara_param(db, station)
            sensitivity = tmp.sensitivity
            site_effect = tmp.site_effect
            try:
                fn = os.path.join("SARA", "ENV", station, "%s.MSEED"%goal_day)
                tmp = read(fn)
            except:
                logging.debug("Error reading %s:%s"%(station, goal_day))
                import traceback
                traceback.print_exc()
                continue
            for trace in tmp:
                trace.data /= (sensitivity * site_effect)
            all[station] = tmp

        logging.debug("Computing all pairs")
        for job in jobs:
            netsta1, netsta2 = job.pair.split(':')
            logging.debug("processing %s:%s"%(netsta1,netsta2))
            net1,sta1,loc1=netsta1.split(".")
            net2,sta2,loc2=netsta2.split(".")
            trace = Trace()
            if netsta1 not in all or netsta2 not in all:
                update_job(db, job.day, job.pair, 'SARA_RATIO', 'D',
                           ref=job.ref)
                continue
            tmp = Stream()
            for tr in all[netsta1]:
                tmp += tr
            for tr in all[netsta2]:
                tmp += tr
            # tmp = Stream(traces=[all[netsta1], all[netsta2]])
            # print(tmp)
            tmp.merge()
            tmp = make_same_length(tmp)
            tmp.merge(fill_value=np.nan)
            if len(tmp)>1:
                trace.data = tmp.select(network=net1, station=sta1, location=loc1)[0].data / \
                             tmp.select(network=net2, station=sta2, location=loc2)[0].data
                trace.stats.starttime = tmp[0].stats.starttime
                trace.stats.delta = tmp[0].stats.delta

                env_output_dir = os.path.join('SARA','RATIO', job.pair.replace(":","_"))
                if not os.path.isdir(env_output_dir):
                    os.makedirs(env_output_dir)
                trace.write(os.path.join(env_output_dir, goal_day+'.MSEED'),
                            format="MSEED", encoding="FLOAT32")

            update_job(db, job.day, job.pair, 'SARA_RATIO', 'D', ref=job.ref)
            del tmp
        logging.info("Done. It took %.2f seconds" % (time.time()-t0))
