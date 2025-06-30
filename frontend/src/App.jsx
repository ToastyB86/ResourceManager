import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import EmployeeList from './components/EmployeeList';
import EmployeeForm from './components/EmployeeForm';
import HoursLog from './components/HoursLog';
import GanttChart from './components/GanttChart';
import './index.css';
import Add_Project_Station_Zone from './components/Add-Project-Station-Zone';
import ViewStations from './components/ViewStations';
import ViewZones from './components/ViewZones';
export default function App() {
  return (
    <Router>
      <NavBar />
      <div className="container">
        <Routes>
          <Route path="/" element={<EmployeeList />} />
          <Route path="/add-employee" element={<EmployeeForm />} />
          <Route path="/log-hours" element={<HoursLog />} />
          <Route path="/gantt" element={<GanttChart />} />
          <Route path= "/add-project-station-zone" element={<Add_Project_Station_Zone/>} />
          <Route path= "/view-stations" element={<ViewStations/>} />
          <Route path= "/view-zones" element={<ViewZones/>} />
        </Routes>
      </div>
    </Router>
  );
}
