# MSNoise-SARA
The Amplitude Ratio plugin for MSNoise - Bringing SARA (Taisne et al 2011) to MSNoise

CI Builds: [![Github Action Status](https://github.com/ThomasLecocq/msnoise-sara/actions/workflows/test_full.yml/badge.svg)](https://github.com/ThomasLecocq/msnoise-sara/actions)

Seismic amplitude ratio analysis (SARA) has been used successfully to
track the sub-surface migration of magma prior to an eruption at Piton de
la Fournaise volcano, La Reunion. The methodology is based on the temporal
analysis of the seismic amplitude ratio between different pairs of stations,
along with a model of seismic wave attenuation. This method has already
highlighted the complexity of magma migration in the shallower part of the
volcanic edifice during a seismic crisis using continuous records. We will
see that this method can also be applied to the localization of individual
earthquakes triggered by monitoring systems, prior to human intervention
such as phase picking.

## Temporary Documentation

### Installation
* Follow the MSNoise installation instructions ([here](http://msnoise.org/doc/installation.html))
* Install ``bottleneck`` using either conda: ``conda install -c conda-forge bottleneck`` or pip: ``pip install bottleneck``
* Install MSNoise-SARA

### Running MSNoise-SARA
In a new or current MSNoise project, once the station table has been populated and the archive scanned:

* ``msnoise config set plugins=msnoise_sara`` is equivalent to going in the web Admin and setting the ``plugins`` configuration bit. Note the underscore and not a dash.
* ``msnoise p sara install`` will set up the MSNoise-SARA database tables and
  * automatically create the `SARA_ENV` jobs if the database already contains `CC` jobs.
  * if your DB doesn't yet contain `CC` jobs and you only want `SARA_ENV` jobs, simply run ``msnoise new_jobs --nocc``
* ``msnoise p sara envelope`` will compute the envelope of the signal for all available data
* **!!TODO!!** ``msnoise p sara new_jobs`` will determine which new ``SARA_RATIO`` jobs need to be done. **!!TODO!!**
* ``msnoise p sara ratio`` will compute the ratio of the envelopes for each pair of stations (only for common data, of course)
* ``msnoise p sara plot ratios`` will plot the ratios of all station pairs.
 