from typing import List, Optional, Type

from sqlalchemy.sql.expression import ClauseElement, Select

from odata_query.grammar import ODataLexer, ODataParser  # type: ignore

from .core import AstToSqlAlchemyCoreVisitor
from .orm import AstToSqlAlchemyOrmVisitor


def _get_joined_attrs(query: Select) -> List[str]:
    return [str(join[0]) for join in query._setup_joins]


def _get_model(query: ClauseElement, model: Optional[Type] = None) -> type:
    if model is not None:
        return model
    return query.columns_clause_froms[0].entity_namespace


def apply_odata_query(
    query: ClauseElement,
    odata_query: str,
    model: Optional[Type] = None,
) -> ClauseElement:
    """
    Shorthand for applying an OData query to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query to apply the OData query to.
        odata_query: OData query string.
    Returns:
        ClauseElement: The modified query
    """
    lexer = ODataLexer()
    parser = ODataParser()

    model = _get_model(query, model)

    ast = parser.parse(lexer.tokenize(odata_query))
    transformer = AstToSqlAlchemyOrmVisitor(model)
    where_clause = transformer.visit(ast)

    existing_joins = _get_joined_attrs(query)
    for required_join in transformer.join_relationships:
        if (
            str(required_join) not in existing_joins
            and str(required_join.key) not in existing_joins
        ):
            query = query.join(required_join)

    return query.filter(where_clause)


def apply_odata_core(query: ClauseElement, odata_query: str) -> ClauseElement:
    """
    Shorthand for applying an OData query to a SQLAlchemy core.

    Args:
        query: SQLAlchemy query to apply the OData query to.
        odata_query: OData query string.
    Returns:
        ClauseElement: The modified query
    """
    lexer = ODataLexer()
    parser = ODataParser()
    table = query.columns_clause_froms[0]

    ast = parser.parse(lexer.tokenize(odata_query))
    transformer = AstToSqlAlchemyCoreVisitor(table)
    where_clause = transformer.visit(ast)
    return query.filter(where_clause)
