# import uvicorn as uv
from fastapi.middleware.cors import (
    CORSMiddleware,
)  # cross origin research sharing (CORS)
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional, Literal, Annotated
from enum import IntEnum
from datetime import date, timedelta
from pydantic import BaseModel, Field  # for documentation
import psycopg2 as psy
from psycopg2 import sql
from fastapi import Query
#from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
from psycopg2.pool import SimpleConnectionPool
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# from jose import JWTError, jwt
# from passlib.context import CryptContext
# import os

db_connect_info = ["Resource Manager", "postgres", "localhost", "1223", "5432"]
# Note the index of db_connect_info. From 0 -> 4
# database="postgres"
# user="postgres"
# host="localhost"
# password="1223"
# port=5432
# documentation schema. Most likely will make one for each table


# Employee Table ------------------------------------------------------------------
class EmployeeBase(BaseModel):
    firstname: str = Field(
        ..., min_length=3, max_length=255, description="First name of employee"
    )
    lastname: str = Field(
        ..., min_length=2, max_length=255, description="Last name of employee"
    )


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
    start_date: Optional[str]
    end_date: Optional[str]


# CREATE
class ProjectCreate(ProjectBase):
    pass


# UPDATE
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project Description")
    start_date: Optional[str]
    end_date: Optional[str]


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
    # type: ignore # Remember to check the usage of datetime lib
    date: Optional[str] = Field(...,
                                 description="The date when hours were logged.")
    phase: Literal["SIM", "SOFTWARE", "DEBUG", "INS", "TRV"]
    hours_worked: float


# CREATE
class HoursLoggedCreate(HoursLoggedBase):
    pass


# UPDATE
class HoursLoggedUpdate(BaseModel):
    date: Optional[str] = Field(
        None, description="The date when hours were logged.")
    phase: Optional[Literal["SIM", "SOFTWARE", "DEBUG", "INS", "TRV"]]
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

# API Endpoints. Remember to add a response_model
app = FastAPI()
# base origin to call endpoints
origins = ["http://localhost:3000"]

# can used specified methods you want or block certain headers. only allows trusted sources (of your choosing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = psy.connect(
        database=db_connect_info[0],
        user=db_connect_info[1],
        host=db_connect_info[2],
        password=db_connect_info[3],
        port=int(db_connect_info[4]),
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
        cur.execute(insert_query, (employee.firstname, employee.lastname))
        new_employee = cur.fetchone()
        db.commit()
        cur.close()
        return {
            "id": new_employee[0],
            "firstname": new_employee[1],
            "lastname": new_employee[2],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating employee: {str(e)}"
        )


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
            {"id": row[0], "firstname": row[1], "lastname": row[2]} for row in rows
        ]
        return employees
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error reading employees: {str(e)}"
        )


# READ/SEARCH ONE --------------------------
@app.get("/employees/search", response_model=List[dict])
def search_employees(
    firstname: Optional[str] = Query(None),
    lastname: Optional[str] = Query(None),
    db=Depends(get_db),
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
                    "assignments": [],
                }

            assignment = {
                "project": {"id": row[3], "name": row[4]},
                "zone": {"id": row[5], "name": row[6]},
                "station": {"id": row[7], "name": row[8]},
                "phase": row[9],
                "hours_worked": row[10],
                "date": row[11],
            }
            employees[emp_id]["assignments"].append(assignment)

        return list(employees.values())

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error searching employees: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500, detail=f"Error updating employee: {str(e)}"
        )


# DELETE -----------------------------
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "DELETE FROM employee WHERE id = %s RETURNING id", (employee_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()

        if not deleted:
            raise HTTPException(status_code=404, detail="Employee not found.")
        return {"message": f"Employee {employee_id} deleted successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting employee: {str(e)}"
        )


# ZONES ENDPOINTS _______________________________________


@app.post("/zones", response_model=ZoneRead)
def create_zone(zone: ZoneCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO zones (name, description) VALUES (%s, %s) RETURNING id, name, description",
            (zone.name, zone.description),
        )
        new_zone = cur.fetchone()
        db.commit()
        cur.close()
        return {"id": new_zone[0], "name": new_zone[1], "description": new_zone[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating zone: {str(e)}")


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
        raise HTTPException(
            status_code=500, detail=f"Error fetching zones: {str(e)}")


@app.get("/zones/{zone_id}", response_model=ZoneRead)
def get_zone(zone_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, name, description FROM zones WHERE id = %s", (zone_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Zone not found.")
        return {"id": row[0], "name": row[1], "description": row[2]}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching zone: {str(e)}")


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
        raise HTTPException(
            status_code=500, detail=f"Error updating zone: {str(e)}")


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
        raise HTTPException(
            status_code=500, detail=f"Error deleting zone: {str(e)}")


# PROJECTS ENDPOINTS _____________________________________


@app.post("/projects", response_model=ProjectRead)
def create_project(project: ProjectCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO projects (name, description, start_date, end_date) VALUES (%s,%s,%s,%s) RETURNING id, name, description, start_date, end_date",
            (project.name, project.description,project.start_date,project.end_date), 
        )
        new_project = cur.fetchone()
        db.commit()
        cur.close()
        return {
            "id": new_project[0],
            "name": new_project[1],
            "description": new_project[2],
            "start_date": new_project[3],
            "end_date": new_project[4]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating project: {str(e)}")


@app.get("/projects", response_model=List[ProjectRead])
def get_all_projects(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("""SELECT id, name, description, start_date, end_date FROM projects""")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "name": r[1], "description": r[2],"start_date":r[3],"end_date":r[4]} for r in rows]
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching projects: {str(e)}"
        )


@app.get("/projects/{project_id}", response_model=ProjectRead) 
def get_project(project_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            """SELECT id, name, description, start_date, end_date FROM projects WHERE id = %s""",
            (project_id,),
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found.")
        return {"id": row[0], "name": row[1], "description": row[2], "start_date": row[3],"end_date": row[4]}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching project: {str(e)}")


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
        if project.start_date:
            fields.append("start_date = %s")
            values.append(project.start_date)
        if project.end_date:
            fields.append("end_date=%s")
            values.append(project.end_date)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")
        values.append(project_id,)
        query = f"""UPDATE projects SET {', '.join(fields)} WHERE id = %s RETURNING id, name, description, start_date, end_date"""
        cur.execute(query, tuple(values))
        updated = cur.fetchone()
        db.commit()
        cur.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Project not found.")
        return {"id": updated[0], "name": updated[1], "description": updated[2], "start_date": updated[3], "end_date": updated[4]}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating project: {str(e)}")


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "DELETE FROM projects WHERE id = %s RETURNING id", (project_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()

        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found.")
        return {"message": f"Project {project_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting project: {str(e)}")


# STATIONS ENDPOINTS ________________________________________
@app.post("/stations", response_model=StationRead)
def create_station(station: StationCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            """
            INSERT INTO stations (name, description, project_id)
            VALUES (%s, %s, %s)
            RETURNING id, name, description, project_id
            """,
            (station.name, station.description, station.project_id),
        )
        row = cur.fetchone()
        db.commit()
        cur.close()
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "project_id": row[3],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating station: {e}")


@app.get("/stations", response_model=List[StationRead])
def get_all_stations(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute("SELECT id, name, description, project_id FROM stations")
        rows = cur.fetchall()
        cur.close()
        return [
            {"id": r[0], "name": r[1], "description": r[2], "project_id": r[3]}
            for r in rows
        ]
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching stations: {e}")


@app.get("/stations/{station_id}", response_model=StationRead)
def get_station(station_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, name, description, project_id FROM stations WHERE id = %s",
            (station_id,),
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Station not found.")
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "project_id": row[3],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching station: {e}")


@app.put("/stations/{station_id}", response_model=StationRead)
def update_station(station_id: int, station: StationUpdate, db=Depends(get_db)):
    try: # make this so you can update only one, if you desire, instead of needing to populate each
        cur = db.cursor()
        fields, values = [], []
        if station.name is not None:
            fields.append("name = %s")
            values.append(station.name)
        if station.description is not None:
            fields.append("description = %s")
            values.append(station.description)
        if station.project_id is not None:
            fields.append("project_id = %s")
            values.append(station.project_id)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")
        values.append(station_id)
        query = f"UPDATE stations SET {', '.join(fields)} WHERE id = %s RETURNING id, name, description, project_id"
        cur.execute(query, tuple(values))
        row = cur.fetchone()
        db.commit()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Station not found.")
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "project_id": row[3],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating station: {e}")


@app.delete("/stations/{station_id}")
def delete_station(station_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "DELETE FROM stations WHERE id = %s RETURNING id", (station_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()
        if not deleted:
            raise HTTPException(status_code=404, detail="Station not found.")
        return {"message": f"Station {station_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting station: {e}")


# EMPLOYEE_PROJECT_ZONE ENDPOINTS _____________________________
@app.post("/assignments", response_model=EmployeeProjectZoneRead)
def create_assignment(assignment: EmployeeProjectZoneCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            """
            INSERT INTO employee_project_zone (employee_id, project_id, zone_id, station_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, employee_id, project_id, zone_id, station_id
            """,
            (
                assignment.employee_id,
                assignment.project_id,
                assignment.zone_id,
                assignment.station_id,
            ),
        )
        row = cur.fetchone()
        db.commit()
        cur.close()
        return {
            "id": row[0],
            "employee_id": row[1],
            "project_id": row[2],
            "zone_id": row[3],
            "station_id": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating assignment: {e}")


@app.get("/assignments", response_model=List[EmployeeProjectZoneRead])
def get_all_assignments(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, employee_id, project_id, zone_id, station_id FROM employee_project_zone"
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "id": r[0],
                "employee_id": r[1],
                "project_id": r[2],
                "zone_id": r[3],
                "station_id": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching assignments: {e}")


@app.get("/assignments/{assignment_id}", response_model=EmployeeProjectZoneRead)
def get_assignment(assignment_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, employee_id, project_id, zone_id, station_id FROM employee_project_zone WHERE id = %s",
            (assignment_id,),
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(
                status_code=404, detail="Assignment not found.")
        return {
            "id": row[0],
            "employee_id": row[1],
            "project_id": row[2],
            "zone_id": row[3],
            "station_id": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching assignment: {e}")


@app.put("/assignments/{assignment_id}", response_model=EmployeeProjectZoneRead)
def update_assignment(
    assignment_id: int, assignment: EmployeeProjectZoneUpdate, db=Depends(get_db)
):
    try:
        cur = db.cursor()
        fields, values = [], []
        if assignment.employee_id is not None:
            fields.append("employee_id = %s")
            values.append(assignment.employee_id)
        if assignment.project_id is not None:
            fields.append("project_id = %s")
            values.append(assignment.project_id)
        if assignment.zone_id is not None:
            fields.append("zone_id = %s")
            values.append(assignment.zone_id)
        if assignment.station_id is not None:
            fields.append("station_id = %s")
            values.append(assignment.station_id)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")
        values.append(assignment_id)
        query = f"""
            UPDATE employee_project_zone
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, employee_id, project_id, zone_id, station_id
        """
        cur.execute(query, tuple(values))
        row = cur.fetchone()
        db.commit()
        cur.close()
        if not row:
            raise HTTPException(
                status_code=404, detail="Assignment not found.")
        return {
            "id": row[0],
            "employee_id": row[1],
            "project_id": row[2],
            "zone_id": row[3],
            "station_id": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating assignment: {e}")


@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "DELETE FROM employee_project_zone WHERE id = %s RETURNING id",
            (assignment_id,),
        )
        deleted = cur.fetchone()
        db.commit()
        cur.close()
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Assignment not found.")
        return {"message": f"Assignment {assignment_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting assignment: {e}")


# HOURS LOGGED ENDPOINTS _______________________________________
@app.post("/hours", response_model=HoursLoggedRead)
def log_hours(entry: HoursLoggedCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            """
            INSERT INTO hours_logged (employee_project_zone_id, date, phase, hours_worked)
            VALUES (%s, %s, %s, %s)
            RETURNING id, employee_project_zone_id, date, phase, hours_worked
            """,
            (
                entry.employee_project_zone_id,
                entry.date, # fixed this from date to log_date. will have to recheck hour system after restart
                entry.phase,
                entry.hours_worked,
            ),
        )
        row = cur.fetchone()
        db.commit()
        cur.close()
        return {
            "id": row[0],
            "employee_project_zone_id": row[1],
            "date": row[2],
            "phase": row[3],
            "hours_worked": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error logging hours: {e}")


@app.get("/hours", response_model=List[HoursLoggedRead])
def get_all_hours(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, employee_project_zone_id, date, phase, hours_worked FROM hours_logged"
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "id": r[0],
                "employee_project_zone_id": r[1],
                "date": r[2],
                "phase": r[3],
                "hours_worked": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching hours: {e}")


@app.get("/hours/{entry_id}", response_model=HoursLoggedRead)
def get_hours_entry(entry_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, employee_project_zone_id, date, phase, hours_worked FROM hours_logged WHERE id = %s",
            (entry_id,),
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(
                status_code=404, detail="Hours entry not found.")
        return {
            "id": row[0],
            "employee_project_zone_id": row[1],
            "date": row[2],
            "phase": row[3],
            "hours_worked": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching hours entry: {e}")


@app.put("/hours/{entry_id}", response_model=HoursLoggedRead)
def update_hours_entry(entry_id: int, entry: HoursLoggedUpdate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        fields, values = [], []
        if entry.date is not None:
            fields.append("date = %s")
            values.append(entry.date)
        if entry.phase is not None:
            fields.append("phase = %s")
            values.append(entry.phase)
        if entry.hours_worked is not None:
            fields.append("hours_worked = %s")
            values.append(entry.hours_worked)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")
        values.append(entry_id)
        query = f"""
            UPDATE hours_logged
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, employee_project_zone_id, date, phase, hours_worked
        """
        cur.execute(query, tuple(values))
        row = cur.fetchone()
        db.commit()
        cur.close()
        if not row:
            raise HTTPException(
                status_code=404, detail="Hours entry not found.")
        return {
            "id": row[0],
            "employee_project_zone_id": row[1],
            "date": row[2],
            "phase": row[3],
            "hours_worked": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating hours entry: {e}")


@app.delete("/hours/{entry_id}")
def delete_hours_entry(entry_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "DELETE FROM hours_logged WHERE id = %s RETURNING id", (entry_id,))
        deleted = cur.fetchone()
        db.commit()
        cur.close()
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Hours entry not found.")
        return {"message": f"Hours entry {entry_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting hours entry: {e}")


# METRICS ENDPOINTS ____________________________________________
@app.post("/metrics", response_model=ProjectMetricsRead)
def create_metrics(metrics: ProjectMetricsCreate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            """
            INSERT INTO project_metrics (project_id, planned_hours, estimated_completion_date, actual_hours_logged)
            VALUES (%s, %s, %s, %s)
            RETURNING id, project_id, planned_hours, estimated_completion_date, actual_hours_logged
            """,
            (
                metrics.project_id,
                metrics.planned_hours,
                metrics.estimated_completion_date,
                metrics.actual_hours_logged,
            ),
        )
        row = cur.fetchone()
        db.commit()
        cur.close()
        return {
            "id": row[0],
            "project_id": row[1],
            "planned_hours": row[2],
            "estimated_completion_date": row[3],
            "actual_hours_logged": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating metrics: {e}")


@app.get("/metrics", response_model=List[ProjectMetricsRead])
def get_all_metrics(db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, project_id, planned_hours, estimated_completion_date, actual_hours_logged FROM project_metrics"
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "id": r[0],
                "project_id": r[1],
                "planned_hours": r[2],
                "estimated_completion_date": r[3],
                "actual_hours_logged": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching metrics: {e}")


@app.get("/metrics/{metrics_id}", response_model=ProjectMetricsRead)
def get_metrics(metrics_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, project_id, planned_hours, estimated_completion_date, actual_hours_logged FROM project_metrics WHERE id = %s",
            (metrics_id,),
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Metrics not found.")
        return {
            "id": row[0],
            "project_id": row[1],
            "planned_hours": row[2],
            "estimated_completion_date": row[3],
            "actual_hours_logged": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error fetching metrics: {e}")


@app.put("/metrics/{metrics_id}", response_model=ProjectMetricsRead)
def update_metrics(metrics_id: int, metrics: ProjectMetricsUpdate, db=Depends(get_db)):
    try:
        cur = db.cursor()
        fields, values = [], []
        if metrics.planned_hours is not None:
            fields.append("planned_hours = %s")
            values.append(metrics.planned_hours)
        if metrics.estimated_completion_date is not None:
            fields.append("estimated_completion_date = %s")
            values.append(metrics.estimated_completion_date)
        if metrics.actual_hours_logged is not None:
            fields.append("actual_hours_logged = %s")
            values.append(metrics.actual_hours_logged)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update.")
        values.append(metrics_id)
        query = f"""
            UPDATE project_metrics
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, project_id, planned_hours, estimated_completion_date, actual_hours_logged
        """
        cur.execute(query, tuple(values))
        row = cur.fetchone()
        db.commit()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Metrics not found.")
        return {
            "id": row[0],
            "project_id": row[1],
            "planned_hours": row[2],
            "estimated_completion_date": row[3],
            "actual_hours_logged": row[4],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating metrics: {e}")


@app.delete("/metrics/{metrics_id}")
def delete_metrics(metrics_id: int, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "DELETE FROM project_metrics WHERE id = %s RETURNING id", (
                metrics_id,)
        )
        deleted = cur.fetchone()
        db.commit()
        cur.close()
        if not deleted:
            raise HTTPException(status_code=404, detail="Metrics not found.")
        return {"message": f"Metrics {metrics_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting metrics: {e}")


# Utility functions for date calculations

# WORKDAY_HOURS = 9


# def business_days_between(start: date, end: date):
#     return list(rrule(DAILY, dtstart=start, until=end, byweekday=(MO, TU, WE, TH, FR)))


# def add_business_days(start: date, num_days: int):
#     days = 0
#     current = start
#     while days < num_days:
#         current += timedelta(days=1)
#         if current.weekday() < 5:
#             days += 1
#     return current


# @app.post("/hours/bulk")
# def bulk_log_hours(
#     assignment_id: int,
#     start_date: date,
#     end_date: date,
#     hours_per_day: float,
#     db=Depends(get_db),
# ):
#     # Creates one HoursLogged entry per business day in [start_date, end_date], each with `hours_per_day`, and then updates the ProjectMetrics.actual_hours_logged.

#     try:
#         cur = db.cursor()
#         dates = business_days_between(start_date, end_date)

#         # 1) Insert all the days in one go
#         args_str = ",".join(
#             cur.mogrify(
#                 "(%s,%s,%s,%s)", (assignment_id, d, "WORK", hours_per_day)
#             ).decode()
#             for d in dates
#         )
#         cur.execute(
#             "INSERT INTO hours_logged (employee_project_zone_id, date, phase, hours_worked) VALUES "
#             + args_str
#         )

#         # 2) Sum actual hours by project and update project_metrics
#         cur.execute(
#             """
#             UPDATE project_metrics pm
#             SET actual_hours_logged = sub.total
#             FROM (
#                 SELECT epz.project_id, SUM(h.hours_worked) AS total
#                   FROM hours_logged h
#                   JOIN employee_project_zone epz
#                     ON h.employee_project_zone_id = epz.id
#                  WHERE epz.id = %s
#                  GROUP BY epz.project_id
#             ) AS sub
#            WHERE pm.project_id = sub.project_id
#         """,
#             (assignment_id,),
#         )

#         db.commit()
#         cur.close()
#         return {"logged_days": len(dates), "hours_per_day": hours_per_day}
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(500, f"Bulk log failed: {e}")


# @app.patch("/projects/{project_id}/shift")
# def shift_project_dates(
#     project_id: int, days: int, db=Depends(get_db)  # positive or negative
# ):

#     # Adds `days` to project start/end dates, shifts all its hours_logged entries
#     # by the same amount (within the original date span), and recomputes estimated_completion_date
#     # based on planned_hours.

#     try:
#         cur = db.cursor()

#         # 1) Shift the project's own dates
#         cur.execute(
#             """
#             UPDATE projects
#                SET start_date = start_date + interval '%s day',
#                    end_date   = end_date   + interval '%s day'
#              WHERE id = %s
#              RETURNING start_date, end_date
#         """,
#             (days, days, project_id),
#         )
#         proj = cur.fetchone()
#         if not proj:
#             raise HTTPException(404, "Project not found.")

#         orig_start, orig_end = proj

#         # 2) Shift hours_logged dates that fall in the original window
#         cur.execute(
#             """
#             UPDATE hours_logged h
#             SET date = date + interval '%s day'
#             FROM employee_project_zone epz
#             WHERE h.employee_project_zone_id = epz.id
#               AND epz.project_id = %s
#               AND h.date BETWEEN %s AND %s
#         """,
#             (days, project_id, orig_start, orig_end),
#         )

#         # 3) Recompute estimated_completion_date in project_metrics
#         #    as start_date + N business days, where N = ceil(planned_hours / WORKDAY_HOURS)
#         cur.execute(
#             """
#             SELECT planned_hours, pm.id
#               FROM project_metrics pm
#              WHERE pm.project_id = %s
#         """,
#             (project_id,),
#         )
#         planned, metrics_id = cur.fetchone()
#         needed_days = -(-planned // WORKDAY_HOURS)  # ceil
#         new_est = add_business_days(proj[0], int(needed_days) - 1)

#         cur.execute(
#             """
#             UPDATE project_metrics
#                SET estimated_completion_date = %s
#              WHERE id = %s
#         """,
#             (new_est, metrics_id),
#         )

#         db.commit()
#         cur.close()
#         return {
#             "new_start": proj[0],
#             "new_end": proj[1],
#             "new_estimated_completion": new_est,
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(500, f"Shift failed: {e}")


# import io
# import pandas as pd
# from fastapi.responses import StreamingResponse

# @app.get("/export/{table_name}")
# def export_table(table_name: str, db=Depends(get_db)):
#     # 1) Query the full table
#     df = pd.read_sql(f"SELECT * FROM {table_name}", db)

#     # 2) Write to an in-memory Excel workbook
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, sheet_name=table_name, index=False)

#     # 3) Rewind and send as a download
#     output.seek(0)
#     return StreamingResponse(
#         output,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f"attachment; filename={table_name}.xlsx"},
#     )


# @app.get("/export/all")
# def export_all(db=Depends(get_db)):
#     tables = ["employee", "zones", "projects", "stations"]
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         for tbl in tables:
#             df = pd.read_sql(f"SELECT * FROM {tbl}", db)
#             df.to_excel(writer, sheet_name=tbl, index=False)
#     output.seek(0)
#     return StreamingResponse()


# func to shift dates


# Ref:  GET (get info), POST (create new), PUT (change existing), Delete


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
