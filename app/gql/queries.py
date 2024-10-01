from graphene import ObjectType, List
from app.db.models import Employee, Department
from app.gql.types import EmployeeObject, DepartmentObject
from app.db.database import Session
from sqlalchemy.orm import joinedload

class Query(ObjectType):
    employees = List(EmployeeObject)
    departments = List(DepartmentObject)

    @staticmethod
    def resolve_employees(root, info):
        # return Session().query(Employee).all()
        return Session().query(Employee).options(joinedload(Employee.department)).all()

    @staticmethod
    def resolve_departments(root, info):
        return Session().query(Department).all()