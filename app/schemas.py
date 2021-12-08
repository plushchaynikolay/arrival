import graphene as gr
import sqlalchemy as sa
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy.types import ORMField
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Feature, Vehicle, Group

from .utils import AsyncSQLAlchemyConnectionField


class VehicleSchema(SQLAlchemyObjectType):
    # !!!: Doesn't work this way :(
    # id = ORMField(type=gr.Int)

    pk = ORMField("id", type=gr.Int)
    features = AsyncSQLAlchemyConnectionField(lambda: FeatureSchema.connection)

    class Meta:
        model = Vehicle
        interfaces = (gr.Node,)

    # TODO: Optimization for one-to-many and many-to-many relations. Something like:
    # https://github.com/tfoxy/graphene-django-optimizer
    def resolve_features(parent, info):
        return sa.select(Feature).join(Feature.vehicles).where(Vehicle.id == parent.id)


class FeatureSchema(SQLAlchemyObjectType):
    pk = ORMField("id", type=gr.Int)

    class Meta:
        model = Feature
        interfaces = (gr.Node,)


class GroupSchema(SQLAlchemyObjectType):
    pk = ORMField("id", type=gr.Int)

    class Meta:
        model = Group
        interfaces = (gr.Node,)


class Query(gr.ObjectType):
    all_vehicles = AsyncSQLAlchemyConnectionField(VehicleSchema.connection)
    all_groups = AsyncSQLAlchemyConnectionField(GroupSchema.connection)
    all_features = AsyncSQLAlchemyConnectionField(FeatureSchema.connection)


class CreateVehicle(gr.Mutation):
    class Arguments:
        name = gr.String(required=True)

    ok = gr.Boolean()
    vehicle = gr.Field(VehicleSchema)

    async def mutate(self, info, name):
        session = info.context.get("session")
        vehicle = Vehicle(name=name)
        async with session.begin():
            session.add(vehicle)
        await session.commit()
        return CreateVehicle(ok=True, vehicle=vehicle)


class CreateFeature(gr.Mutation):
    class Arguments:
        name = gr.String(required=True)

    ok = gr.Boolean()
    feature = gr.Field(FeatureSchema)

    async def mutate(self, info, name):
        session = info.context.get("session")
        feature = Feature(name=name)
        async with session.begin():
            session.add(feature)
        await session.commit()
        return CreateFeature(ok=True, feature=feature)


class AddFeature(gr.Mutation):
    class Arguments:
        feature_id = gr.Int(required=True)
        vehicle_id = gr.Int(required=True)

    ok = gr.Boolean()
    vehicle = gr.Field(VehicleSchema)

    async def mutate(self, info, feature_id, vehicle_id):
        session: AsyncSession = info.context.get("session")
        vehicle = Vehicle(id=vehicle_id)
        feature = Feature(id=feature_id)

        async with session.begin():
            vehicle.features.append(feature)
            await session.merge(vehicle)
        await session.commit()

        return AddFeature(ok=True, vehicle=vehicle)


class Mutation(gr.ObjectType):
    add_feature = AddFeature.Field()
    create_vehicle = CreateVehicle.Field()
    create_feature = CreateFeature.Field()


schema = gr.Schema(query=Query, mutation=Mutation)
