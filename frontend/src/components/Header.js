import React, { useState } from "react";
import "./Header.css";

function Header() {
  return (
    <div className="header">
      <div className="nav-buttons">
        <DropdownButton title="Option 1" items={["Item 1", "Item 2", "Item 3"]} />
        <DropdownButton title="Option 2" items={["Item A", "Item B", "Item C"]} />
        <DropdownButton title="Option 3" items={["Item X", "Item Y", "Item Z"]} />
      </div>
      <div className="menu-icon">&#9776;</div>
    </div>
  );
}

function DropdownButton({ title, items }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="dropdown">
      <button className="dropbtn" onClick={() => setOpen(!open)}>
        {title}
      </button>
      {open && (
        <div className="dropdown-content">
          {items.map((item, index) => (
            <button key={index} className="dropdown-item">
              {item}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Header;