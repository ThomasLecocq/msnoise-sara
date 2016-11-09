import time

from scikits.samplerate import resample
from obspy.core import utcdatetime
from obspy.signal import envelope
import bottleneck as bn
from msnoise.api import *


class Params():
    pass


def main():

    db = connect()

    goal_duration = float(get_config(db, "analysis_duration",
                                          plugin="Sara"))
    resampling_method = get_config(db, "resampling_method",
                                          plugin="Sara")
    decimation_factor = int(get_config(db, "decimation_factor",
                                          plugin="Sara"))

    goal_sampling_rate = float(get_config(db, "preprocess_sampling_rate",
                                          plugin="Sara"))
    preprocess_lowpass = float(get_config(db, "preprocess_lowpass",
                                          plugin="Sara"))
    preprocess_highpass = float(get_config(db, "preprocess_highpass",
                                          plugin="Sara"))
    preprocess_taper_length = float(get_config(db, "preprocess_taper_length",
                                          plugin="Sara"))

    env_sampling_rate = int(1./float(get_config(db, "env_sampling_rate",
                                          plugin="Sara")))

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('*** Starting: Compute SARA_ENV ***')

    while is_next_job(db, jobtype='SARA_ENV'):
        jobs = get_next_job(db, jobtype='SARA_ENV')
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

        datafilesZ = {}
        datafilesE = {}
        datafilesN = {}

        for station in stations:
            datafilesZ[station] = []
            datafilesE[station] = []
            datafilesN[station] = []
            net, sta = station.split('.')
            gd = datetime.datetime.strptime(goal_day, '%Y-%m-%d')
            files = get_data_availability(
                db, net=net, sta=sta, starttime=gd, endtime=gd)
            for file in files:
                comp = file.comp
                fullpath = os.path.join(file.path, file.file)
                if comp[-1] == 'Z':
                    datafilesZ[station].append(fullpath)
                elif comp[-1] == 'E':
                    datafilesE[station].append(fullpath)
                elif comp[-1] == 'N':
                    datafilesN[station].append(fullpath)

        comps = ['Z']

        j = 0
        for istation, station in enumerate(stations):
            logging.info('Processing %s' % station)
            for comp in comps:
                files = eval("datafiles%s['%s']" % (comp, station))
                t0 = time.time()
                if len(files) == 0:
                    # Should not happen, but skipping if no file is found
                    continue

                logging.debug("%s.%s Reading %i Files" %
                              (station, comp, len(files)))
                stream = Stream()
                for file in sorted(files):
                    st = read(file, format="MSEED")
                    stream += st
                    del st
                stream.merge()
                stream = stream.split()
                for trace in stream:
                    data = trace.data
                    if len(data) > 2:
                        trace.detrend("demean")
                        trace.taper(max_percentage=None, max_length = preprocess_taper_length)
                    else:
                        trace.data *= 0
                    del data
                logging.debug("%s.%s Merging Stream" % (station, comp))

                stream.merge(fill_value=0)
                logging.debug("%s.%s Slicing Stream to %s:%s" % (station, comp, utcdatetime.UTCDateTime(
                    goal_day.replace('-', '')), utcdatetime.UTCDateTime(goal_day.replace('-', '')) + goal_duration - stream[0].stats.delta))

                stream[0].trim(utcdatetime.UTCDateTime(goal_day.replace('-', '')), utcdatetime.UTCDateTime(
                    goal_day.replace('-', '')) + goal_duration - stream[0].stats.delta, pad=True, fill_value=0.0,nearest_sample=False)
                trace = stream[0]

                logging.debug(
                    "%s.%s Lowpass at %.2f Hz" % (station, comp, preprocess_lowpass))
                trace.filter("lowpass", freq=preprocess_lowpass, zerophase=True)

                logging.debug(
                    "%s.%s Highpass at %.2f Hz" % (station, comp, preprocess_highpass))
                trace.filter("highpass", freq=preprocess_highpass, zerophase=True)

                samplerate = trace.stats['sampling_rate']
                if samplerate != goal_sampling_rate:
                    if resampling_method == "Resample":
                        logging.debug("%s.%s Downsample to %.1f Hz" %
                                      (station, comp, goal_sampling_rate))
                        trace.data = resample(
                            trace.data, goal_sampling_rate / trace.stats.sampling_rate, 'sinc_fastest')
                    elif resampling_method == "Decimate":
                        logging.debug("%s.%s Decimate by a factor of %i" %
                                      (station, comp, decimation_factor))
                        trace.data = trace.data[::decimation_factor]
                    trace.stats['sampling_rate'] = goal_sampling_rate

                if len(trace.data) % 2 != 0:
                    trace.data = np.append(trace.data, 0.)

                # SARA
                logging.debug("Processing")
                ### ENVELOPE
                trace.data = envelope(trace.data)
                n = env_sampling_rate
                sps = trace.stats.sampling_rate
                trace.data = bn.move_median(trace.data,
                                            window=sps*n)
                trace.data = trace.data[n*sps-1::sps*n]
                trace.stats.sampling_rate = 1./float(n)
                trace.data = np.require(trace.data, np.float32)
                env_output_dir = os.path.join('SARA','ENV', station)
                if not os.path.isdir(env_output_dir):
                    os.makedirs(env_output_dir)
                trace.write(os.path.join(env_output_dir, goal_day+'.MSEED'),
                            format="MSEED", encoding="FLOAT32")
                logging.info("Done. It took %.2f seconds" % (time.time()-t0))
                del trace, stream

        for job in jobs:
            update_job(db, job.day, job.pair, 'SARA_ENV', 'D')
            update_job(db, job.day, job.pair, 'SARA_RATIO', 'T')