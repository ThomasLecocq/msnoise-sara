import datetime
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

    ccjobs = get_jobs_by_lastmod(session, "CC",
                                 lastmod=datetime.datetime(1970, 1, 1))
    
    for job in ccjobs:
        update_job(session, job.day, job.pair, "SARA_ENV", "T")
    session.commit()
    session.close()
