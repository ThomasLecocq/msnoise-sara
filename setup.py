from setuptools import setup, find_packages

setup(
    name='msnoise_sara',
    version='0.1a',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['msnoise',
                      'bottleneck'],
    entry_points = {
        'msnoise.plugins.commands': [
            'sara = msnoise_sara.plugin_definition:sara',
        ],
        'msnoise.plugins.table_def': [
            'SaraConfig = msnoise_sara.sara_table_def:SaraConfig',
        ],
        'msnoise.plugins.admin_view': [
            'SaraConfigView = msnoise_sara.plugin_definition:SaraConfigView',
            'SaraStationView = msnoise_sara.plugin_definition:SaraStationView',
            # 'SaraResultPlotter = msnoise_sara.plugin_definition:SaraResultPlotter',
        ],
        'msnoise.plugins.jobtypes': [
            'register = msnoise_sara.plugin_definition:register_job_types',
        ],


    },
    author = "Thomas Lecocq & Corentin Caudron",
    author_email = "Thomas.Lecocq@seismology.be",
    description = "The Amplitude Ratio plugin for MSNoise - Bringing SARA (Taisne et al 2011) to MSNoise",
    license = "EUPL-1.1",
    url = "http://www.msnoise.org/plugins/msnoise-sara",
    keywords="noise monitoring seismic microseismicity amplitude ratio location seismology"
)