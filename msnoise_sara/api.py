from .sara_table_def import SaraStation

def get_sara_param(session, station):
    net, sta = station.split('.')
    return session.query(SaraStation).filter(SaraStation.net==net).filter(SaraStation.sta==sta).first()