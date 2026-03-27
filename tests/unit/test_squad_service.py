"""
Тесты для SquadCommandCenter — статус агентов, назначение задач.
"""
import pytest


def test_squad_has_all_roles():
    """Все роли присутствуют в штабе."""
    from app.services.jarvis.squad_service import SquadCommandCenter, SquadRole
    center = SquadCommandCenter()

    for role in SquadRole:
        assert center.get_employee(role) is not None, f"Роль {role.value} отсутствует"


def test_get_all_employees_returns_list():
    """get_all_employees возвращает список словарей."""
    from app.services.jarvis.squad_service import SquadCommandCenter
    center = SquadCommandCenter()
    employees = center.get_all_employees()

    assert isinstance(employees, list)
    assert len(employees) > 0
    for emp in employees:
        assert "name" in emp
        assert "role" in emp
        assert "status" in emp


def test_broadcast_mission_sets_working_status():
    """broadcast_mission переводит всех агентов в статус working."""
    from app.services.jarvis.squad_service import SquadCommandCenter
    center = SquadCommandCenter()
    center.broadcast_mission("Тестовая миссия")

    for emp in center.employees.values():
        assert emp.status == "working"
        assert emp.last_action is not None


def test_employee_to_dict_structure():
    """to_dict возвращает корректную структуру."""
    from app.services.jarvis.squad_service import SquadCommandCenter, SquadRole
    center = SquadCommandCenter()
    emp = center.get_employee(SquadRole.CTO)
    assert emp is not None

    d = emp.to_dict()
    assert set(d.keys()) >= {"name", "role", "status", "last_action", "performance", "tasks"}
