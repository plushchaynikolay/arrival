"""Dirty 'copy-paste' module which provides asyncio support for `graphene_sqlalchemy.SQLAlchemyConnection`
"""
from functools import partial

import graphene as gr
import sqlalchemy as sa
from graphql import get_nullable_type
from promise import Promise, is_thenable
from sqlalchemy.ext.asyncio import AsyncSession
from graphene_sqlalchemy.fields import UnsortedSQLAlchemyConnectionField
from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)


# NOTE: async version of `graphene_sqlalchemy.fields::connection_from_list_slice`
async def connection_from_list_slice(
    session: AsyncSession,
    list_slice,
    args=None,
    connection_type=None,
    edge_type=None,
    pageinfo_type=None,
    slice_start=0,
    list_length=0,
    list_slice_length=None,
):
    connection_type = connection_type or gr.Connection
    edge_type = edge_type or gr.Edge
    pageinfo_type = pageinfo_type or gr.PageInfo

    args = args or {}

    before = args.get("before")
    after = args.get("after")
    first = args.get("first")
    last = args.get("last")
    if list_slice_length is None:
        list_slice_length = len(list_slice)
    slice_end = slice_start + list_slice_length
    before_offset = get_offset_with_default(before, list_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(slice_start - 1, after_offset, -1) + 1
    end_offset = min(slice_end, before_offset, list_length)
    if isinstance(first, int):
        end_offset = min(end_offset, start_offset + first)
    if isinstance(last, int):
        start_offset = max(start_offset, end_offset - last)

    # If supplied slice is too large, trim it down before mapping over it.

    # NOTE: ONLY MODIFIED ->
    if isinstance(list_slice, sa.sql.Select):
        offset = max(start_offset - slice_start, 0)
        limit = list_slice_length - (slice_end - end_offset) - offset
        _slice = list_slice.limit(limit).offset(offset)
        _slice = await session.scalars(_slice)
    # -> END

    else:
        _slice = list_slice[
            max(start_offset - slice_start, 0) : list_slice_length
            - (slice_end - end_offset)
        ]

    edges = [
        edge_type(node=node, cursor=offset_to_cursor(start_offset + i))
        for i, node in enumerate(_slice)
    ]

    first_edge_cursor = edges[0].cursor if edges else None
    last_edge_cursor = edges[-1].cursor if edges else None
    lower_bound = after_offset + 1 if after else 0
    upper_bound = before_offset if before else list_length

    return connection_type(
        edges=edges,
        page_info=pageinfo_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=isinstance(last, int) and start_offset > lower_bound,
            has_next_page=isinstance(first, int) and end_offset < upper_bound,
        ),
    )


class AsyncSQLAlchemyConnectionField(UnsortedSQLAlchemyConnectionField):
    async def resolve_connection(self, connection_type, model, info, args, resolved):

        # NOTE: ONLY MODIFIED ->
        session: AsyncSession = info.context.get("session")
        if resolved is None or isinstance(resolved, sa.sql.Selectable):
            resolved = sa.select(model)
            stmt = sa.select(sa.func.count(model.id))
            _len = (await session.execute(stmt)).scalars().first()
        # -> END

        else:
            _len = len(resolved)

        # NOTE: ONLY MODIFIED ->
        connection = await connection_from_list_slice(
            session,  # -> END
            resolved,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection_type,
            pageinfo_type=gr.PageInfo,
            edge_type=connection_type.Edge,
        )
        connection.iterable = resolved
        connection.length = _len
        return connection

    def connection_resolver(self, resolver, connection_type, model, root, info, **args):
        resolved = resolver(root, info, **args)

        on_resolve = partial(
            # NOTE: ONLY MODIFIED: Instance method instead of class method
            self.resolve_connection,
            connection_type,
            model,
            info,
            args,
        )
        if is_thenable(resolved):
            return Promise.resolve(resolved).then(on_resolve)

        return on_resolve(resolved)

    def get_resolver(self, parent_resolver):
        return partial(
            # NOTE: ONLY MODIFIED: Instance method instead of class method
            self.connection_resolver,
            parent_resolver,
            get_nullable_type(self.type),
            self.model,
        )
