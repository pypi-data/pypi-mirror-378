"""Abstract syntax tree (AST) for the frontend."""

from dataclasses import dataclass, field
from typing import List, Union


@dataclass()
class Statement:
    """Base class for all statements in the AST."""

    position: tuple[int, int, int]


@dataclass()
class Program(Statement):
    """Program class."""

    body: List[Statement]


@dataclass()
class Expression(Statement):
    """Expression base class."""


@dataclass()
class AssignmentExpression(Expression):
    """Assignment expression class."""

    assigne: Expression
    value: Expression
    operator: str | None = None


@dataclass()
class BinaryExpression(Expression):
    """Binary expression class."""

    left: Expression
    operator: str
    right: Expression


@dataclass()
class Identifier(Expression):
    """Identifier class."""

    symbol: str


@dataclass()
class VariableDeclaration(Statement):
    """Variable declaration class."""

    constant: bool
    identifier: Identifier
    value: Union[Expression, None] = None


@dataclass()
class NumericLiteral(Expression):
    """Numeric literal class."""

    value: float


@dataclass()
class StringLiteral(Expression):
    """String literal class."""

    value: str


@dataclass()
class Property(Expression):
    """Property class."""

    key: str
    value: Union[Expression, None] = None


@dataclass()
class ObjectLiteral(Expression):
    """Object literal class."""

    properties: List[Property]


@dataclass()
class ArrayLiteral(Expression):
    """Represents an array literal."""

    elements: List[Expression]


@dataclass()
class CallExpression(Expression):
    """Binary expression class."""

    arguments: List[Expression]
    caller: Expression


@dataclass()
class MemberExpression(Expression):
    """Binary expression class."""

    object: Expression
    property: Expression
    computed: bool


@dataclass()
class FunctionDeclaration(Statement):
    """Function declaration class."""

    name: str
    arguments: List[str]
    body: list[Statement]


@dataclass()
class IfStatement(Statement):
    """If statement class."""

    condition: Expression
    then: list[Statement]
    else_: list[Union[Statement, None]] = field(default_factory=list)


@dataclass()
class ReturnStatement(Statement):
    """Return statement class."""

    value: Union[Expression, None] = None


@dataclass()
class ImportStatement(Statement):
    """Import statement class."""

    module: str
    names: List[str] | None = None
    alias: str | None = None


@dataclass()
class LoopStatement(Statement):
    """Loop statement class."""

    body: list[Statement]


@dataclass()
class WhileStatement(Statement):
    """While statement class."""

    condition: Expression
    body: list[Statement]


@dataclass()
class ForStatement(Statement):
    """For statement class."""

    variable: Expression
    iterator: Expression
    body: list[Statement]


@dataclass()
class BreakLiteral(Expression):
    """Break literal class."""


@dataclass()
class DelStatement(Statement):
    """Del statement class."""

    identifier: Expression


@dataclass()
class ContinueLiteral(Expression):
    """Continue literal class."""


@dataclass()
class ClassDeclaration(Statement):
    """Class declaration class."""

    name: str
    methods: list[FunctionDeclaration | VariableDeclaration | Identifier]
    arguments: List[str] | None = None


@dataclass()
class EnumDeclaration(Statement):
    """Enum declaration class."""

    name: str
    values: list[Identifier]


@dataclass()
class AssertStatement(Statement):
    """Assert statement class."""

    condition: Expression
    message: str | None = None
