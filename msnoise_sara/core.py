import click
import sys

from msnoise.api import *

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
        print p

@click.command()
def install():
    from .install import main
    main()

@click.command()
def step1():
    from .compute_envelope import main
    main()


sara.add_command(test)
sara.add_command(step1)