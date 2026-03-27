import ast
import logging
from typing import List, Dict, Any

logger = logging.getLogger("jarvis-code-review")

class JARVISCodeReviewer:
    """Модуль автономного ревью кода (Stage 15)"""
    
    def __init__(self, personality):
        self.personality = personality

    async def review_code(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Анализ кода на наличие антипаттернов и уязвимостей"""
        logger.info(f"🧐 JARVIS reviewing: {file_path}")
        findings = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # 1. Поиск паролей и секретов в коде
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id.lower()
                            if any(secret in name for secret in ["password", "secret", "key", "token"]):
                                findings.append({
                                    "line": node.lineno,
                                    "severity": "critical",
                                    "message": "Сэр, вы храните секреты в открытом виде. Это даже для вас слишком беспечно.",
                                    "type": "security"
                                })

                # 2. Проверка на пустые блоки except
                if isinstance(node, ast.ExceptHandler):
                    if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                        findings.append({
                            "line": node.lineno,
                            "severity": "medium",
                            "message": "Пустой блок 'except'? Вы решили, что ошибки исчезнут сами по себе?",
                            "type": "code_quality"
                        })

                # 3. Слишком длинные функции
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 50:
                        findings.append({
                            "line": node.lineno,
                            "severity": "low",
                            "message": f"Функция '{node.name}' слишком длинная. Мой процессор вскипит, пока дочитает её до конца.",
                            "type": "refactor"
                        })

        except SyntaxError as e:
            findings.append({
                "line": e.lineno,
                "severity": "critical",
                "message": f"Сэр, у вас тут синтаксическая ошибка. Даже я не могу это прочитать: {e.msg}",
                "type": "syntax"
            })

        return findings

    async def generate_review_report(self, findings: List[Dict[str, Any]]) -> str:
        """Генерация итогового отчета в стиле JARVIS"""
        if not findings:
            return "Код безупречен, сэр. Я почти завидую вашему мастерству."
            
        summary = f"Сэр, я провел аудит. Найдено {len(findings)} замечаний. "
        critical = len([f for f in findings if f["severity"] == "critical"])
        
        if critical > 0:
            summary += f"Из них {critical} критических. Я бы на вашем месте это не запускал."
        else:
            summary += "Ничего смертельного, но есть над чем поработать."
            
        return summary
