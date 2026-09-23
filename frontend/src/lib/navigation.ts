import {
  Calendar,
  ClipboardList,
  Eye,
  LayoutDashboard,
  ShieldCheck,
  Users,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  name: string;
  href: string;
  icon: LucideIcon;
  disabled?: boolean;
  description?: string;
  adminOnly?: boolean;
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
    description: "Appointments",
  },
  {
    name: "Waiting list",
    href: "/waiting-list",
    icon: ClipboardList,
    description: "For hospitalization",
  },
  {
    name: "Observation",
    href: "/observation",
    icon: Eye,
    description: "Follow-up",
  },
  {
    name: "Audit log",
    href: "/audit",
    icon: ShieldCheck,
    description: "Security audit",
    adminOnly: true,
  },
];
