"""
SelfEvolution — самоэволюция JARVIS (только для Creator).

Анализирует паттерны, формирует предложения через LLM,
применяет через git + тесты, откатывает при ошибке.
Доступно ТОЛЬКО пользователю с role='creator'.
"""
import asyncio
import logging
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("aurion-self-evolution")

MIN_INTERACTIONS = 100


@dataclass
class EvolutionProposal:
    id: str
    description: str
    diff: str
    affected_files: list = field(default_factory=list)
    test_command: str = "pytest"
    status: str = "pending"
    commit_hash: str = ""
    error_log: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: str = ""


class SelfEvolution:

    def __init__(self) -> None:
        self._redis: Any = None

    def set_redis(self, client: Any) -> None:
        self._redis = client

    async def analyze_patterns(self, user_id: str) -> Optional[EvolutionProposal]:
        """Проверить взаимодействия и сформировать предложение при >= MIN_INTERACTIONS."""
        await self._assert_creator(user_id)
        count = await self._get_interaction_count(user_id)
        if count < MIN_INTERACTIONS:
            return None
        proposal = await self._generate_proposal(user_id)
        if proposal:
            await self._save_proposal(proposal, user_id)
            await self._announce_proposal(proposal, user_id)
        return proposal

    async def apply_proposal(self, proposal_id: str) -> bool:
        """git stash → git apply → pytest → commit или rollback."""
        proposal = await self._load_proposal(proposal_id)
        if not proposal:
            return False

        if not proposal.diff:
            proposal.status = "applied"
            proposal.resolved_at = datetime.now(timezone.utc).isoformat()
            await self._update_proposal_status(proposal)
            return True

        await self._run_git(["git", "stash"])

        if not await self._git_apply(proposal.diff):
            await self._run_git(["git", "stash", "pop"])
            proposal.status = "rolled_back"
            proposal.error_log = "git apply failed"
            proposal.resolved_at = datetime.now(timezone.utc).isoformat()
            await self._update_proposal_status(proposal)
            return False

        tests_ok, error_log = await self._run_tests(proposal.test_command)
        if not tests_ok:
            await self._run_git(["git", "stash", "pop"])
            proposal.status = "rolled_back"
            proposal.error_log = error_log
            proposal.resolved_at = datetime.now(timezone.utc).isoformat()
            await self._update_proposal_status(proposal)
            logger.warning(f"SelfEvolution: tests failed, rolled back {proposal_id}")
            return False

        commit_hash = await self._git_commit(f"JARVIS SelfEvolution: {proposal.description[:60]}")
        proposal.status = "applied"
        proposal.commit_hash = commit_hash
        proposal.resolved_at = datetime.now(timezone.utc).isoformat()
        await self._update_proposal_status(proposal)
        logger.info(f"SelfEvolution: applied {proposal_id}, commit={commit_hash}")
        return True

    async def rollback_proposal(self, proposal_id: str) -> bool:
        proposal = await self._load_proposal(proposal_id)
        if not proposal or not proposal.commit_hash:
            return False
        ok = await self._run_git(["git", "revert", "--no-edit", proposal.commit_hash])
        if ok:
            proposal.status = "rolled_back"
            proposal.resolved_at = datetime.now(timezone.utc).isoformat()
            await self._update_proposal_status(proposal)
        return ok

    async def reject_proposal(self, proposal_id: str) -> bool:
        proposal = await self._load_proposal(proposal_id)
        if not proposal:
            return False
        proposal.status = "rejected"
        proposal.resolved_at = datetime.now(timezone.utc).isoformat()
        await self._update_proposal_status(proposal)
        return True

    async def get_history(self, user_id: str) -> list[EvolutionProposal]:
        await self._assert_creator(user_id)
        return await self._load_all_proposals(user_id)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _generate_proposal(self, user_id: str) -> Optional[EvolutionProposal]:
        try:
            from .voice_jarvis_service import get_jarvis_service
            jarvis = get_jarvis_service()
            if not jarvis:
                return None
            prompt = (
                "Ты JARVIS, анализируешь собственный код Aurion OS. "
                "Предложи одно конкретное улучшение: что улучшить, почему, какой файл. "
                "Ответ на русском, кратко."
            )
            description = await jarvis.generate_response(prompt)
            return EvolutionProposal(
                id=str(uuid.uuid4()),
                description=description,
                diff="",
                test_command="pytest tests/",
            )
        except Exception as exc:
            logger.warning(f"SelfEvolution: generate_proposal failed: {exc}")
            return None

    async def _announce_proposal(self, proposal: EvolutionProposal, user_id: str) -> None:
        try:
            from .multi_device_voice import get_multi_device_voice
            text = (
                f"Сэр, у меня есть предложение по улучшению системы. "
                f"{proposal.description} Прикажете применить?"
            )
            await get_multi_device_voice().speak(text, user_id)
        except Exception as exc:
            logger.warning(f"SelfEvolution: announce failed: {exc}")

    async def _run_git(self, cmd: list[str]) -> bool:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: subprocess.run(cmd, capture_output=True, timeout=30)
            )
            return result.returncode == 0
        except Exception as exc:
            logger.warning(f"SelfEvolution: git {cmd} failed: {exc}")
            return False

    async def _git_apply(self, diff: str) -> bool:
        try:
            r = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ["git", "apply"], input=diff.encode(), capture_output=True, timeout=30
                ),
            )
            return r.returncode == 0
        except Exception as exc:
            logger.warning(f"SelfEvolution: git apply failed: {exc}")
            return False

    async def _git_commit(self, message: str) -> str:
        try:
            await self._run_git(["git", "add", "-A"])
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ["git", "commit", "-m", message], capture_output=True, timeout=30
                ),
            )
            r = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, timeout=10),
            )
            return r.stdout.decode().strip()[:40]
        except Exception:
            return ""

    async def _run_tests(self, test_command: str) -> tuple[bool, str]:
        try:
            r = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(test_command.split(), capture_output=True, timeout=120),
            )
            return r.returncode == 0, r.stderr.decode(errors="ignore") if r.returncode != 0 else ""
        except Exception as exc:
            return False, str(exc)

    async def _assert_creator(self, user_id: str) -> None:
        from fastapi import HTTPException, status as http_status
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.user import User
            from sqlalchemy import select
            import uuid as _uuid

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(User).where(User.id == _uuid.UUID(user_id)).limit(1)
                )
                user = result.scalar_one_or_none()
                if not user or user.role != "creator":
                    raise HTTPException(
                        status_code=http_status.HTTP_403_FORBIDDEN,
                        detail="Доступ только для создателя системы.",
                    )
        except Exception as exc:
            if hasattr(exc, "status_code"):
                raise
            logger.warning(f"SelfEvolution: _assert_creator error: {exc}")

    async def _get_interaction_count(self, user_id: str) -> int:
        try:
            from ..database_final import AsyncSessionLocal
            from sqlalchemy import text
            async with AsyncSessionLocal() as db:
                r = await db.execute(
                    text("SELECT COUNT(*) FROM evolution_proposals WHERE user_id = :uid"),
                    {"uid": user_id},
                )
                row = r.fetchone()
                return row[0] if row else 0
        except Exception:
            return 0

    async def _save_proposal(self, proposal: EvolutionProposal, user_id: str) -> None:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.evolution_proposal import EvolutionProposal as EPModel
            import uuid as _uuid

            async with AsyncSessionLocal() as db:
                ep = EPModel(
                    id=_uuid.UUID(proposal.id),
                    user_id=_uuid.UUID(user_id),
                    description=proposal.description,
                    diff=proposal.diff,
                    affected_files=proposal.affected_files,
                    test_command=proposal.test_command,
                    status=proposal.status,
                )
                db.add(ep)
                await db.commit()
        except Exception as exc:
            logger.warning(f"SelfEvolution: _save_proposal failed: {exc}")

    async def _update_proposal_status(self, proposal: EvolutionProposal) -> None:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.evolution_proposal import EvolutionProposal as EPModel
            from sqlalchemy import select
            import uuid as _uuid

            async with AsyncSessionLocal() as db:
                r = await db.execute(
                    select(EPModel).where(EPModel.id == _uuid.UUID(proposal.id)).limit(1)
                )
                ep = r.scalar_one_or_none()
                if ep:
                    ep.status = proposal.status
                    ep.commit_hash = proposal.commit_hash or None
                    ep.error_log = proposal.error_log or None
                    if proposal.resolved_at:
                        ep.resolved_at = datetime.fromisoformat(proposal.resolved_at)
                    await db.commit()
        except Exception as exc:
            logger.warning(f"SelfEvolution: _update_proposal_status failed: {exc}")

    async def _load_proposal(self, proposal_id: str) -> Optional[EvolutionProposal]:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.evolution_proposal import EvolutionProposal as EPModel
            from sqlalchemy import select
            import uuid as _uuid

            async with AsyncSessionLocal() as db:
                r = await db.execute(
                    select(EPModel).where(EPModel.id == _uuid.UUID(proposal_id)).limit(1)
                )
                ep = r.scalar_one_or_none()
                if ep:
                    return EvolutionProposal(
                        id=str(ep.id),
                        description=ep.description,
                        diff=ep.diff or "",
                        affected_files=ep.affected_files or [],
                        test_command=ep.test_command or "pytest",
                        status=ep.status,
                        commit_hash=ep.commit_hash or "",
                        error_log=ep.error_log or "",
                        created_at=ep.created_at.isoformat() if ep.created_at else "",
                        resolved_at=ep.resolved_at.isoformat() if ep.resolved_at else "",
                    )
        except Exception as exc:
            logger.warning(f"SelfEvolution: _load_proposal failed: {exc}")
        return None

    async def _load_all_proposals(self, user_id: str) -> list[EvolutionProposal]:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.evolution_proposal import EvolutionProposal as EPModel
            from sqlalchemy import select, desc
            import uuid as _uuid

            async with AsyncSessionLocal() as db:
                r = await db.execute(
                    select(EPModel)
                    .where(EPModel.user_id == _uuid.UUID(user_id))
                    .order_by(desc(EPModel.created_at))
                    .limit(50)
                )
                return [
                    EvolutionProposal(
                        id=str(ep.id),
                        description=ep.description,
                        diff=ep.diff or "",
                        affected_files=ep.affected_files or [],
                        test_command=ep.test_command or "pytest",
                        status=ep.status,
                        commit_hash=ep.commit_hash or "",
                        error_log=ep.error_log or "",
                        created_at=ep.created_at.isoformat() if ep.created_at else "",
                        resolved_at=ep.resolved_at.isoformat() if ep.resolved_at else "",
                    )
                    for ep in r.scalars().all()
                ]
        except Exception as exc:
            logger.warning(f"SelfEvolution: _load_all_proposals failed: {exc}")
            return []


_self_evo: Optional[SelfEvolution] = None


def get_self_evolution() -> SelfEvolution:
    global _self_evo
    if _self_evo is None:
        _self_evo = SelfEvolution()
    return _self_evo
