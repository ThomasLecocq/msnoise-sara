import sys

import click
from flask_admin.contrib.sqla import ModelView

from .sara_table_def import SaraConfig, SaraStation


### COMMAND LINE INTERFACE PLUGIN DEFINITION

@click.group()
def sara():
    """Seismic amplitude ratio analysis (SARA) has been used successfully to
    track the sub-surface migration of magma prior to an eruption at Piton de
    la Fournaise volcano, La Reunion. The methodology is based on the temporal
    analysis of the seismic amplitude ratio between different pairs of stations
    , along with a model of seismic wave attenuation. This method has already
    highlighted the complexity of magma migration in the shallower part of the
    volcanic edifice during a seismic crisis using continuous records. We will
    see that this method can also be applied to the localization of individual
    earthquakes triggered by monitoring systems, prior to human intervention
    such as phase picking."""
    pass

@click.command()
def test():
    for p in sys.path:
        print(p)

@click.command()
def install():
    from .install import main
    main()


@click.command()
def envelope():
    from .compute_envelope import main
    main()


@click.command()
def ratio():
    from .compute_ratio import main
    main()

@click.group()
def plot():
    pass

@click.command()
@click.argument('sta1')
@click.argument('sta2')
@click.option('-f', '--filterid', default=1, help='Filter ID')
@click.option('-c', '--comp', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-S', '--smooth', default=1, help='Smooth over N points')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def result(sta1, sta2, filterid, comp, smooth, show, outfile):
    """Plots the interferogram between sta1 and sta2 (parses the CCFs)\n
    STA1 and STA2 must be provided with this format: NET.STA !"""
    from .plot_ratios import main
    main(sta1, sta2, filterid, comp, smooth, show, outfile)



sara.add_command(test)
sara.add_command(install)
sara.add_command(envelope)
sara.add_command(ratio)

sara.add_command(plot)
plot.add_command(result)

### WEB INTERFACE PLUGIN DEFINITION
class SaraConfigView(ModelView):
    # Disable model creation
    view_title = "MSNoise SARA Configuration"
    name = "Configuration"

    #inline_models = (SaraConfig,)
    can_create = False
    can_delete = False
    page_size = 50
    # Override displayed fields
    column_list = ('name', 'value')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(SaraConfigView, self).__init__(SaraConfig, session,
                                             endpoint="saraconfig",
                                             name="Config",
                                             category="SARA", **kwargs)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


class SaraStationView(ModelView):
    # Disable model creation
    view_title = "MSNoise SARA Station Configuration"
    name = "Station Config"

    #inline_models = (SaraConfig,)
    can_create = False
    can_delete = False
    page_size = 50
    # Override displayed fields
    column_list = ('net', 'sta', 'sensitivity', 'site_effect')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(SaraStationView, self).__init__(SaraStation, session,
                                             endpoint="sarastation",
                                             name="Station Config",
                                             category="SARA", **kwargs)


# class SaraResultPlotter(BaseView):
#     name = "MSNoise"
#     view_title = "Result Plotter"
#     category = "SARA"
#     def __init__(self, session, **kwargs):
#         # You can pass name and other parameters if you want to
#         super(SaraResultPlotter, self).__init__(name="Results",
#                                                 category="SARA",
#                                              endpoint="sararesults",
#                                              **kwargs)
#
#     @expose('/')
#     def index(self):
#         args = flask.request.args
#         filters = []
#         pairs = select_pair()
#
#         # Get all the form arguments in the url with defaults
#         filter = int(getitem(args, 'filter', 1))
#         pair = int(getitem(args, 'pair', 0))
#         component = getitem(args, 'component', 'ZZ')
#         format = getitem(args, 'format', 'stack')
#
#         db = connect()
#         station1, station2 = pairs[pair]['text'].replace('.','_').split(' - ')
#
#         x = []
#         y = []
#
#         try:
#             data = read(os.path.join('SARA','RATIO', pairs[pair]['text'].replace("-","_").replace(' ',''),"*"))
#             data.merge(fill_value=1)
#             x = np.arange(data[0].stats.npts)
#             y = data[0].data
#         except:
#             traceback.print_exc()
#             pass
#
#         fig = figure(title=pairs[pair]['text'], plot_width=1000)
#         fig.line(x, y, line_width=2)
#
#         plot_resources = RESOURCES.render(
#             js_raw=CDN.js_raw,
#             css_raw=CDN.css_raw,
#             js_files=CDN.js_files,
#             css_files=CDN.css_files,
#         )
#
#         script, div = components(fig, INLINE)
#         return self.render(
#             'admin/results.html',
#             plot_script=script, plot_div=div, plot_resources=plot_resources,
#             filter_list=filters,
#             pair_list=pairs
#         )


# Job definitions

def register_job_types():
    jobtypes = []
    jobtypes.append( {"name":"SARA_ENV", "after":"scan_archive"} )
    return jobtypes
