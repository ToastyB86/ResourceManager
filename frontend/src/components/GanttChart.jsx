import React, { useEffect, useState } from 'react';

// Utility to generate date array between two dates
const getDatesBetween = (start, end) => {
  const dates = []; 
  const curr = new Date(start); // converts the start string in a javascript Date object. Curr is used to iterate from the start to the end date
  while (curr <= new Date(end)) { // continues as long as cur is less than or equal to the end date. new Date(end) creates a new Data object from the end string for comparison
    dates.push(new Date(curr)); //  .push() is an array method that adds a new item to the end of an array. new Date(curr) ensures a new object is added, not a reference to curr
    curr.setDate(curr.getDate() + 1); // curr.setDate(curr.getDate()+1) Moves curr forward by one day. curr.getDate() gets the day of the month. SsetDate() updates the day. "go to next day"
  }
  return dates;
};

export default function GanttChart() {
  const [projects, setProjects] = useState([]); //  store list of projects fetched from the backend/ useState returns a pair : current value of state (projects) and a function to update that value (setProjects)
  const [range, setRange] = useState({ start: '', end: '' });  // const [projects, setProjects] = useState([]) equivalent to const stateArray = useState([]), const projects = stateArray[0], const setProjects = stateArray[1]
  const [dates, setDates] = useState([]); 

  useEffect(() => {
    fetch('http://localhost:8000/projects')
      .then(r => r.json())
      .then(setProjects);
  }, []); // useEffect is a hook that runs side effects (like data fetching). runs once  when the component mounts because of the empty dependency array []. Fetches project data from backend
  // parses as JSON, and stores it in projects
  // effectsFunction -> a function that runs after the component renders : dependencyArray: A list of variables that the effect depends on :: useEffect(effectFunction, dependencyArray)  
  // setProjects updates the projects state. when you call setProjects(data) -> updates the projects variable with the new data, re-renders the component with the updated state
  // replaces entire state value with a new one

  useEffect(() => {
    if (range.start && range.end) {
      setDates(getDatesBetween(range.start, range.end));
    }
  }, [range]);

  const onChange = (e) => {
    setRange(r => ({ ...r, // copies all existing properties
       [e.target.name]: e.target.value // updates or adds this pair to range. Only overwrites the specific property you want to change. the name for example
       }));
  }; // runs every time the range state changes. Checks if both range.start and range.end are set. If they are, calls getDatesBetween(start,end) to generate an array of dates between those two values
// then updates the dates state using setDates
// React watches the range object. If it changes (either start or end), the effect re-runs. 
// const Onchange handles changes to the date input fields (like <input type="data" name="start" />). e.target.name will be "start". e.taget.value is the new date string selected by the user
// ... is the spread operator. In this case, copies all key-value pairs from the object r into a new object


// && below is a short circuit operator. if condition is true, renders div
//dates.map(...) loops through each date and renders a cell for it
//toLocaleDateString: Formats dates like Jun 27 
return (
    <div>
      <h2>Gantt View</h2>
      <div className="calendar-picker">
        <label>Start:</label>
        <input type="date" name="start" value={range.start} onChange={onChange} />
        <label>End:</label>
        <input type="date" name="end" value={range.end} onChange={onChange} />
      </div>

      {dates.length > 0 && (
        <div className="gantt">
          <div className="gantt-header">
            <div className="gantt-label">Task</div>
            {dates.map((d, i) => (
              <div key={i} className="gantt-cell">
                {d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
              </div>
            ))}
          </div>

          {projects.map(p => {
            const startIdx = dates.findIndex(d => d.toISOString().slice(0,10) === p.start_date);
            const endIdx = dates.findIndex(d => d.toISOString().slice(0,10) === p.end_date);
            const left = startIdx * 42; // cell width + border
            const width = (endIdx - startIdx + 1) * 42 - 4;

            return (
              <div className="gantt-row" key={p.id}>
                <div className="gantt-label">{p.name}</div>
                <div className="gantt-bar" style={{ left, width }} />
              </div>
            );
          })}
        </div>
      )}

      {!dates.length && <p>Please select a start and end date for the Gantt chart.</p>}
    </div>
  );
}
