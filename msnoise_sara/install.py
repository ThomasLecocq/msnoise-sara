from msnoise.api import *

from .default import default
from .sara_table_def import SaraConfig, SaraStation

def main():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    SaraConfig.__table__.create(bind=engine, checkfirst=True)
    for name in default.keys():
        session.add(SaraConfig(name=name,value=default[name][-1]))
        try:
            session.commit()
        except:
            session.rollback()

    SaraStation.__table__.create(bind=engine, checkfirst=True)

    db = connect()
    for station in get_stations(db):
        session.add(SaraStation(net=station.net, sta=station.sta,
                                sensitivity=1, site_effect=1 ))

    session.commit()