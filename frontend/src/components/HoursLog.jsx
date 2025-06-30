import React, { useState, useEffect } from 'react'; // Two React hooks. useState manages component state and useEffect manages side effects (like fetching data) after the component mounts

export default function HoursLog() {
  const [assignments, setAsgn] = useState([]); // Holds a list of assignment options fetched from the backend
  const [entry, setEntry] = useState({}); // Stores the form data the user inputs (assignment ID, date, phase, hours)
  const [employees, setEmployees] = useState({});
  useEffect(()=>{
    fetch('http://localhost:8000/assignments').then(r=>r.json()).then(setAsgn); // Runs once when the component mounts. Fetches the assignment data from the backend and stores it in assignments
  },[]);
  // useEffect(() => {
  //   fetch('http://localhost:8000/employees')
  //     .then(res => res.json())
  //     .then(setEmployees)
  //     .catch(console.error);
  // }, []);
  const log = () => fetch('http://localhost:8000/hours',{ // sends POST request to log the hours. converts entry object to JSON and sends it to the /hours endpoint
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(entry)
  }).then(()=>alert('Logged')); //shows alert when request is completed

  return (
    <div>
  <h2>Log Hours</h2>

  <div className="form-group">
    <label>Assignment</label>
    <select onChange={e => setEntry({ ...entry, employee_project_zone_id: +e.target.value })}>
      <option value="">Select...</option>
      {assignments.map(a => (
        <option key={a.id} value={a.id}>{`#${a.id}`}</option>
      ))}
    </select>
  </div>

 {/* <div className="form-group">
    <label>Employee</label>
    <select onChange={e => setEntry({ ...entry, employee: +e.target.value })}>
      <option value="">Select...</option>
      {employees.map(emp => (
        <option key={emp.id} value={emp.id}>{`${emp.firstname} ${emp.lastname}`}</option>
      ))}
    </select>
  </div> */}

  <div className="form-group">
    <label>Date</label>
    <input type="date" onChange={e => setEntry({ ...entry, date: e.target.value })} />
  </div>

  <div className="form-group">
    <label>Phase</label>
    <select onChange={e => setEntry({ ...entry, phase: e.target.value })}>
      <option>SIM</option>
      <option>SOFTWARE</option>
      <option>DEBUG</option>
      <option>INS</option>
      <option>TRV</option>
    </select>
  </div>

  <div className="form-group">
    <label>Hours Worked</label>
    <input type="number" step="0.1" onChange={e => setEntry({ ...entry, hours_worked: +e.target.value })} />
  </div>

  <button className="btn" onClick={log}>Log</button>
</div>


  );
}
