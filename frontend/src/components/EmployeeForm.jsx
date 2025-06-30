import React, { useState, useEffect } from 'react';

export default function EmployeeForm() {
  const [first, setFirst] = useState('');
  const [last, setLast] = useState(''); // last will be of type string
  const [projects, setProjects] = useState([]);
  const [zones, setZones] = useState([]); 
  const [stations, setStations] = useState([]); //Empty Array
  const [assignment, setAssignment] = useState({}); //Empty Object

  useEffect(() => {
    fetch('http://localhost:8000/projects').then(r => r.json()).then(setProjects);
    fetch('http://localhost:8000/zones').then(r => r.json()).then(setZones);
    fetch('http://localhost:8000/stations').then(r => r.json()).then(setStations);
  }, []);

  const handleSubmit = () => {
    // create employee then assignment
    fetch('http://localhost:8000/employees', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({firstname:first, lastname:last})
    })
      .then(res => res.json())
      .then(emp => fetch('http://localhost:8000/assignments',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          employee_id: emp.id,
          project_id: assignment.project_id,
          zone_id: assignment.zone_id,
          station_id: assignment.station_id
        })
      }))
      .then(() => alert('Created!'))
      .catch(console.error);
  };

  return (
    <div>
      <h2>Add Employee & Assignment</h2>
      <div className="form-group">
        <label>First Name</label>
        <input value={first} onChange={e=>setFirst(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Last Name</label>
        <input value={last} onChange={e=>setLast(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Project</label>
        <select onChange={e=>setAssignment(a=>({...a,project_id: +e.target.value}))}>
          <option value="">Select...</option>
          {projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label>Zone</label>
        <select onChange={e=>setAssignment(a=>({...a,zone_id: +e.target.value}))}>
          <option value="">Select...</option>
          {zones.map(z=><option key={z.id} value={z.id}>{z.name}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label>Station</label>
        <select onChange={e=>setAssignment(a=>({...a,station_id: +e.target.value}))}>
          <option value="">Select...</option>
          {stations.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>
      <button className="btn" onClick={handleSubmit}>Create</button>
    </div>
  );
}