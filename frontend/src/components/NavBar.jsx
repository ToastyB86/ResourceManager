import React from 'react';
import { NavLink } from 'react-router-dom'; 

export default function NavBar() {
  return (
    <nav className="navbar">
      <div className="nav-links">
        <NavLink to="/" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>View Employees</NavLink>
        <NavLink to="/add-employee" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>Add Employee</NavLink>
        <NavLink to="/log-hours" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>Log Hours</NavLink>
        <NavLink to="/gantt" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>Gantt View</NavLink>
        <NavLink to="/add-project-station-zone" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>Add New Project, Zone or Station</NavLink>
        <NavLink to="/view-stations" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>View Stations</NavLink>
        <NavLink to="/view-zones" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>View Zones</NavLink>
      </div>
    </nav>)
} 

