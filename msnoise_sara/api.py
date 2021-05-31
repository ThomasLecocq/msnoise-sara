from .sara_table_def import SaraStation

def get_sara_param(session, station):
    net, sta, loc = station.split('.')
    return session.query(SaraStation).filter(SaraStation.net==net).filter(SaraStation.sta==sta).first()