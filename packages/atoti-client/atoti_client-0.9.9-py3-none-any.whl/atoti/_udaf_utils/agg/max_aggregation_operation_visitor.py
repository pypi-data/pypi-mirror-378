from __future__ import annotations

from textwrap import dedent
from typing import final

from typing_extensions import override

from ..._data_type import DataType, is_numeric_type
from ..java_operation_element import JavaOperationElement
from ..utils import get_buffer_read_code, get_buffer_write_code, get_terminate_code
from ._aggregation_operation_visitor import (
    CONTRIBUTE_TEMPLATE,
    MERGE_TEMPLATE,
    TERMINATE_TEMPLATE,
    AggregationOperationVisitor,
)


def _get_numeric_code(operation_element: JavaOperationElement) -> str:
    numeric_code = dedent(
        """\
        {output_type} in = {{java_source_code}};
        if (aggregationBuffer.isNull(0)) {{{{
            {buffer_writer}
        }}}} else {{{{
            {output_type} buffer = {buffer_value};
            if (in > buffer) {{{{
                {buffer_writer}
            }}}}
        }}}}
    """,
    )
    output_type = operation_element.output_type
    buffer_writer = get_buffer_write_code(
        buffer_code="aggregationBuffer",
        value_code="in",
        output_type=output_type,
    )
    buffer_value = get_buffer_read_code(
        buffer_code="aggregationBuffer",
        output_type=output_type,
    )
    return numeric_code.format(
        output_type=output_type,
        buffer_writer=buffer_writer,
        buffer_value=buffer_value,
    )


@final
class MaxAggregationOperationVisitor(AggregationOperationVisitor):
    """Implementation of the AggregationOperationVisitor to build the source code for a ``MAX`` aggregation function."""

    @staticmethod
    @override
    def _get_contribute_source_code(operation_element: JavaOperationElement) -> str:
        numeric_code = (
            _get_numeric_code(operation_element)
            if is_numeric_type(operation_element.output_type)
            else None
        )
        body = operation_element.get_java_source_code(numeric_code=numeric_code)
        return CONTRIBUTE_TEMPLATE.format(body=body)

    @staticmethod
    @override
    def _get_decontribute_source_code(
        operation_element: JavaOperationElement,
    ) -> str | None:
        # Max cannot be de-aggregated
        return None

    @staticmethod
    @override
    def _get_merge_source_code(operation_element: JavaOperationElement) -> str:
        if is_numeric_type(operation_element.output_type):
            output_type = operation_element.output_type
            input_value = get_buffer_read_code(
                buffer_code="inputAggregationBuffer",
                output_type=output_type,
            )
            output_value = get_buffer_read_code(
                buffer_code="outputAggregationBuffer",
                output_type=output_type,
            )
            output_writer = get_buffer_write_code(
                buffer_code="outputAggregationBuffer",
                value_code="in",
                output_type=output_type,
            )
            body_template = dedent(
                """\
                if (!inputAggregationBuffer.isNull(0)) {{{{
                    {output_type} in = {input_value};
                    if (outputAggregationBuffer.isNull(0)) {{{{
                        {output_writer}
                    }}}} else {{{{
                        {output_type} buffer = {output_value};
                        if (in > buffer) {{{{
                            {output_writer}
                        }}}}
                    }}}}
                }}}}
            """,
            )
            body = body_template.format(
                output_type=output_type,
                input_value=input_value,
                output_writer=output_writer,
                output_value=output_value,
            )
            return MERGE_TEMPLATE.format(body=body)

        raise TypeError("Unsupported output type " + str(operation_element.output_type))

    @staticmethod
    @override
    def _get_terminate_source_code(operation_element: JavaOperationElement) -> str:
        if is_numeric_type(operation_element.output_type):
            return_value = get_terminate_code(
                operation_element.output_type,
                get_buffer_read_code(
                    buffer_code="aggregationBuffer",
                    output_type=operation_element.output_type,
                ),
            )
            body = f"return {return_value};"
            return TERMINATE_TEMPLATE.format(body=body)

        raise TypeError("Unsupported output type " + str(operation_element.output_type))

    @staticmethod
    @override
    def _get_buffer_types(
        operation_element: JavaOperationElement,
    ) -> list[DataType]:
        return [operation_element.output_type]
