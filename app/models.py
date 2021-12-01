from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import declarative_base


Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    subgroups = relationship("Subgroup", back_populates="group")
    sets = relationship("Set", back_populates="group")
    features = relationship("Feature", back_populates="group")


class Subgroup(Base):
    __tablename__ = "subgroups"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship(Group, back_populates="subgroups")
    sets = relationship("Set", back_populates="subgroup")
    features = relationship("Feature", back_populates="subgroup")


class Set(Base):
    __tablename__ = "sets"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    subgroup_id = Column(Integer, ForeignKey("subgroups.id"))
    subgroup = relationship(Subgroup, back_populates="sets")
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship(Group, back_populates="sets")
    features = relationship("Feature", back_populates="set")


class Interface(Base):
    __tablename__ = "interfaces"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")


interface_component_rel = Table(
    "interface_component_rel",
    Base.metadata,
    Column("interface_id", ForeignKey("interfaces.id"), primary_key=True),
    Column("component_id", ForeignKey("components.id"), primary_key=True),
)


class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    interfaces = relationship(Interface, secondary=interface_component_rel)


component_function_rel = Table(
    "component_function_rel",
    Base.metadata,
    Column("component_id", ForeignKey("components.id"), primary_key=True),
    Column("function_id", ForeignKey("functions.id"), primary_key=True),
    Column("amount", Integer, default=1),
)


class Function(Base):
    __tablename__ = "functions"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    components = relationship(Component, secondary=component_function_rel)


class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    subgroup_id = Column(Integer, ForeignKey("subgroups.id"))
    subgroup = relationship(Subgroup, back_populates="features")
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship(Group, back_populates="features")
    set_id = Column(Integer, ForeignKey("sets.id"))
    set = relationship(Set, back_populates="features")


feature_vehicle_rel = Table(
    "feature_vehicle_rel",
    Base.metadata,
    Column("feature_id", ForeignKey("features.id"), primary_key=True),
    Column("vehicle_id", ForeignKey("vehicles.id"), primary_key=True),
)


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    features = relationship(Feature, secondary=feature_vehicle_rel)
