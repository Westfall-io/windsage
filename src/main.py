# Copyright (c) 2023-2024 Westfall Inc.
#
# This file is part of Windsage.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, and can be found in the file NOTICE inside this
# git repository.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from env import *

import time
start_time = time.time()

from datetime import datetime

import requests
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
    default_branch: Mapped[str] = mapped_column(db.String(255))

class Artifacts_Commits(Base):
    __tablename__ = "artifact_commits"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    artifacts_id: Mapped[int] = mapped_column(db.ForeignKey("artifacts.id"))
    ref: Mapped[str] = mapped_column(db.String(255))
    commit: Mapped[str] = mapped_column(db.String(255))
    date: Mapped[datetime] = mapped_column(default=None)

def connect():
    db_type = "postgresql"
    user = DBUSER
    passwd = DBPASS
    address = SQLHOST
    db_name = DBTABLE

    address = db_type+"://"+user+":"+passwd+"@"+address+"/"+db_name
    engine = db.create_engine(address)
    conn = engine.connect()

    return conn, engine

def main(ref, commit, full_name, commit_url, default_branch):
    print('Parsing inputs')
    ref = ref.split('/')[-1]

    if ref != default_branch:
        print('Skipping non-default branch.')
        return

    print('Pushing to database')
    c, engine = connect()
    with Session(engine) as session:
        # Find all artifacts with this full name
        # Ex: "full_name": "Westfall/sysml_workflow"
        result = session \
            .query(Artifacts) \
            .filter(
                Artifacts.full_name == full_name
            ) \
            .first()

        if result is None:
            # This artifact repo has never been seen, add it to the db.
            this_a = Artifacts(
                full_name = full_name,
                commit_url = commit_url,
                default_branch = default_branch
            )
            session.add(this_a)
            session.commit()

            # Grab the result again after it was commited, so that in either
            # case, result.id is the artifact id.
            session.refresh(this_a)
            artifact_id = this_a.id
        else:
            # Grab the id
            artifact_id = result.id

            # See if we need to update the default branch
            if result.default_branch != ref:
                result = session \
                    .query(Artifacts) \
                    .filter(
                        Artifacts.id == artifact_id
                    ) \
                    .update({'default_branch': default_branch})
                session.commit()

        result = session \
            .query(Artifacts_Commits) \
            .filter(
                Artifacts_Commits.ref == ref,
                Artifacts_Commits.commit == str(commit)
            ) \
            .first()

        if result is None:
            # Create a new commit to refresh the head.
            this_ac = Artifacts_Commits(
                artifacts_id=artifact_id,
                ref=ref,
                commit=str(commit),
                date=datetime.now()
            )
            session.add(this_ac)
            session.commit()

    print('Closing session.')
    c.close()
    engine.dispose()

    try:
        requests.post(WINDSTORMHOST, json = {
            'source' : 'sage',
            'payload' : {
                'artifact_id': artifact_id
            }
        })
    except:
        print('Could not connect to windstorm webhook endpoint.')

if __name__ == '__main__':
    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
