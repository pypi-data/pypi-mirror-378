from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypeAlias

from .._constant import ScalarConstant
from .._graphql import (
    DatabaseRestrictionFragmentConditionDatabaseRestrictionMembershipCondition,
    DatabaseRestrictionFragmentConditionDatabaseRestrictionRelationalCondition,
    DatabaseRestrictionLeafConditionInput,
    DatabaseRestrictionMembershipConditionInput,
    DatabaseRestrictionMembershipConditionOperator as GraphqlDatabaseRestrictionMembershipConditionOperator,
    DatabaseRestrictionRelationalConditionInput,
    DatabaseRestrictionRelationalConditionOperator as GraphqlDatabaseRestrictionRelationalConditionOperator,
)
from .._identification import ColumnIdentifier
from .._operation import (
    LogicalCondition,
    MembershipCondition,
    RelationalCondition,
    condition_from_dnf,
    dnf_from_condition,
)

DatabaseRestrictionMembershipConditionOperator: TypeAlias = Literal["IN"]
DatabaseRestrictionRelationalConditionOperator: TypeAlias = Literal["EQ"]
DatabaseRestrictionLeafCondition: TypeAlias = (
    MembershipCondition[
        ColumnIdentifier, DatabaseRestrictionMembershipConditionOperator, ScalarConstant
    ]
    | RelationalCondition[
        ColumnIdentifier, DatabaseRestrictionRelationalConditionOperator, ScalarConstant
    ]
)
DatabaseRestrictionLogicalConditionOperator: TypeAlias = Literal["AND"]
DatabaseRestrictionLogicalCondition: TypeAlias = LogicalCondition[
    DatabaseRestrictionLeafCondition, DatabaseRestrictionLogicalConditionOperator
]
DatabaseRestrictionCondition: TypeAlias = (
    DatabaseRestrictionLeafCondition | DatabaseRestrictionLogicalCondition
)


_GraphQLDatabaseLeafCondition: TypeAlias = (
    DatabaseRestrictionFragmentConditionDatabaseRestrictionMembershipCondition
    | DatabaseRestrictionFragmentConditionDatabaseRestrictionRelationalCondition
)


def _leaf_condition_from_graphql(
    condition: _GraphQLDatabaseLeafCondition, /
) -> DatabaseRestrictionLeafCondition:
    match condition:
        case DatabaseRestrictionFragmentConditionDatabaseRestrictionMembershipCondition(
            subject=subject,
            membership_operator=operator,
            elements=elements,
        ):
            match operator.value:
                case "IN":
                    membership_operator: DatabaseRestrictionMembershipConditionOperator = "IN"

            return MembershipCondition.of(
                subject=ColumnIdentifier._from_graphql(subject),
                operator=membership_operator,
                elements=set(elements),
            )
        case DatabaseRestrictionFragmentConditionDatabaseRestrictionRelationalCondition(
            subject=subject,
            relational_operator=operator,
            target=target,
        ):
            match operator.value:
                case "EQ":
                    relational_operator: DatabaseRestrictionRelationalConditionOperator = "EQ"

            return RelationalCondition(
                subject=ColumnIdentifier._from_graphql(subject),
                operator=relational_operator,
                target=target,
            )


def database_restriction_condition_from_graphql(
    dnf: Sequence[Sequence[_GraphQLDatabaseLeafCondition]], /
) -> DatabaseRestrictionCondition:
    match dnf:
        case [graphql_conjunct_conditions]:
            conjunct_conditions = [
                _leaf_condition_from_graphql(condition)
                for condition in graphql_conjunct_conditions
            ]
            return condition_from_dnf((conjunct_conditions,))
        case _:
            raise AssertionError(f"Unexpected disjunctive normal form: {dnf}.")


def _leaf_condition_to_graphql(
    condition: DatabaseRestrictionLeafCondition, /
) -> DatabaseRestrictionLeafConditionInput:
    match condition:
        case MembershipCondition(subject=subject, operator=operator, elements=elements):
            match operator:
                case "IN":
                    membership_operator: GraphqlDatabaseRestrictionMembershipConditionOperator = GraphqlDatabaseRestrictionMembershipConditionOperator.IN

            return DatabaseRestrictionLeafConditionInput(
                membership=DatabaseRestrictionMembershipConditionInput(
                    subject=subject._to_graphql(),
                    operator=membership_operator,
                    elements=list(elements),
                )
            )
        case RelationalCondition(subject=subject, operator=operator, target=target):
            match operator:
                case "EQ":
                    relational_operator: GraphqlDatabaseRestrictionRelationalConditionOperator = GraphqlDatabaseRestrictionRelationalConditionOperator.EQ

            return DatabaseRestrictionLeafConditionInput(
                relational=DatabaseRestrictionRelationalConditionInput(
                    subject=subject._to_graphql(),
                    operator=relational_operator,
                    target=target,
                )
            )


def database_restriction_condition_to_graphql(
    condition: DatabaseRestrictionCondition, /
) -> list[list[DatabaseRestrictionLeafConditionInput]]:
    dnf = dnf_from_condition(condition)
    return [
        [
            _leaf_condition_to_graphql(
                leaf_condition  # type: ignore[arg-type]
            )
            for leaf_condition in conjunct_conditions
        ]
        for conjunct_conditions in dnf
    ]
