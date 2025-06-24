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

db_connect_info = ["Resource Manager","postgres","localhost","1223","5432"]
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
@app.get("/employees/search", response_model=List[dict])
def search_employees(
    firstname: Optional[str] = Query(None),
    lastname: Optional[str] = Query(None),
    db=Depends(get_db)
):
    try:
        cur = db.cursor()

        query = """
        SELECT 
            e.id, e.firstname, e.lastname,
            p.id AS project_id, p.name AS project_name,
            z.id AS zone_id, z.name AS zone_name,
            s.id AS station_id, s.name AS station_name,
            h.phase, h.hours_worked, h.date
        FROM employee e
        LEFT JOIN employee_project_zone epz ON e.id = epz.employee_id
        LEFT JOIN projects p ON epz.project_id = p.id
        LEFT JOIN zones z ON epz.zone_id = z.id
        LEFT JOIN stations s ON epz.station_id = s.id
        LEFT JOIN hours_logged h ON epz.id = h.employee_project_zone_id
        WHERE TRUE
        """

        params = []
        if firstname:
            query += " AND LOWER(e.firstname) = LOWER(%s)"
            params.append(firstname)
        if lastname:
            query += " AND LOWER(e.lastname) = LOWER(%s)"
            params.append(lastname)

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()

        # Group by employee
        employees = {}
        for row in rows:
            emp_id = row[0]
            if emp_id not in employees:
                employees[emp_id] = {
                    "id": emp_id,
                    "firstname": row[1],
                    "lastname": row[2],
                    "assignments": []
                }

            assignment = {
                "project": {"id": row[3], "name": row[4]},
                "zone": {"id": row[5], "name": row[6]},
                "station": {"id": row[7], "name": row[8]},
                "phase": row[9],
                "hours_worked": row[10],
                "date": row[11]
            }
            employees[emp_id]["assignments"].append(assignment)

        return list(employees.values())

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error searching employees: {str(e)}")


# UPDATE ----------------------------
@app.put("/employees/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, employee: EmployeeUpdate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        fields = []
        values = []

        if employee.firstname:
            fields.append("firstname = %s")
            values.append(employee.firstname)
        if employee.lastname:
            fields.append("lastname = %s")
            values.append(employee.lastname)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")

        values.append(employee_id)
        query = f"UPDATE employee SET {', '.join(fields)} WHERE id = %s RETURNING id, firstname, lastname"
        cur.execute(query, tuple(values))
        updated = cur.fetchone()
        db.commit()
        cur.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Employee not found.")

        return {"id": updated[0], "firstname": updated[1], "lastname": updated[2]}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating employee: {str(e)}")


#DELETE -----------------------------
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM employee WHERE id = %s RETURNING id", (employee_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()

        if not deleted:
            raise HTTPException(status_code=404, detail="Employee not found.")
        return {"message": f"Employee {employee_id} deleted successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting employee: {str(e)}")
# ZONES ENDPOINTS _______________________________________



@app.post("/zones", response_model=ZoneRead)
def create_zone(zone: ZoneCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO zones (name, description) VALUES (%s, %s) RETURNING id, name, description",
            (zone.name, zone.description)
        )
        new_zone = cur.fetchone()
        db.commit()
        cur.close()
        return {"id": new_zone[0], "name": new_zone[1], "description": new_zone[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating zone: {str(e)}")


@app.get("/zones", response_model=List[ZoneRead])
def get_all_zones(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("SELECT id, name, description FROM zones")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fetching zones: {str(e)}")

@app.get("/zones/{zone_id}", response_model=ZoneRead)
def get_zone(zone_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("SELECT id, name, description FROM zones WHERE id = %s", (zone_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Zone not found.")
        return {"id": row[0], "name": row[1], "description": row[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fetching zone: {str(e)}")

@app.put("/zones/{zone_id}", response_model=ZoneRead)
def update_zone(zone_id: int, zone: ZoneUpdate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        fields = []
        values = []

        if zone.name:
            fields.append("name = %s")
            values.append(zone.name)
        if zone.description:
            fields.append("description = %s")
            values.append(zone.description)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")

        values.append(zone_id)
        query = f"UPDATE zones SET {', '.join(fields)} WHERE id = %s RETURNING id, name, description"
        cur.execute(query, tuple(values))
        updated = cur.fetchone()
        db.commit()
        cur.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Zone not found.")

        return {"id": updated[0], "name": updated[1], "description": updated[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating zone: {str(e)}")


@app.delete("/zones/{zone_id}")
def delete_zone(zone_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM zones WHERE id = %s RETURNING id", (zone_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()

        if not deleted:
            raise HTTPException(status_code=404, detail="Zone not found.")
        return {"message": f"Zone {zone_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting zone: {str(e)}")


# PROJECTS ENDPOINTS _____________________________________

@app.post("/projects", response_model=ProjectRead)
def create_project(project: ProjectCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("""INSERT INTO projects (name, description) VALUES (%s,%s) RETURNING id, name, description""",(project.name, project.description))
        new_project = cur.fetchone()
        db.commit()
        cur.close()
        return {"id": new_project[0], "name": new_project[1], "description": new_project[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error creating project: {str(e)}")
    
@app.get("/projects", response_model=List[ProjectRead])
def get_all_projects(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("""SELECT id, name, description FROM projects""")
        rows = cur.fetchall()
        cur.close()
        return[{"id":r[0],"name":r[1],"description":r[2]}for r in rows]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error fetching projects: {str(e)}")

@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("""SELECT id, name, description FROM projects WHERE id = %s""",(project_id))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found.")
        return{"id":row[0],"name":row[1],"description":row[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error fetching project: {str(e)}")

@app.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, project: ProjectUpdate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        fields = []
        values = []
        if project.name:
            fields.append("name = %s")
            values.append(project.name)
        if project.description:
            fields.append("description=%s")
            values.append(project.description)

        if not fields:
            raise HTTPException(status_code=400,detail="No fields to update.")
        values.append(project_id)
        query = f"""UPDATE projects SET {', '.join(fields)} WHERE id = %s RETURNING id, name, description"""
        cur.execute(query, tuple(values))
        updated = cur.fetchone()
        db.commit()
        db.close()
        
        if not updated:
            raise HTTPException(status_code=404, detail="Project not found.")
        return{"id": updated[0], "name": updated[1], "description": updated[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error updating project: {str(e)}")

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM projects WHERE id = %s RETURNING id",(project_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()

        if not deleted:
            raise HTTPException(status_code=404,detail="Project not found.")
        return{"message": f"Project {project_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error deleting project: {str(e)}")
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

# func to shift dates


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
