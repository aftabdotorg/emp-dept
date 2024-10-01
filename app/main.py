from graphene import Schema
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette_graphene3 import GraphQLApp, make_playground_handler
from app.db.database import prepare_database, Session
from app.gql.queries import Query
from app.db.models import Employee, Department
from app.gql.mutations import Mutation


schema = Schema(query=Query, mutation=Mutation)
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup_event():
    prepare_database()

@app.get("/employees")
def get_employees():
    session = Session()
    employees = session.query(Employee).all()
    session.close()
    return employees

@app.get("/departments")
def get_departments():
    session = Session()
    departments = session.query(Department).all()
    session.close()
    return departments

@app.get("/")
def test_home():
    return {"OK" : 200}


@app.get("/employees-table")
async def employees_table(request: Request):
    query = """
    query {
        employees {
            id
            name
            email
            department {
                name
                location
            }
        }
        departments {
            id
            name
        }
    }
    """
    result = schema.execute(query)
    employees = result.data['employees']
    departments = result.data['departments']
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees, "departments": departments})


@app.post("/init-data")
async def init_data():
    session = Session()

    # Add initial departments
    departments = [
        Department(name="Engineering", location="Building A"),
        Department(name="Human Resources", location="Building B"),
        Department(name="Marketing", location="Building C")
    ]
    session.add_all(departments)
    session.commit()

    # Add initial employees
    employees = [
        Employee(name="John Doe", email="john@example.com", department_id=1),
        Employee(name="Jane Smith", email="jane@example.com", department_id=2),
        Employee(name="Bob Johnson", email="bob@example.com", department_id=3)
    ]
    session.add_all(employees)
    session.commit()

    session.close()
    return {"message": "Initial data added successfully"}


app.mount("/graphql", GraphQLApp(
    schema=schema,
    on_get=make_playground_handler()
    ))


