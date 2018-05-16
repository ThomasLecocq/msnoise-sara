# installer for SARA
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime,\
    text, TIMESTAMP, Enum
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

from msnoise.msnoise_table_def import PrefixerBase

class SaraConfig(PrefixerBase):
    """
    Config Object

    :type name: str
    :param name: The name of the config bit to set.

    :type value: str
    :param value: The value of parameter `name`
    """
    __incomplete_tablename__ = "sara-config"
    name = Column(String(255), primary_key=True)
    value = Column(String(255))

    def __init__(self, name, value):
        """"""
        self.name = name
        self.value = value

class SaraStation(PrefixerBase):
    """
    Station Object

    :type ref: int
    :param ref: The Station ID in the database
    :type net: str
    :param net: The network code of the Station
    :type sta: str
    :param sta: The station code
    :type X: float
    :param X: The X coordinate of the station
    :type Y: float
    :param Y: The Y coordinate of the station
    :type altitude: float
    :param altitude: The altitude of the station
    :type coordinates: str
    :param coordinates: The coordinates system. "DEG" is WGS84 latitude/
        longitude in degrees. "UTM" is expressed in meters.
    :type instrument: str
    :param instrument: The instrument code, useful with PAZ correction
    :type used: bool
    :param used: Whether this station must be used in the computations.
    """
    __incomplete_tablename__ = "sara-stations"
    ref = Column(Integer, primary_key=True)
    net = Column(String(10))
    sta = Column(String(10))
    sensitivity = Column(Float)
    site_effect = Column(Float)

    used = Column(Boolean)

    def __init__(self, net, sta, sensitivity, site_effect ):
        """"""
        self.net = net
        self.sta = sta
        self.sensitivity = sensitivity
        self.site_effect = site_effect


########################################################################
