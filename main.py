#import uvicorn as uv
from fastapi.middleware.cors import CORSMiddleware #cross origin research sharing (CORS)
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional, Literal, Annotated
from enum import IntEnum 
from datetime import date
from pydantic import BaseModel, Field #for documentation
import psycopg2 as psy
from psycopg2 import sql
from fastapi import Query

db_connect_info = ["postgres","postgres","localhost","1223","5432"]
# Note the index of db_connect_info. From 0 -> 4
# database="postgres"
# user="postgres"
# host="localhost"
# password="1223"
# port=5432
#documentation schema. Most likely will make one for each table

# Employee Table ------------------------------------------------------------------
class EmployeeBase(BaseModel):
    firstname: str = Field(..., min_length=3, max_length=255, description="First name of employee")
    lastname: str = Field(..., min_length=2, max_length=255, description="Last name of employee")


# Create
class EmployeeCreate(EmployeeBase):
  pass

# Update
class EmployeeUpdate(BaseModel):
  firstname: Optional[str] = Field(None, min_length=3, max_length=255)
  lastname: Optional[str] = Field(None, min_length=2, max_length=255)

# Read
class EmployeeRead(EmployeeBase):
  id: int



# Zone Table ------------------------------------------------------------------
class ZoneBase(BaseModel):
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(None, description="Zone Description")

# CREATE
class ZoneCreate(ZoneBase):
   pass

# UPDATE
class ZoneUpdate(BaseModel):
   name: Optional[str] = Field(None, description="Zone name")
   description: Optional[str] = Field(None, description="Zone Description")


# READ
class ZoneRead(ZoneBase):
   id: int


# Project Table ------------------------------------------------------------------
class ProjectBase(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(..., description="Project Description")
    start_date: Optional[date]
    end_date: Optional[date]

# CREATE
class ProjectCreate(ProjectBase):
   pass

# UPDATE
class ProjectUpdate(BaseModel):
  name: Optional[str] = Field(None, description="Project name")
  description: Optional[str] = Field(None, description="Project Description")
  start_date: Optional[date] 
  end_date: Optional[date]  

# READ 
class ProjectRead(ProjectBase):
   id: int


# Station Table ------------------------------------------------------------------
class StationBase(BaseModel):
    name: str = Field(..., description="Station name")
    description: Optional[str] = Field(..., description="Station Description")
    project_id: int = Field(..., description="Associated project ID")

# CREATE
class StationCreate(StationBase):
   pass

# UPDATE
class StationUpdate(BaseModel):
   name: Optional[str] = Field(None, description="Station name")
   description: Optional[str] = Field(None, description="Station Description")
   project_id: Optional[int]

# READ 
class StationRead(StationBase):
   id: int

# Join Table: EmployeeProjectZone ------------------------------------------------------------------
class EmployeeProjectZoneBase(BaseModel):
    employee_id: int
    project_id: int
    zone_id: int
    station_id: int


# CREATE
class EmployeeProjectZoneCreate(EmployeeProjectZoneBase):
   pass

# UPDATE
class EmployeeProjectZoneUpdate(BaseModel):
    employee_id: Optional[int]
    project_id: Optional[int]
    zone_id: Optional[int]
    station_id: Optional[int]
# READ 
class EmployeeProjectZoneRead(EmployeeProjectZoneBase):
   id: int


# Hours Logged Table ------------------------------------------------------------------
class HoursLoggedBase(BaseModel):
    employee_project_zone_id: int
    date: Optional[date] = Field(...,description="The date when hours were logged.")  # Remember to check the usage of datetime lib
    phase: Literal['SIM', 'SOFTWARE', 'DEBUG', 'INS', 'TRV']
    hours_worked: float

# CREATE
class HoursLoggedCreate(HoursLoggedBase):
   pass

# UPDATE
class HoursLoggedUpdate(BaseModel):
   date: Optional[str] = Field(None,description="The date when hours were logged.")
   phase: Optional[Literal['SIM', 'SOFTWARE', 'DEBUG', 'INS', 'TRV']]
   hours_worked: Optional[float]
# READ 
class HoursLoggedRead(HoursLoggedBase):
   id: int

# Project Metrics Table ------------------------------------------------------------------
class ProjectMetricsBase(BaseModel):
    project_id: int
    planned_hours: float
    estimated_completion_date: Optional[str]
    actual_hours_logged: Optional[float]

# CREATE
class ProjectMetricsCreate(ProjectMetricsBase):
   pass

# UPDATE
class ProjectMetricsUpdate(BaseModel):
   planned_hours: Optional[float]
   estimated_completion_date: Optional[str]
   actual_hours_logged: Optional[float]
# READ 

class ProjectMetricsRead(ProjectMetricsBase):
   id: int


#############################################################################################################################

#API Endpoints. Remember to add a response_model
app = FastAPI() 
#base origin to call endpoints
origins = [
"http://localhost:3000"
]

#can used specified methods you want or block certain headers. only allows trusted sources (of your choosing)
app.add_middleware(CORSMiddleware,allow_origins=origins, allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

def get_db():
    conn = psy.connect(
        database=db_connect_info[0],
        user=db_connect_info[1],
        host=db_connect_info[2],
        password=db_connect_info[3],
        port=int(db_connect_info[4])
    )
    try:
        yield conn
    finally:
        conn.close()
# CREATE ----------------------------
@app.post("/employees", response_model=EmployeeRead)
def create_employee(employee: EmployeeCreate, db=Depends(get_db)):
  try:
      cur = db.cursor()
      insert_query = """
      INSERT INTO employee (firstname,lastname)
      VALUES (%s,%s)
      RETURNING id, firstname, lastname;
      """
      cur.execute(insert_query,(employee.firstname,employee.lastname))
      new_employee = cur.fetchone()
      db.commit()
      cur.close()
      return {
          "id": new_employee[0],
          "firstname": new_employee[2],
          "lastname": new_employee[2]
      }
  except Exception as e: 
      db.rollback()
      raise HTTPException(status_code=500, detail=f"Error creating employee: {str(e)}")

# READ ALL --------------------------
@app.get("/employees", response_model=List[EmployeeRead])
def get_all_employees(db=Depends(get_db)):
  try:
      cur = db.cursor()
      query = """SELECT * FROM employee"""
      cur.execute(query)
      rows = cur.fetchall()
      cur.close()

      employees = [
          {"id": row[0], "firstname": row[1] , "lastname": row[2]}
          for row in rows
      ]
      return employees
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=f"Error reading employees: {str(e)}")

# READ/SEARCH ONE --------------------------
@app.get("/employees/search", response_model=List[EmployeeRead])
def search_employees(
    firstname: Optional[str] = Query(None),
    lastname: Optional[str] = Query(None),
    db=Depends(get_db)
):
    try:
        cur = db.cursor()

        # Build dynamic query
        query = """SELECT id, firstname, lastname FROM employee WHERE TRUE"""
        params = []

        if firstname:
            query += " AND LOWER(firstname) = LOWER(%s)"
            params.append(firstname)
        if lastname:
            query += " AND LOWER(lastname) = LOWER(%s)"
            params.append(lastname)

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()

        employees = [
            {"id": row[0], "firstname": row[1], "lastname": row[2]}
            for row in rows
        ]
        return employees

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error searching employees: {str(e)}")


# UPDATE ----------------------------
@app.put("/employees/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, employee: EmployeeUpdate, db=Depends(get_db)):
    ...


#DELETE -----------------------------
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db=Depends(get_db)):
    ...
# ZONES ENDPOINTS _______________________________________



@app.post("/zones", response_model=ZoneRead)
def create_zone(zone: ZoneCreate, db=Depends(get_db)):
    ...

@app.get("/zones", response_model=List[ZoneRead])
def get_all_zones(db=Depends(get_db)):
    ...

@app.get("/zones/{zone_id}", response_model=ZoneRead)
def get_zone(zone_id: int, db=Depends(get_db)):
    ...

@app.put("/zones/{zone_id}", response_model=ZoneRead)
def update_zone(zone_id: int, zone: ZoneUpdate, db=Depends(get_db)):
    ...

@app.delete("/zones/{zone_id}")
def delete_zone(zone_id: int, db=Depends(get_db)):
    ...

# PROJECTS ENDPOINTS _____________________________________

@app.post("/projects", response_model=ProjectRead)
def create_project(project: ProjectCreate, db=Depends(get_db)):
    ...

@app.get("/projects", response_model=List[ProjectRead])
def get_all_projects(db=Depends(get_db)):
    ...

@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db=Depends(get_db)):
    ...

@app.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, project: ProjectUpdate, db=Depends(get_db)):
    ...

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db=Depends(get_db)):
    ...

# STATIONS ENDPOINTS ________________________________________
@app.post("/stations", response_model=StationRead)
def create_station(station: StationCreate, db=Depends(get_db)):
    ...

@app.get("/stations", response_model=List[StationRead])
def get_all_stations(db=Depends(get_db)):
    ...

@app.get("/stations/{station_id}", response_model=StationRead)
def get_station(station_id: int, db=Depends(get_db)):
    ...

@app.put("/stations/{station_id}", response_model=StationRead)
def update_station(station_id: int, station: StationUpdate, db=Depends(get_db)):
    ...

@app.delete("/stations/{station_id}")
def delete_station(station_id: int, db=Depends(get_db)):
    ...

# EMPLOYEE_PROJECT_ZONE ENDPOINTS _____________________________
@app.post("/assignments", response_model=EmployeeProjectZoneRead)
def create_assignment(assignment: EmployeeProjectZoneCreate, db=Depends(get_db)):
    ...

@app.get("/assignments", response_model=List[EmployeeProjectZoneRead])
def get_all_assignments(db=Depends(get_db)):
    ...

@app.get("/assignments/{assignment_id}", response_model=EmployeeProjectZoneRead)
def get_assignment(assignment_id: int, db=Depends(get_db)):
    ...

@app.put("/assignments/{assignment_id}", response_model=EmployeeProjectZoneRead)
def update_assignment(assignment_id: int, assignment: EmployeeProjectZoneUpdate, db=Depends(get_db)):
    ...

@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db=Depends(get_db)):
    ...

# HOURS LOGGED ENDPOINTS _______________________________________
@app.post("/hours", response_model=HoursLoggedRead)
def log_hours(entry: HoursLoggedCreate, db=Depends(get_db)):
    ...

@app.get("/hours", response_model=List[HoursLoggedRead])
def get_all_hours(db=Depends(get_db)):
    ...

@app.get("/hours/{entry_id}", response_model=HoursLoggedRead)
def get_hours_entry(entry_id: int, db=Depends(get_db)):
    ...

@app.put("/hours/{entry_id}", response_model=HoursLoggedRead)
def update_hours_entry(entry_id: int, entry: HoursLoggedUpdate, db=Depends(get_db)):
    ...

@app.delete("/hours/{entry_id}")
def delete_hours_entry(entry_id: int, db=Depends(get_db)):
    ...

# METRICS ENDPOINTS ____________________________________________


@app.post("/metrics", response_model=ProjectMetricsRead)
def create_metrics(metrics: ProjectMetricsCreate, db=Depends(get_db)):
    ...

@app.get("/metrics", response_model=List[ProjectMetricsRead])
def get_all_metrics(db=Depends(get_db)):
    ...

@app.get("/metrics/{metrics_id}", response_model=ProjectMetricsRead)
def get_metrics(metrics_id: int, db=Depends(get_db)):
    ...

@app.put("/metrics/{metrics_id}", response_model=ProjectMetricsRead)
def update_metrics(metrics_id: int, metrics: ProjectMetricsUpdate, db=Depends(get_db)):
    ...

@app.delete("/metrics/{metrics_id}")
def delete_metrics(metrics_id: int, db=Depends(get_db)):
    ...




#Ref:  GET (get info), POST (create new), PUT (change existing), Delete


# @app.get('/') #in parenth, we have the path
# async def index():
#   return {"message": "Hello"}




# @app.get('/getdata')
# async def show_data(db=Depends(get_db)):
#   cur = db.cursor()
#   cur.execute("""SELECT * FROM profile""")
#   data = cur.fetchall()
#   return {"data": data}

# # raise HTTPException(status_code=404,detail='__ Not Found ')
