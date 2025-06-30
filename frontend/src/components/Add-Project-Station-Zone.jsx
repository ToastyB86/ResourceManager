import React, { useState, useEffect } from 'react';

export default function Add_Project_Station_Zone()
{
  
  const [projects, setProjects] = useState([]);
  const [zones, setZones] = useState([]);
  const [stations, setStations] = useState([]);

  // Projects sets
   const [name1, setName] = useState('');
   const [desc, setDescription] = useState('');
   const [startDate, setStart_date] = useState('');
   const [endDate, setEnd_date] = useState('');
   
   // Stations set
   const [name2, setName2] = useState('');
   const [desc1,setDescription1] = useState('');

   // Zones set
   const [name3, setName3] = useState('');
   const [desc2,setDescription2] = useState('');


   const handleAddProject = () => {
    fetch('http://localhost:8000/projects', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        name: name1, 
        description: desc, 
        start_date: startDate,
         end_date: endDate})
    }).then(() => {
    setName('');
    setDescription('');
    setStart_date('');
    setEnd_date('');
  });
   };

   const handleAddStation = () => {

    fetch('http://localhost:8000/stations', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name: name2, description: desc1})
    }).then(() => {
    setName2('');
    setDescription1('');
  });
   };

   const handleAddZone = () => {
    fetch('http://localhost:8000/zones', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name: name3, description: desc2})
    }).then(() => {
    setName3('');
    setDescription2('');
  });
   };


// fetch returned data from backend
  useEffect(() => {
    fetch('http://localhost:8000/projects').then(r => r.json()).then(setProjects);
    fetch('http://localhost:8000/zones').then(r => r.json()).then(setZones);
    fetch('http://localhost:8000/stations').then(r => r.json()).then(setStations);
  }, []);







return(
<div>
      <h2>Add Project, Zone, or Station</h2>
      <div className="form-group">
        <label>Add Project Name</label>
        <input value={name1} onChange={e=>setName(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Add Project Description</label>
        <input value={desc} onChange={e=>setDescription(e.target.value)} />
      </div>
       <div className="form-group">
        <label>Add Project start date</label>
        <input value={startDate} onChange={e=>setStart_date(e.target.value)} />
      </div>
       <div className="form-group">
        <label>Add Project end date</label>
        <input value={endDate} onChange={e=>setEnd_date(e.target.value)} />
      </div>
      <button className="btn1" onClick={handleAddProject}>Add Project</button>
      <div className="form-group">
        <label>Add Station Name</label>
        <input value={name2} onChange={e=>setName2(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Add Station Description</label>
        <input value={desc1} onChange={e=>setDescription1(e.target.value)} />
      </div>
      <button className="btn1" onClick={handleAddStation}>Add Station</button>
      <div className="form-group">
        <label>Add Zone Name</label>
        <input value={name3} onChange={e=>setName3(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Add Zone Description</label>
        <input value={desc2} onChange={e=>setDescription2(e.target.value)} />
      </div>
      <button className="btn1" onClick={handleAddZone}>Add Zone</button>
    </div>
);
}