"""Parser module for the frontend of the compiler."""

from eryx.frontend.ast import (
    ArrayLiteral,
    AssertStatement,
    AssignmentExpression,
    BinaryExpression,
    BreakLiteral,
    CallExpression,
    ClassDeclaration,
    ContinueLiteral,
    DelStatement,
    EnumDeclaration,
    Expression,
    ForStatement,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    ImportStatement,
    LoopStatement,
    MemberExpression,
    NumericLiteral,
    ObjectLiteral,
    Program,
    Property,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
    WhileStatement,
)
from eryx.frontend.lexer import Token, TokenType, tokenize
from eryx.utils.errors import syntax_error

# Precedence:
# 1. Member expression: obj.prop, obj[expr]
# 2. Call expression: func(), obj.method()
# 3. Exponentiation: **
# 4. Multiplication, division, modulo: *, /, %
# 5. Addition, subtraction: +, -
# 6. Bitwise operations: <<, >>, &, |, ^
# 7. Logical AND and OR: &&, ||
# 8. Comparison: ==, !=, >, >=, <, <=
# 9. Assignment: =


class Parser:
    """Parser class."""

    def __init__(self) -> None:
        self.source_code = ""
        self.tokens = []

    def not_eof(self) -> bool:
        """Check if the parser has not reached the end of the token stream."""
        return self.tokens[0].type != TokenType.EOF

    def at(self) -> Token:
        """Get the current token."""
        return self.tokens[0]

    def next(self) -> Token:
        """Get the current token and skip to next one (also called eat)."""
        return self.tokens.pop(0)

    def look_ahead(self, n: int) -> Token:
        """Look ahead n tokens."""
        return self.tokens[n]

    def assert_next(self, token_type: TokenType, error: str) -> Token:
        """Return the current token and assert that the next token is of a certain type."""
        token = self.next()
        if token.type != token_type:
            syntax_error(self.source_code, token.position, error)
        return token

    def parse_additive_expression(self) -> Expression:
        """Parse an additive expression."""
        left = self.parse_multiplicative_expression()

        while self.at().value in ("+", "-"):
            operator = self.next().value
            right = self.parse_multiplicative_expression()
            left = BinaryExpression(left.position, left, operator, right)

        return left

    def parse_call_member_expression(self) -> Expression:
        """Parse a call member expression."""
        member = self.parse_member_expression()

        if self.at().type == TokenType.OPEN_PAREN:
            return self.parse_call_expression(member)

        return member

    def parse_call_expression(self, caller: Expression) -> Expression:
        """Parse a call expression."""
        call_expression = CallExpression(
            caller.position, self.parse_arguments(), caller
        )

        if self.at().type == TokenType.OPEN_PAREN:
            call_expression = self.parse_call_expression(call_expression)

        return call_expression

    def parse_arguments(self) -> list[Expression]:
        """Parse arguments."""
        self.assert_next(TokenType.OPEN_PAREN, "Expected an open parenthesis.")

        arguments = (
            []
            if self.at().type == TokenType.CLOSE_PAREN
            else self.parse_arguments_list()
        )

        self.assert_next(TokenType.CLOSE_PAREN, "Expected a closing parenthesis.")

        return arguments

    def parse_arguments_list(self) -> list[Expression]:
        """Parse an arguments list."""
        arguments = [self.parse_assignment_expression()]

        while self.not_eof() and self.at().type in (TokenType.COMMA, TokenType.COLON):
            skipped = self.next()  # Skip the comma / colon

            if skipped.type == TokenType.COLON:  # Handle type hinting
                self.next()  # Skip the type hint
                continue

            value = self.parse_assignment_expression()

            arguments.append(value)

        return arguments

    def parse_member_expression(self) -> Expression:
        """Parse a member expression."""
        obj = self.parse_primary_expression()

        while self.at().type in (TokenType.OPEN_BRACKET, TokenType.DOT):
            operator = self.next()
            proprty = None
            computed = False

            if operator.type == TokenType.DOT:
                proprty = self.parse_primary_expression()  # Identifier

                if not isinstance(proprty, Identifier):
                    syntax_error(
                        self.source_code,
                        self.at().position,
                        "Expected an identifier as a property.",
                    )
            else:
                computed = True
                proprty = self.parse_expression()
                self.assert_next(TokenType.CLOSE_BRACKET, "Expected a closing bracket.")

            obj = MemberExpression(obj.position, obj, proprty, computed)

        return obj

    def parse_multiplicative_expression(self) -> Expression:
        """Parse a multiplicative expression."""
        left = self.parse_exponentiation_expression()

        while self.at().value in ("/", "*", "%"):
            operator = self.next().value
            right = self.parse_exponentiation_expression()
            left = BinaryExpression(left.position, left, operator, right)

        return left

    def parse_exponentiation_expression(self) -> Expression:
        """Parse an exponentiation expression."""
        left = self.parse_call_member_expression()

        while self.at().value == "**":
            operator = self.next().value
            right = self.parse_call_member_expression()
            left = BinaryExpression(left.position, left, operator, right)

        return left

    def parse_array_expression(self) -> Expression:
        """Parse an array expression."""
        start_token = self.assert_next(
            TokenType.OPEN_BRACKET, "Expected an opening bracket '[' for array."
        )

        elements = []
        # Check for empty arrays
        if self.at().type != TokenType.CLOSE_BRACKET:
            elements.append(self.parse_expression())

            while self.at().type == TokenType.COMMA:
                self.next()  # Skip the comma
                elements.append(self.parse_expression())

        self.assert_next(
            TokenType.CLOSE_BRACKET, "Expected a closing bracket ']' for array."
        )
        return ArrayLiteral(start_token.position, elements)

    def parse_primary_expression(self) -> Expression:
        """Parse a primary expression."""
        token = self.at()

        match token.type:
            case TokenType.IDENTIFIER:
                return Identifier(token.position, self.next().value)
            case TokenType.NUMBER:
                return NumericLiteral(token.position, float(self.next().value))
            case TokenType.STRING:
                return StringLiteral(token.position, self.next().value)
            case TokenType.BREAK:
                new_token = self.next()
                return BreakLiteral(new_token.position)
            case TokenType.CONTINUE:
                new_token = self.next()
                return ContinueLiteral(new_token.position)
            case TokenType.BINARY_OPERATOR:
                if token.value in ("++", "--"):
                    self.next()  # Skip the operator
                    if self.at().type == TokenType.IDENTIFIER:
                        return AssignmentExpression(
                            self.at().position,
                            Identifier(self.at().position, self.next().value),
                            NumericLiteral(self.at().position, 1),
                            token.value[0] + "=",
                        )
                syntax_error(
                    self.source_code,
                    token.position,
                    "Unexpected binary operator found.",
                )
                return Expression(token.position)  # This will never be reached
            case TokenType.OPEN_BRACKET:
                return self.parse_array_expression()
            case TokenType.OPEN_BRACE:
                return self.parse_object_expression()
            case TokenType.OPEN_PAREN:
                self.next()  # Skip the open parenthesis
                expression = self.parse_expression()
                self.assert_next(
                    TokenType.CLOSE_PAREN,
                    "Unexpected token found inside parenthesised expression, "
                    "expected closing parenthesis.",
                )  # Skip the close parenthesis
                return expression
            case TokenType.SEMICOLON:
                self.next()  # Skip the semicolon
                return Expression((0, 0, 0))
            case _:
                syntax_error(
                    self.source_code, token.position, f"Unexpected token. {token}"
                )
                return Expression((0, 0, 0))  # This will never be reached

    def parse_assignment_expression(self) -> Expression:
        """Parse an assignment expression."""
        left = self.parse_comparison_expression()

        if self.at().type == TokenType.COLON:  # Handle type hinting
            self.next()  # Skip the colon
            self.next()  # Skip the type hint

        if (
            self.at().type == TokenType.EQUALS
            and self.look_ahead(1).type != TokenType.EQUALS
        ):
            self.next()  # Skip the equals sign

            value = self.parse_assignment_expression()
            return AssignmentExpression(left.position, left, value)

        if self.at().type == TokenType.ASSIGNMENT_OPERATOR:
            operator = self.next().value
            value = self.parse_assignment_expression()
            return AssignmentExpression(left.position, left, value, operator)

        return left

    def parse_expression(self) -> Expression:
        """Parse an expression."""
        return self.parse_assignment_expression()

    def parse_object_expression(self) -> Expression:
        """Parse an object expression."""

        start_token = self.next()  # Skip the open brace

        properties = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            key = self.assert_next(
                TokenType.IDENTIFIER, "Expected an identifier as a key."
            )

            if self.at().type == TokenType.COMMA:
                self.next()  # Skip the comma
                properties.append(Property(self.at().position, key.value))
                continue

            if self.at().type == TokenType.CLOSE_BRACE:
                properties.append(Property(self.at().position, key.value))
                continue

            self.assert_next(TokenType.COLON, "Expected a colon after the key.")

            value = self.parse_expression()
            properties.append(Property(self.at().position, key.value, value))

            if self.at().type != TokenType.CLOSE_BRACE:
                self.assert_next(
                    TokenType.COMMA,
                    "Expected a comma or closing brace after the value.",
                )

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected a closing brace after the object."
        )
        return ObjectLiteral(start_token.position, properties)

    def parse_comparison_expression(self) -> Expression:
        """Parse a comparison expression."""
        left = self.parse_logical_expression()

        while self.at().value in ("==", "!=", ">", ">=", "<", "<="):
            operator = self.next().value
            right = self.parse_logical_expression()
            left = BinaryExpression(left.position, left, operator, right)

        return left

    def parse_bitwise_expression(self) -> Expression:
        """Parse a bitwise expression."""
        left = self.parse_additive_expression()

        while self.at().value in ("&", "|", "^", "<<", ">>"):
            operator = self.next().value
            right = self.parse_additive_expression()
            left = BinaryExpression(left.position, left, operator, right)

        return left

    def parse_logical_expression(self) -> Expression:
        """Parse a logical expression."""
        left = self.parse_bitwise_expression()

        while self.at().value in ("&&", "||"):
            operator = self.next().value
            right = self.parse_bitwise_expression()
            left = BinaryExpression(left.position, left, operator, right)

        return left

    def parse_assert_statement(self) -> Statement:
        """Parse an assert statement."""
        self.next()  # Skip the assert keyword

        condition = self.parse_expression()

        if self.at().type == TokenType.COMMA:
            self.next()  # Skip the comma

            message = self.parse_expression()

            if isinstance(message, StringLiteral):
                return AssertStatement(condition.position, condition, message.value)

            syntax_error(
                self.source_code,
                self.at().position,
                "Assert message must be a string.",
            )

        self.assert_next(TokenType.SEMICOLON, "Expected a semicolon after the assert.")

        return AssertStatement(condition.position, condition)

    def parse_if_statement(self) -> Statement:
        """Parse an if statement."""
        start_token = self.next()  # Skip the if keyword
        self.assert_next(
            TokenType.OPEN_PAREN,
            "Expected an opening parenthesis for the if condition.",
        )

        condition = self.parse_expression()

        self.assert_next(
            TokenType.CLOSE_PAREN,
            "Expected a closing parenthesis after the if condition.",
        )

        self.assert_next(
            TokenType.OPEN_BRACE, "Expected an opening brace for the if body."
        )

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                body.append(statement)

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected a closing brace after the if body."
        )

        if self.at().type == TokenType.ELSE:
            self.next()
            self.assert_next(
                TokenType.OPEN_BRACE, "Expected an opening brace for the else body."
            )

            else_body = []
            while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
                statement = self.parse_statement()
                if statement != Expression((0, 0, 0)):
                    else_body.append(statement)

            self.assert_next(
                TokenType.CLOSE_BRACE, "Expected a closing brace after the else body."
            )

            return IfStatement(
                start_token.position, condition, then=body, else_=else_body
            )

        return IfStatement(start_token.position, condition, then=body)

    def parse_return_statement(self) -> Statement:
        """Parse a return statement."""
        start_token = self.next()  # Skip the return keyword

        if self.at().type == TokenType.SEMICOLON:
            self.next()
            return ReturnStatement(start_token.position)

        value = self.parse_expression()

        self.assert_next(TokenType.SEMICOLON, "Expected a semicolon after the return.")

        return ReturnStatement(start_token.position, value)

    def parse_function_declaration(self) -> Statement:
        """Parse a function declaration."""
        start_token = self.next()  # Skip the func keyword

        name = self.assert_next(
            TokenType.IDENTIFIER,
            "Expected an function name after the function keyword.",
        ).value
        arguments = self.parse_arguments()

        parameters = []
        for argument in arguments:
            if isinstance(argument, Identifier):
                parameters.append(argument.symbol)
            else:
                syntax_error(
                    self.source_code,
                    self.at().position,
                    "Function arguments must be identifiers.",
                )

        self.assert_next(TokenType.OPEN_BRACE, "Expected an opening brace.")

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                body.append(statement)

        self.assert_next(
            TokenType.CLOSE_BRACE,
            "Expected a closing brace after the function body.",
        )

        return FunctionDeclaration(start_token.position, name, parameters, body)

    def parse_enum_declaration(self) -> Statement:
        """Parse an enum declaration."""
        start_token = self.next()  # Skip the enum declaration

        name = self.assert_next(
            TokenType.IDENTIFIER,
            "Expected a class name after the class keyword.",
        ).value

        self.assert_next(
            TokenType.OPEN_BRACE,
            "Expected an opening brace for the class body.",
        )

        values = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                if isinstance(statement, Identifier):
                    values.append(Identifier(statement.position, statement.symbol))
                else:
                    syntax_error(
                        self.source_code,
                        self.at().position,
                        "Invalid statement in enum body.",
                    )

        self.assert_next(
            TokenType.CLOSE_BRACE,
            "Expected a closing brace after the class body.",
        )

        return EnumDeclaration(start_token.position, name, values)

    def parse_class_declaration(self) -> Statement:
        """Parse a class declaration."""
        start_token = self.next()  # Skip the class keyword

        name = self.assert_next(
            TokenType.IDENTIFIER,
            "Expected a class name after the class keyword.",
        ).value

        self.assert_next(
            TokenType.OPEN_BRACE,
            "Expected an opening brace for the class body.",
        )

        body = []
        parameters = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                if isinstance(statement, AssignmentExpression):
                    body.append(statement)
                elif isinstance(statement, FunctionDeclaration):
                    body.append(statement)
                elif isinstance(statement, Identifier):
                    parameters.append(statement.symbol)
                else:
                    syntax_error(
                        self.source_code,
                        self.at().position,
                        "Invalid statement in class body.",
                    )

        self.assert_next(
            TokenType.CLOSE_BRACE,
            "Expected a closing brace after the class body.",
        )

        return ClassDeclaration(start_token.position, name, body, parameters)

    def parse_variable_declaration(self) -> Statement:
        """Parse a variable declaration."""
        start_token = self.at()
        is_constant = self.next().type == TokenType.CONST
        identifier = self.assert_next(
            TokenType.IDENTIFIER, "Expected an identifier after a declaration."
        )

        if self.at().type == TokenType.SEMICOLON:
            self.next()  # Skip the semicolon
            if is_constant:
                syntax_error(
                    self.source_code,
                    self.at().position,
                    "Constant declaration must have an initial value.",
                )

            return VariableDeclaration(
                start_token.position,
                is_constant,
                Identifier(identifier.position, identifier.value),
            )

        self.assert_next(
            TokenType.EQUALS, "Expected an equals sign after the identifier."
        )

        declaration = VariableDeclaration(
            start_token.position,
            is_constant,
            Identifier(identifier.position, identifier.value),
            self.parse_expression(),
        )

        self.assert_next(
            TokenType.SEMICOLON, "Expected a semicolon after the declaration."
        )

        return declaration

    def parse_import_statement(self) -> Statement:
        """Parse an import statement."""
        start_token = self.next()  # Skip the import keyword

        value = self.assert_next(
            TokenType.STRING, "Expected a string after the import keyword."
        )

        if self.at().type == TokenType.AS:
            self.next()  # Skip the as keyword

            alias = self.assert_next(
                TokenType.STRING, "Expected a string for the import alias."
            )

            return ImportStatement(start_token.position, value.value, alias=alias.value)

        return ImportStatement(start_token.position, value.value)

    def parse_from_statement(self) -> Statement:
        """Parse a from statement."""
        start_token = self.next()  # Skip the from keyword

        from_value = self.assert_next(
            TokenType.STRING, "Expected a string after the from keyword."
        )

        if not self.at().type == TokenType.IMPORT:
            syntax_error(
                self.source_code,
                self.at().position,
                "Expected an import keyword after the from keyword.",
            )

        self.next()  # Skip the import keyword

        import_value = self.parse_array_expression()

        if not isinstance(import_value, ArrayLiteral):
            syntax_error(
                self.source_code,
                self.at().position,
                "Import properties must be an array.",
            )
            return ImportStatement(
                start_token.position, from_value.value, None
            )  # Type checker stuff, will never happen

        if not import_value.elements:
            syntax_error(
                self.source_code,
                self.at().position,
                "Import properties must not be empty.",
            )

        if not all(isinstance(item, StringLiteral) for item in import_value.elements):
            syntax_error(
                self.source_code,
                self.at().position,
                "Import properties must be strings.",
            )

        return ImportStatement(
            start_token.position,
            from_value.value,
            [
                item.value
                for item in import_value.elements
                if isinstance(item, StringLiteral)
            ],
        )

    def parse_loop_statement(self) -> Statement:
        """Parse a loop statement."""
        start_token = self.next()  # Skip the loop keyword

        self.assert_next(
            TokenType.OPEN_BRACE, "Expected opening brace for the loop statement."
        )

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                body.append(statement)

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected closing brace for the loop statement."
        )

        return LoopStatement(start_token.position, body)

    def parse_for_statement(self) -> Statement:
        """Parse a for statement."""
        start_token = self.next()  # Skip the for keyword

        variable = self.assert_next(
            TokenType.IDENTIFIER, "Expected an identifier for the loop variable."
        )

        self.assert_next(TokenType.IN, "Expected the 'in' keyword for the for loop.")

        iterator = self.parse_expression()

        self.assert_next(
            TokenType.OPEN_BRACE, "Expected opening brace for the for statement."
        )

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                body.append(statement)

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected closing brace for the for statement."
        )

        return ForStatement(
            start_token.position,
            Identifier(variable.position, variable.value),
            iterator,
            body,
        )

    def parse_del_statement(self) -> Statement:
        """Parse a del statement."""
        start_token = self.next()  # Skip the del keyword

        variable = self.assert_next(
            TokenType.IDENTIFIER, "Expected an identifier after the del keyword."
        )

        return DelStatement(
            start_token.position, Identifier(variable.position, variable.value)
        )

    def parse_while_statement(self) -> Statement:
        """Parse a while statement."""
        start_token = self.next()  # Skip the while keyword

        self.assert_next(
            TokenType.OPEN_PAREN,
            "Expected an opening parenthesis for the while condition.",
        )

        condition = self.parse_expression()

        self.assert_next(
            TokenType.CLOSE_PAREN,
            "Expected a closing parenthesis after the while condition.",
        )

        self.assert_next(
            TokenType.OPEN_BRACE, "Expected opening brace for the while statement."
        )

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                body.append(statement)

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected closing brace for the while statement."
        )

        return WhileStatement(start_token.position, condition, body)

    def parse_statement(self) -> Statement:
        """Parse a statement."""
        match self.at().type:
            case TokenType.LET:
                return self.parse_variable_declaration()
            case TokenType.CONST:
                return self.parse_variable_declaration()
            case TokenType.FUNC:
                return self.parse_function_declaration()
            case TokenType.IF:
                return self.parse_if_statement()
            case TokenType.ASSERT:
                return self.parse_assert_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case TokenType.IMPORT:
                return self.parse_import_statement()
            case TokenType.FROM:
                return self.parse_from_statement()
            case TokenType.WHILE:
                return self.parse_while_statement()
            case TokenType.LOOP:
                return self.parse_loop_statement()
            case TokenType.FOR:
                return self.parse_for_statement()
            case TokenType.DEL:
                return self.parse_del_statement()
            case TokenType.CLASS:
                return self.parse_class_declaration()
            case TokenType.ENUM:
                return self.parse_enum_declaration()
            case _:
                return self.parse_expression()

    def produce_ast(self, source_code: str) -> Program:
        """Produce an abstract syntax tree (AST) from source code."""
        self.source_code = source_code
        self.tokens = tokenize(source_code)
        program = Program((0, 0, 0), body=[])

        # Parse all statements in the program until the EOF
        while self.not_eof():
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                program.body.append(statement)

        return program
