import { BarChart2, FileText, Users, Calendar } from "lucide-react"
import "./Sidebar.css"

function SidebarIcon({ icon }) {
  return <button className="sidebar-icon">{icon}</button>
}

export default function Sidebar() {
  return (
    <div className="sidebar">
      <SidebarIcon icon={<BarChart2 />} />
      <SidebarIcon icon={<FileText />} />
      <SidebarIcon icon={<Users />} />
      <SidebarIcon icon={<Calendar />} />
    </div>
  )
}

