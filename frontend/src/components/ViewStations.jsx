import React, {useEffect, useState } from 'react';

export default function ViewStations(){
// Define 
const [stations, setStations] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/stations')
      .then(res => res.json())
      .then(data => setStations(data))
      .catch(console.error);
  }, []);


  return(
<div>
<h2>Stations</h2>
<table className ="table">
<thread>
<tr><th>ID</th><th>Name</th><th>Description</th><th>Project ID</th></tr>
</thread>
<tbody>
{stations.map(stat => (
<tr key={stat.id}>
<td>{stat.id}</td>
<td>{stat.name}</td>
<td>{stat.description}</td>
<td>{stat.project_id}</td>
</tr>
))}
</tbody>
</table>
</div>
  );
}