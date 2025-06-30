from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
from datetime import date, timedelta
import psycopg2 as psy
from psycopg2.pool import SimpleConnectionPool
from fastapi import  HTTPException, Depends, status, APIRouter
from dotenv import load_dotenv
import os




load_dotenv()
raw_info= os.getenv("DB_CONNECT_INFO")
db_connect_info = raw_info.split(",") if raw_info else []
router = APIRouter()


#@router

pool = SimpleConnectionPool( minconn=1, maxconn=30,
                             database=db_connect_info[0],
        user=db_connect_info[1],
        host=db_connect_info[2],
        password=db_connect_info[3],
        port=int(db_connect_info[4]),
                            )

def get_db():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

# Utility functions for date calculations
WORKDAY_HOURS = 9

def business_days_between(start: date, end: date):
    return list(rrule(DAILY, dtstart=start, until=end, byweekday=(MO, TU, WE, TH, FR)))


def add_business_days(start: date, num_days: int):
    days = 0
    current = start
    while days < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return current


@router.post("/hours/bulk")
def bulk_log_hours(
    assignment_id: int,
    start_date: date,
    end_date: date,
    hours_per_day: float,
    db=Depends(get_db),
):
    # Creates one HoursLogged entry per business day in [start_date, end_date], each with `hours_per_day`, and then updates the ProjectMetrics.actual_hours_logged table in postgres

    try:
        cur = db.cursor()
        dates = business_days_between(start_date, end_date)

        #  Insert all of  the days in one go
        args_str = ",".join(
            cur.mogrify(
                "(%s,%s,%s,%s)", (assignment_id, d, "WORK", hours_per_day)
            ).decode()
            for d in dates
        )
        cur.execute(
            "INSERT INTO hours_logged (employee_project_zone_id, date, phase, hours_worked) VALUES "
            + args_str
        )

        #  Sum actual hours by project and update project_metrics
        cur.execute(
            """
            UPDATE project_metrics pm
            SET actual_hours_logged = sub.total
            FROM (
                SELECT epz.project_id, SUM(h.hours_worked) AS total
                  FROM hours_logged h
                  JOIN employee_project_zone epz
                    ON h.employee_project_zone_id = epz.id
                 WHERE epz.id = %s
                 GROUP BY epz.project_id
            ) AS sub
           WHERE pm.project_id = sub.project_id
        """,
            (assignment_id,),
        )

        db.commit()
        cur.close()
        return {"logged_days": len(dates), "hours_per_day": hours_per_day}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Bulk log failed: {e}")


@router.patch("/projects/{project_id}/shift")
def shift_project_dates(
    project_id: int, days: int, db=Depends(get_db)  
):

    # Adds `days` to project start/end dates, shifts all its hours_logged entries
    # by the same amount (within the original date span), and recomputes estimated_completion_date based on planned_hours.
 

    try:
        cur = db.cursor()

        # Shift the project's own dates
        cur.execute(
            """
            UPDATE projects
               SET start_date = start_date + interval '%s day',
                   end_date   = end_date   + interval '%s day'
             WHERE id = %s
             RETURNING start_date, end_date
        """,
            (days, days, project_id),
        )
        proj = cur.fetchone()
        if not proj:
            raise HTTPException(404, "Project not found.")

        orig_start, orig_end = proj

        # Shift hours_logged dates that fall in the original window
        cur.execute(
            """
            UPDATE hours_logged h
            SET date = date + interval '%s day'
            FROM employee_project_zone epz
            WHERE h.employee_project_zone_id = epz.id
              AND epz.project_id = %s
              AND h.date BETWEEN %s AND %s
        """,
            (days, project_id, orig_start, orig_end),
        )

        #  Recompute estimated_completion_date in project_metrics
        #    as start_date + N business days, where N = ceil(planned_hours / WORKDAY_HOURS)
        cur.execute(
            """
            SELECT planned_hours, pm.id
              FROM project_metrics pm
             WHERE pm.project_id = %s
        """,
            (project_id,),
        )
        planned, metrics_id = cur.fetchone()
        needed_days = -(-planned // WORKDAY_HOURS)  # ceil
        new_est = add_business_days(proj[0], int(needed_days) - 1)

        cur.execute(
            """
            UPDATE project_metrics
               SET estimated_completion_date = %s
             WHERE id = %s
        """,
            (new_est, metrics_id),
        )

        db.commit()
        cur.close()
        return {
            "new_start": proj[0],
            "new_end": proj[1],
            "new_estimated_completion": new_est,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Shift failed: {e}")


