from graphene import ObjectType, String, Int, List, Field

class EmployeeObject(ObjectType):
    id = Int()
    name = String()
    email = String()
    department_id = Int()
    department = Field(lambda: DepartmentObject)

    @staticmethod
    def resolve_departments(root, info):
        return root.departments

class DepartmentObject(ObjectType):
    id = Int()
    name = String()
    location = String()
    employees = List(EmployeeObject)

    @staticmethod
    def resolve_employees(root, info):
        return root.employees
