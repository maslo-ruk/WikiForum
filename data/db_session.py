import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None

def global_init(db_name):
    global __factory
    if __factory:
        return

    if not db_name or not db_name.strip():
        raise Exception('Укажите имя базы данных!')

    adress = f'sqlite:///{db_name.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {adress}")

    engine = sa.create_engine(adress, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import _all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()