import time
start_time = time.time()

import os

SQLDEF = "localhost:5432"
SQLHOST = os.environ.get("SQLHOST",SQLDEF)

from datetime import datetime

import sqlalchemy as db
from sqlalchemy.orm import DeclarativeBase, Mapped, \
    mapped_column, MappedAsDataclass, relationship, Session

class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""

class Artifacts(Base):
    __tablename__ = "artifacts"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    commit_url: Mapped[str] = mapped_column(db.String(), nullable=False)
    ref: Mapped[str] = mapped_column(db.String(255))
    commit: Mapped[str] = mapped_column(db.String(255))
    date: Mapped[datetime] = mapped_column(default=None)

def connect():
    db_type = "postgresql"
    user = "postgres"
    passwd = "mysecretpassword"
    address = SQLHOST
    db_name = "sysml2"

    address = db_type+"://"+user+":"+passwd+"@"+address+"/"+db_name
    engine = db.create_engine(address)
    conn = engine.connect()

    return conn, engine

def main(ref, commit, full_name, commit_url):
    print('Parsing inputs')
    ref = ref.split('/')[-1]

    print('Pushing to database')
    c, engine = connect()
    with Session(engine) as session:
        this_a = Artifacts(
            full_name = full_name,
            commit_url = commit_url,
            ref = ref,
            commit = commit,
            date = datetime.now()
        )
        session.add(this_a)
        session.commit()

    print('Closing session.')
    c.close()
    engine.dispose()

    #requests.post(WINDSTORMHOST, json={'ref'=ref, 'commit':commit})

if __name__ == '__main__':
    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
