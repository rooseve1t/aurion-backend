import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger("jarvis-squad")

class SquadRole(Enum):
    CTO = "CTO"
    TECH_LEAD = "Tech Lead"
    SENIOR_DEV = "Senior Developer"
    QA = "QA"
    SECURITY = "Security"
    DEVOPS = "DevOps"
    ANALYST = "Analyst"
    RESEARCHER = "Researcher"

class VirtualEmployee:
    def __init__(self, name: str, role: SquadRole, description: str):
        self.name = name
        self.role = role
        self.description = description
        self.status = "standby"
        self.last_action: Optional[str] = None
        self.performance_score = 1.0
        self.active_tasks: List[str] = []

    def set_action(self, action: str):
        self.status = "working"
        self.last_action = action
        logger.info(f"👷 [{self.role.value}] {self.name}: {action}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role.value,
            "status": self.status,
            "last_action": self.last_action,
            "performance": self.performance_score,
            "tasks": self.active_tasks
        }

class SquadCommandCenter:
    """Централизованное управление виртуальным штабом Aurion (Stage 22: Final Staff)"""
    
    def __init__(self):
        self.employees: Dict[SquadRole, VirtualEmployee] = {
            SquadRole.CTO: VirtualEmployee("Alpha", SquadRole.CTO, "Architecture, system integrity, tech risks"),
            SquadRole.TECH_LEAD: VirtualEmployee("Sigma", SquadRole.TECH_LEAD, "Decomposition, code review, implementation"),
            SquadRole.SENIOR_DEV: VirtualEmployee("Lux", SquadRole.SENIOR_DEV, "Code implementation, solutions development"),
            SquadRole.QA: VirtualEmployee("Omega", SquadRole.QA, "Testing, scenarios, bug hunting"),
            SquadRole.SECURITY: VirtualEmployee("Sentinel", SquadRole.SECURITY, "Vulnerabilities, encryption, secure integration"),
            SquadRole.DEVOPS: VirtualEmployee("Flux", SquadRole.DEVOPS, "Infrastructure, deploy, CI/CD"),
            SquadRole.ANALYST: VirtualEmployee("Nexus", SquadRole.ANALYST, "Priorities, business value, user experience"),
            SquadRole.RESEARCHER: VirtualEmployee("Echo", SquadRole.RESEARCHER, "New tech research, voice models, TTS, cloning")
        }

    def get_employee(self, role: SquadRole) -> Optional[VirtualEmployee]:
        return self.employees.get(role)

    def get_all_employees(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.employees.values()]

    def broadcast_mission(self, mission: str):
        """Разослать миссию всему штабу"""
        logger.info(f"📢 CEO BROADCAST: {mission}")
        for emp in self.employees.values():
            emp.set_action(f"Analyzing mission: {mission}")

# Singleton
squad_center = SquadCommandCenter()

def get_squad_center():
    return squad_center
