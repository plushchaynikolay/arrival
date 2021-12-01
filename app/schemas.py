import graphene as gr
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy.types import ORMField
import sqlalchemy as sa

from app.models import Feature, Vehicle, Group


async def _resolve(schema, info):
    return await info.context.get("session").scalars(sa.select(schema._meta.model))


# TODO: Optimization for one-to-many and many-to-many relations. Something like:
# https://github.com/tfoxy/graphene-django-optimizer
class BaseSchema:
    @classmethod
    def get_query(cls, info):
        return _resolve(cls, info)


class VehicleSchema(BaseSchema, SQLAlchemyObjectType):
    # !!!: Doesn't work this way :(
    # id = ORMField(type=gr.Int)

    pk = ORMField("id", type=gr.Int)

    class Meta:
        model = Vehicle
        interfaces = (gr.Node,)


class FeatureSchema(BaseSchema, SQLAlchemyObjectType):
    pk = ORMField("id", type=gr.Int)

    class Meta:
        model = Feature
        interfaces = (gr.Node,)


class GroupSchema(BaseSchema, SQLAlchemyObjectType):
    pk = ORMField("id", type=gr.Int)

    class Meta:
        model = Group
        interfaces = (gr.Node,)


class Query(gr.ObjectType):
    vehicles = gr.List(VehicleSchema)
    groups = gr.List(GroupSchema)
    features = gr.List(FeatureSchema)

    # TODO: Implement filters.
    def resolve_vehicles(self, info):
        return VehicleSchema.get_query(info)

    def resolve_groups(self, info):
        return GroupSchema.get_query(info)

    def resolve_features(self, info):
        return FeatureSchema.get_query(info)


class CreateVehicle(gr.Mutation):
    class Arguments:
        name = gr.String()

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
        name = gr.String()

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
        feature_id = gr.Int()
        vehicle_id = gr.Int()

    ok = gr.Boolean()
    vehicle = gr.Field(VehicleSchema)

    async def mutate(self, info, feature_id, vehicle_id):
        session = info.context.get("session")
        vehicle = Vehicle(id=vehicle_id)
        feature = Feature(id=feature_id)
        vehicle.features.append(feature)

        async with session.begin():
            session.add(vehicle)
        await session.commit()

        vehicle = VehicleSchema()
        return AddFeature(ok=True, vehicle=vehicle)


class Mutation(gr.ObjectType):
    add_feature = AddFeature.Field()
    create_vehicle = CreateVehicle.Field()
    create_feature = CreateFeature.Field()


schema = gr.Schema(query=Query, mutation=Mutation)
