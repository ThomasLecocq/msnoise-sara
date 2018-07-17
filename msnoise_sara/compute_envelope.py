import time

try:
    from scikits.samplerate import resample
except:
    pass

from obspy.signal.filter import envelope
import bottleneck as bn

from msnoise.preprocessing import preprocess
from msnoise.api import *


class Params():
    pass


def main():

    db = connect()
    # Obtaining the default MSNoise Parameters:
    params = get_params(db)
    
    # Then customizing/overriding with Sara Parameters:
    params.goal_duration = float(get_config(db, "analysis_duration",
                                          plugin="Sara"))
    params.resampling_method = get_config(db, "resampling_method",
                                          plugin="Sara")
    params.decimation_factor = int(get_config(db, "decimation_factor",
                                          plugin="Sara"))

    params.goal_sampling_rate = float(get_config(db, "preprocess_sampling_rate",
                                          plugin="Sara"))
    params.preprocess_lowpass = float(get_config(db, "preprocess_lowpass",
                                          plugin="Sara"))
    params.preprocess_highpass = float(get_config(db, "preprocess_highpass",
                                          plugin="Sara"))
    params.preprocess_taper_length = float(get_config(db, "preprocess_taper_length",
                                          plugin="Sara"))

    params.env_sampling_rate = int(1./float(get_config(db, "env_sampling_rate",
                                          plugin="Sara")))

    params.components_to_compute = get_components_to_compute(db, plugin="Sara")

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('*** Starting: Compute SARA_ENV ***')

    while is_next_job(db, jobtype='SARA_ENV'):
        jobs = get_next_job(db, jobtype='SARA_ENV')
        stations = []
        pairs = []
        refs = []
        if not len(jobs):
            continue

        for job in jobs:
            refs.append(job.ref)
            pairs.append(job.pair)
            netsta1, netsta2 = job.pair.split(':')
            stations.append(netsta1)
            stations.append(netsta2)
            goal_day = job.day

        stations = np.unique(stations)
        t0 = time.time()

        logging.info("New SARA Job: %s (%i pairs with %i stations)" %
                     (goal_day, len(pairs), len(stations)))

        comps = []
        for comp in params.components_to_compute:
            if comp[0] in ["R", "T"] or comp[1] in ["R", "T"]:
                comps.append("E")
                comps.append("N")
            else:
                comps.append(comp[0])
                comps.append(comp[1])
        comps = np.unique(comps)
        stream = preprocess(db, stations, comps, goal_day, params)
        for tr in stream:
            tr.stats.location = "00"
        uniqueids = np.unique([tr.id for tr in stream])
        for uid in uniqueids:
            tmp = stream.select(id=uid).copy()
            # SARA
            logging.debug("Processing %s" % uid)
            ### ENVELOPE
            for trace in tmp:
                if len(trace.data) % 2 != 0:
                    logging.debug("%s Trace not even, removing last sample" %
                                  trace.id)
                    trace.data = trace.data[:-1]
                n = int(params.env_sampling_rate)
                sps = int(trace.stats.sampling_rate)
                if len(trace.data) % (sps * n) != 0:
                    logging.debug("%s Cutting trace to n*sps" % trace.id)
                    div = trace.stats.npts // (sps*n)
                    trace.data = trace.data[:int(div*sps*n)]
                if not len(trace.data):
                    continue
                trace.data = envelope(trace.data)
                trace.data = bn.move_median(trace.data, sps*n)
                trace.data = trace.data[n*sps-1::sps*n]
                trace.stats.sampling_rate = 1./float(n)
                trace.data = np.require(trace.data, np.float32)
            env_output_dir = os.path.join('SARA', 'ENV',
                                          "%s.%s" % (trace.stats.network,
                                                     trace.stats.station))
            if not os.path.isdir(env_output_dir):
                os.makedirs(env_output_dir)
            tmp.write(os.path.join(env_output_dir, goal_day+'.MSEED'),
                        format="MSEED", encoding="FLOAT32")
            del trace, tmp
        del stream
        logging.info("Done. It took %.2f seconds" % (time.time() - t0))

        # THIS SHOULD BE IN THE API
        massive_update_job(db, jobs, flag="D")
        for job in jobs:
            update_job(db, job.day, job.pair, 'SARA_RATIO', 'T')
