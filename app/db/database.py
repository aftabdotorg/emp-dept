from sqlalchemy import create_engine
from app.db.models import Base
from app.settings.config import DB_URI
from sqlalchemy.orm import sessionmaker
# from app.db.data import employees_data, departments_data
from app.db.models import Employee, Department

engine = create_engine(DB_URI, echo=True)
Session = sessionmaker(bind=engine)


def prepare_database():
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # session = Session()
    #
    # for employee in employees_data:
    #     emp = Employee(**employee)
    #     session.add(emp)
    #
    # for department in departments_data:
    #     session.add(Department(**department))
    #
    # session.commit()
    # session.close()
