from graphene import Schema
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette_graphene3 import GraphQLApp, make_playground_handler
from app.db.database import prepare_database, Session
from app.gql.queries import Query
from app.db.models import Employee, Department
from app.gql.mutations import Mutation
from fastapi.responses import StreamingResponse
import csv
from io import StringIO


schema = Schema(query=Query, mutation=Mutation)
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")



@app.get("/download-employees-csv", response_class=StreamingResponse)
async def download_employees_csv():
    # Create a string buffer to store the CSV data
    output = StringIO()

    # Create a CSV writer object
    writer = csv.writer(output)

    # Write header row
    writer.writerow(["ID", "Name", "Email", "Department", "Location"])

    # Fetch employee data
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
    }
    """
    result = schema.execute(query)
    employees = result.data['employees']

    # Write employee data rows
    for employee in employees:
        writer.writerow([
            employee['id'],
            employee['name'],
            employee['email'],
            employee['department']['name'],
            employee['department']['location']
        ])

    # Move the cursor to the start of the stream
    output.seek(0)

    # Return the file as a StreamingResponse with appropriate headers
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )


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
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})



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


