import React, {useEffect, useState } from 'react';

export default function ViewZones(){
// Define 
const [zones, setZones] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/zones')
      .then(res => res.json())
      .then(data => setStations(data))
      .catch(console.error);
  }, []);


  return(
<div>
<h2>Zones</h2>
<table className ="table">
<thread>
<tr><th>ID</th><th>Name</th><th>Description</th></tr>
</thread>
<tbody>
{zones.map(zon => (
<tr key={zon.id}>
<td>{zon.id}</td>
<td>{zon.name}</td>
<td>{zon.description}</td>
</tr>
))}
</tbody>
</table>
</div>
  );
}