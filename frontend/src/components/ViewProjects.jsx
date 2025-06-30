import React, {useEffect, useState } from 'react';

export default function ViewProjects(){
// Define 
const [projects, setProjects] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/projects')
      .then(res => res.json())
      .then(data => setProjects(data))
      .catch(console.error);
  }, []);


  return(
<div>
<h2>Projects</h2>
<table className ="table">
<thread>
<tr><th>ID</th><th>Name</th><th>Description</th><th>Start Date</th><th>End Date</th></tr>
</thread>
<tbody>
{projects.map(proj => (
<tr key={proj.id}>
<td>{proj.name}</td>
<td>{proj.description}</td>
<td>{proj.start_date}</td>
<td>{proj.end_date}</td>
</tr>
))}
</tbody>
</table>
</div>
  );
}