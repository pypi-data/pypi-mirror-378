import enum
from dataclasses import dataclass, field
from typing import List

from pylasu.model import Position, Node


class IssueType(enum.Enum):
    LEXICAL = 0
    SYNTACTIC = 1
    SEMANTIC = 2


class IssueSeverity(enum.Enum):
    ERROR = 30
    WARNING = 20
    INFO = 10


@dataclass
class Issue:
    type: IssueType
    message: str
    severity: IssueSeverity = IssueSeverity.ERROR
    position: Position = None

    def __str__(self):
        msg = f"{self.severity.name.capitalize()} ({self.type.name.lower()}): {self.message}"
        if self.position:
            msg += f" @ {self.position}"
        return msg

    @staticmethod
    def lexical(message: str, severity: IssueSeverity = IssueSeverity.ERROR, position: Position = None):
        return Issue(IssueType.LEXICAL, message, severity, position)

    @staticmethod
    def syntactic(message: str, severity: IssueSeverity = IssueSeverity.ERROR, position: Position = None):
        return Issue(IssueType.SYNTACTIC, message, severity, position)

    @staticmethod
    def semantic(message: str, severity: IssueSeverity = IssueSeverity.ERROR, position: Position = None):
        return Issue(IssueType.SEMANTIC, message, severity, position)


@dataclass
class WithIssues:
    """Many classes have the necessity of tracking issues"""
    issues: List[Issue] = field(default_factory=list, init=False)


@dataclass
class Result(WithIssues):
    root: Node
