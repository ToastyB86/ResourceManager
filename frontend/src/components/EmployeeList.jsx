import React, { useEffect, useState } from 'react';

export default function EmployeeList() {
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/employees')
      .then(res => res.json())
      .then(data => setEmployees(data))
      .catch(console.error);
  }, []);

  return (
    <div>
      <h2>Employees</h2>
      <table className="table">
        <thead>
          <tr><th>ID</th><th>First</th><th>Last</th></tr>
        </thead>
        <tbody>
          {employees.map(emp => (
            <tr key={emp.id}>
              <td>{emp.id}</td>
              <td>{emp.firstname}</td>
              <td>{emp.lastname}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
