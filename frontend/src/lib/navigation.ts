import {
  Calendar,
  ClipboardList,
  Eye,
  LayoutDashboard,
  Users,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  name: string;
  href: string;
  icon: LucideIcon;
  disabled?: boolean;
  description?: string;
}

export const navigation: NavItem[] = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    description: "Overview",
  },
  {
    name: "Patients",
    href: "/patients",
    icon: Users,
    description: "All patients",
  },
  {
    name: "Schedule",
    href: "/schedule",
    icon: Calendar,
    disabled: true,
    description: "Appointments",
  },
  {
    name: "Waiting list",
    href: "/waiting-list",
    icon: ClipboardList,
    disabled: true,
    description: "For hospitalization",
  },
  {
    name: "Observation",
    href: "/observation",
    icon: Eye,
    disabled: true,
    description: "Follow-up",
  },
];
