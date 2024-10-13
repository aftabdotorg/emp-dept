from importlib.metadata import requires

from graphene import Mutation, String, Int, Field, ObjectType, Boolean
from app.db.models import Employee, Department
from app.gql.types import EmployeeObject, DepartmentObject
from app.db.database import Session
from sqlalchemy.orm import joinedload

# model to object conversion


class AddEmployee(Mutation):
    class Arguments:
        name = String(required=True)
        email = String(required=True)
        department_id = Int(required=True)

    employee = Field(lambda: EmployeeObject)

    @staticmethod
    def mutate(root, info, name, email, department_id):
        employee = Employee(name=name, email=email, department_id=department_id)
        session = Session()
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return AddEmployee(employee=employee)

class UpdateEmployee(Mutation):
    class Arguments:
        employee_id = Int(required=True)
        name = String(required=True)
        email = String(required=True)
        department_id = Int(required=True)

    employee = Field(lambda: EmployeeObject)

    @staticmethod
    def mutate(root, info, employee_id, name=None, email=None, department_id=None):
        session = Session()

        employee = session.query(Employee).options(joinedload(Employee.department)).filter(Employee.id == employee_id).first()

        if not employee:
            raise Exception("Employee not found")

        if name is not None:
            employee.name = name
        if email is not None:
            employee.email = email
        if department_id is not None:
            employee.department_id = department_id

        session.commit()
        session.refresh(employee)
        session.close()
        return UpdateEmployee(employee=employee)

class DeleteEmployee(Mutation):
    class Arguments:
        id = Int(required=True)

    success = Boolean()

    @staticmethod
    def mutate(root, info, id):
        session = Session()
        employee = session.query(Employee).filter(Employee.id == id).first()

        if not employee:
            raise Exception("Employee not found")

        session.delete(employee)
        session.commit()
        session.close()
        return DeleteEmployee(success=True)


class AddDepartment(Mutation):
    class Arguments:
        name = String(required=True)
        location = String(required=True)

    department = Field(lambda: DepartmentObject)

    @staticmethod
    def mutate(root, info, name, location):
        session = Session()
        department = Department(name=name, location=location)
        session.add(department)
        session.commit()
        session.refresh(department)
        return AddDepartment(department=department)

class Mutation(ObjectType):
    add_employee = AddEmployee.Field()
    update_employee = UpdateEmployee.Field()
    delete_employee = DeleteEmployee.Field()
