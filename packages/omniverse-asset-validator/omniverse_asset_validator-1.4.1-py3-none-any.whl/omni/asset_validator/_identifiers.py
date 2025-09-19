# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from dataclasses import dataclass, field
from functools import singledispatch, singledispatchmethod
from typing import Any, Generic, TypeVar

from pxr import Sdf, Usd, UsdGeom

from ._deprecate import deprecated
from ._url_utils import normalize_url

__all__ = [
    "AtType",
    "AttributeId",
    "EditTargetId",
    "Identifier",
    "LayerId",
    "PrimId",
    "PropertyId",
    "PrimvarId",
    "SchemaBaseId",
    "SpecId",
    "SpecIdList",
    "StageId",
    "VariantIdMixin",
    "to_identifier",
    "to_identifiers",
    "ANON_VALIDATOR_LAYER_NAME",
]

AtType = TypeVar(
    "AtType",
    Sdf.Layer,
    Usd.Stage,
    Usd.Prim,
    Usd.Property,
    Usd.Attribute,
    Usd.Relationship,
    Usd.SchemaBase,
    UsdGeom.Primvar,
    Sdf.PrimSpec,
    Sdf.PropertySpec,
)
"""
Location of an issue or a fix.

Can be any of:
  - :py:class:`pxr.Sdf.Layer`
  - :py:class:`pxr.Usd.Stage`
  - :py:class:`pxr.Usd.Prim`
  - :py:class:`pxr.Usd.Property`
  - :py:class:`pxr.Usd.Attribute`
  - :py:class:`pxr.Usd.Relationship`
  - :py:class:`pxr.Usd.SchemaBase`
  - :py:class:`pxr.UsdGeom.Primvar`
  - :py:class:`pxr.Sdf.PrimSpec`
  - :py:class:`pxr.Sdf.PropertySpec`
"""

ANON_VALIDATOR_LAYER_NAME = "AssetValidator"
"""str: Internal layer name to use with anonymous layers."""


@dataclass(frozen=True)
class Identifier(Generic[AtType]):
    """
    An Identifier is a stateful representation of an Usd object (i.e. Usd.Prim). A identifier can convert back to a
    live Usd object.
    """

    @classmethod
    def from_(cls, obj: AtType) -> Identifier[AtType]:
        """
        Args:
            obj (AtType): An Usd Object.

        Returns:
            A stateful representation of an Usd object.
        """
        raise NotImplementedError()

    def restore(self, stage: Usd.Stage) -> AtType:
        """
        Convert this stateful identifier to a live object.

        Args:
            stage (Usd.Stage): The stage to use to restore the object.

        Returns:
            An Usd object.
        """
        raise NotImplementedError()

    @deprecated("For testing use Sdf.Path")
    def as_str(self) -> str:
        raise NotImplementedError()

    @deprecated("Use get_spec_ids instead")
    def get_layer_ids(self) -> list[LayerId]:
        return [spec_id.layer_id for spec_id in self.get_spec_ids()]

    def get_spec_ids(self) -> list[SpecId]:
        """
        Returns:
            The list of all possible prim specs i.e., path and layer ids associated to this identifier.
        """
        return []


@dataclass(frozen=True)
class LayerId(Identifier[Sdf.Layer]):
    """
    A unique identifier to layer, i.e. identifier.

    Attributes:
        identifier (str): The unique identifier of this layer.
    """

    identifier: str

    def __post_init__(self):
        object.__setattr__(self, "identifier", normalize_url(self.identifier))

    @classmethod
    def from_(cls, layer: Sdf.Layer) -> LayerId:
        return LayerId(
            identifier=layer.identifier,
        )

    def restore(self, stage: Usd.Stage) -> Sdf.Layer:
        return Sdf.Layer.FindOrOpen(self.identifier)

    def get_spec_ids(self) -> list[SpecId]:
        return [SpecId(layer_id=self)]

    def as_str(self):
        return self.identifier

    @property
    def _internal(self) -> bool:
        return (
            Sdf.Layer.IsAnonymousLayerIdentifier(self.identifier)
            and Sdf.Layer.GetDisplayNameFromIdentifier(self.identifier) == ANON_VALIDATOR_LAYER_NAME
        )


@dataclass(frozen=True)
class StageId(Identifier[Usd.Stage]):
    """
    A unique identifier to stage, i.e. identifier.

    Attributes:
        root_layer (LayerId): Identifier representing the root layer.
    """

    root_layer: LayerId

    @classmethod
    def from_(cls, stage: Usd.Stage) -> StageId:
        return StageId(
            root_layer=LayerId.from_(stage.GetRootLayer()),
        )

    @property
    @deprecated("Use root_layer instead")
    def identifier(self) -> str:
        return self.root_layer.identifier

    @property
    def stage_id(self) -> StageId:
        return self

    def restore(self, stage: Usd.Stage) -> Usd.Stage:
        if LayerId.from_(stage.GetRootLayer()) != self.root_layer:
            raise ValueError("The supplied stage do not corresponds to current stage.")
        return stage

    def as_str(self) -> str:
        return f"Stage <{self.root_layer.identifier}>"

    def get_spec_ids(self) -> list[SpecId]:
        return self.root_layer.get_spec_ids()


@dataclass(frozen=True)
class EditTargetId(Identifier[Sdf.Layer | Sdf.Spec]):
    """
    A unique identifier to a edit targets (i.e. layer or spec).

    Attributes:
        layer_id (LayerId): The layer where this identifier exists.
        path (Sdf.Path | None): The path to this specification. If None, the edit target is the layer.
    """

    layer_id: LayerId
    path: Sdf.Path | None = None

    @singledispatchmethod
    @classmethod
    def from_(cls, obj: Sdf.Layer | Sdf.Spec) -> EditTargetId:
        raise NotImplementedError(f"Unknown type {type(obj)}")

    @from_.register(Sdf.Layer)
    @classmethod
    def _(cls, layer: Sdf.Layer) -> EditTargetId:
        return EditTargetId(
            layer_id=LayerId.from_(layer),
            path=None,
        )

    @from_.register(Sdf.Spec)
    @classmethod
    def _(cls, spec: Sdf.Spec) -> EditTargetId:
        return EditTargetId(
            layer_id=LayerId.from_(spec.layer),
            path=spec.path,
        )

    def restore(self, stage: Usd.Stage) -> Sdf.Layer | Sdf.Spec | None:
        layer: Sdf.Layer = self.layer_id.restore(stage)  # Hold ref.
        if not layer:
            return None
        if not self.path:
            return layer
        spec: Sdf.Spec = layer.GetObjectAtPath(self.path)
        if not spec:
            return None
        return spec

    def get_spec_ids(self) -> list[EditTargetId]:
        return [self]

    def as_str(self) -> str:
        if self.path is None:
            return f"Sdf.Find('{self.layer_id.identifier}')"
        else:
            return f"Sdf.Find('{self.layer_id.identifier}', '{self.path}')"

    @property
    def _internal(self) -> bool:
        return self.layer_id._internal


SpecId = EditTargetId
"""
Deprecated. Use EditTargetId instead.
"""


@dataclass(frozen=True)
class SpecIdList:
    """
    A snapshot of a list of PcpNodeRefs.

    Attributes:
        spec_ids (list[SpecId]): The list of prim specifications.
    """

    spec_ids: list[SpecId] = field(hash=False)

    @classmethod
    def from_(cls, prim: Usd.Prim) -> SpecIdList:
        nodes: list[SpecId] = []
        for spec in prim.GetPrimStack():
            spec_id = SpecId.from_(spec)
            if spec_id._internal:
                continue
            nodes.append(spec_id)
        return SpecIdList(spec_ids=nodes)

    def __iter__(self):
        return iter(self.spec_ids)


class VariantIdMixin:
    """
    Mixin class for handling variant selection paths for USD prims.

    This class provides utility methods to retrieve and restore variant selections
    for USD prims, making it easier to work with variant hierarchies.
    """

    @property
    def variant_selection_path(self) -> Sdf.Path:
        return Sdf.Path.emptyPath

    @staticmethod
    def get_variant_selection_path(prim: Usd.Prim) -> Sdf.Path:
        """
        Return a Sdf.Path with variant selection encoded.

        For Example:
            Sdf.Path("/World/asset{variantA=aaa}child{variantB=bbb}{variantC=ccc}group/mesh.extent")
        """

        paths = []
        # Traverse the hierarchy to get variant selections
        while prim and prim.GetPath() != Sdf.Path.absoluteRootPath:
            path = Sdf.Path(prim.GetName())

            # Get the variant sets for the current prim
            variant_sets = prim.GetVariantSets()
            # Append each variant set and its selected variant
            for variant_set_name in variant_sets.GetNames():
                variant_set = variant_sets.GetVariantSet(variant_set_name)
                selected_variant = variant_set.GetVariantSelection()
                if selected_variant:
                    path = path.AppendVariantSelection(variant_set_name, selected_variant)

            paths.append(path)
            prim = prim.GetParent()

        variant_selection_path = Sdf.Path.absoluteRootPath
        for path in reversed(paths):
            variant_selection_path = variant_selection_path.AppendPath(path)

        return variant_selection_path

    def restore_variant_selection(self, stage: Usd.Stage):
        all_variant_selections: list[tuple[Sdf.Path, list[tuple[str, str]]]] = []
        selected_variants: list[tuple[str, str]] = []
        # Retrieve all parent variant selections from self.variant_selection_path
        for path in self.variant_selection_path.GetAncestorsRange():
            if path.IsPrimVariantSelectionPath():
                selected_variants.append(path.GetVariantSelection())
            else:
                if selected_variants:
                    all_variant_selections.append((path.StripAllVariantSelections().GetPrimPath(), selected_variants))
                selected_variants = []

        for prim_path, variants in reversed(all_variant_selections):
            for variant_name, selected_variant in variants:
                stage.GetPrimAtPath(prim_path).GetVariantSet(variant_name).SetVariantSelection(selected_variant)


@dataclass(frozen=True)
class PrimId(Identifier[Usd.Prim], VariantIdMixin):
    """
    A unique identifier of a prim, i.e. a combination of Stage definition and a list of Specs.

    Attributes:
        stage_id (StageId): An identifier to the stage this prim exists.
        path (Sdf.Path): The path to this prim.
        spec_ids (SpecIdList): The list of specifications as found in the stage.
        variant_selection_path (Sdf.Path): The variant selection path for this prim.
    """

    stage_id: StageId
    path: Sdf.Path
    spec_ids: SpecIdList
    variant_selection_path: Sdf.Path = Sdf.Path.emptyPath

    @classmethod
    def from_(cls, prim: Usd.Prim) -> PrimId:
        return PrimId(
            stage_id=StageId.from_(prim.GetStage()),
            path=prim.GetPrimPath(),
            spec_ids=SpecIdList.from_(prim),
            variant_selection_path=cls.get_variant_selection_path(prim),
        )

    def restore(self, stage: Usd.Stage) -> Usd.Prim:
        stage = self.stage_id.restore(stage)
        return stage.GetPrimAtPath(self.path)

    def as_str(self) -> str:
        return f"Prim <{self.path}>"

    def get_spec_ids(self) -> list[SpecId]:
        result: list[SpecId] = []
        for node_id in self.spec_ids:
            result.extend(node_id.get_spec_ids())
        return result

    def __str__(self):
        """Custom str as path is calculated."""
        return f"PrimId(stage_id={self.stage_id}, path={self.path})"


@dataclass(frozen=True)
class PropertyId(Identifier[Usd.Attribute], VariantIdMixin):
    """
    A unique identifier of a property, i.e. a combination of prim definition and property path.

    Attributes:
        prim_id (PrimId): An identifier to the prim containing this property.
        path (Sdf.Path): The path to this property.
    """

    prim_id: PrimId
    path: Sdf.Path

    @property
    def variant_selection_path(self):
        return self.prim_id.variant_selection_path.AppendElementString(self.path.elementString)

    @classmethod
    def from_(cls, prop: Usd.Property) -> PropertyId:
        return PropertyId(prim_id=PrimId.from_(prop.GetPrim()), path=prop.GetPath())

    def restore(self, stage: Usd.Stage) -> Usd.Property:
        prim = self.prim_id.restore(stage)
        return prim.GetProperty(self.name)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def stage_id(self) -> StageId:
        return self.prim_id.stage_id

    def as_str(self) -> str:
        return f"Attribute ({self.name}) {self.prim_id.as_str()}"

    def get_spec_ids(self) -> list[SpecId]:
        return [
            SpecId(
                path=node_id.path.AppendProperty(self.name),
                layer_id=node_id.layer_id,
            )
            for node_id in self.prim_id.get_spec_ids()
        ]


@dataclass(frozen=True)
class AttributeId(PropertyId):
    """
    A unique identifier of an attribute, i.e. a combination of prim definition and attribute name.
    """

    @classmethod
    def from_(cls, attr: Usd.Attribute) -> AttributeId:
        return AttributeId(prim_id=PrimId.from_(attr.GetPrim()), path=attr.GetPath())


@dataclass(frozen=True)
class RelationshipId(PropertyId):
    """
    A unique identifier of a relationship, i.e. a combination of prim definition and relationship name.
    """

    @classmethod
    def from_(cls, rel: Usd.Relationship) -> RelationshipId:
        return RelationshipId(prim_id=PrimId.from_(rel.GetPrim()), path=rel.GetPath())


@dataclass(frozen=True)
class PrimvarId(AttributeId, Identifier[UsdGeom.Primvar]):
    """Alias for primvars."""

    @classmethod
    def from_(cls, primvar: UsdGeom.Primvar) -> PrimvarId:
        attribute_id = super().from_(primvar.GetAttr())
        return PrimvarId(
            prim_id=attribute_id.prim_id,
            path=attribute_id.path,
        )

    def restore(self, stage: Usd.Stage) -> UsdGeom.Primvar:
        return UsdGeom.Primvar(super().restore(stage))


@dataclass(frozen=True)
class SchemaBaseId(Identifier[Usd.SchemaBase], VariantIdMixin):
    """
    A unique identifier of a UsdSchemaBase, i.e. a combination of prim definition and its real type class.

    Attributes:
        prim_id (PrimId): An identifier to the prim this schema is applied or typed to.
        schema_class (Any): The real type class that's inherited from UsdSchemaBase.
    """

    prim_id: PrimId
    schema_class: Any
    instance_name: str | None  # Only valid when it's multi apply schema.

    @property
    def variant_selection_path(self):
        return self.prim_id.variant_selection_path

    @classmethod
    def from_(cls, instance: Usd.SchemaBase) -> SchemaBaseId:
        return SchemaBaseId(
            prim_id=PrimId.from_(instance.GetPrim()),
            schema_class=type(instance),
            instance_name=instance.GetName() if instance.IsMultipleApplyAPISchema() else "",
        )

    @property
    def path(self) -> Sdf.Path:
        return self.prim_id.path

    def restore(self, stage: Usd.Stage) -> Any:
        prim = self.prim_id.restore(stage)
        return self.schema_class(prim, self.instance_name) if self.instance_name else self.schema_class(prim)

    def get_spec_ids(self) -> list[SpecId]:
        return self.prim_id.get_spec_ids()

    def as_str(self) -> str:
        return self.prim_id.as_str()


@singledispatch
def to_identifier(value: AtType | None) -> Identifier[AtType] | None:
    """
    Args:
        value (AtType | None): An USD object.

    Returns:
        An identifier (i.e. stateful representation) to a USD object.
    """
    raise NotImplementedError(f"Unknown type {type(value)}")


@to_identifier.register(Identifier)
def _(value: Identifier[AtType]) -> Identifier[AtType]:
    return value


@to_identifier.register(type(None))
def _(value: None) -> None:
    return None


@to_identifier.register(Usd.Attribute)
def _(value: Usd.Attribute) -> AttributeId:
    return AttributeId.from_(value)


@to_identifier.register(Usd.Property)
def _(value: Usd.Property) -> PropertyId:
    return PropertyId.from_(value)


@to_identifier.register(Usd.Relationship)
def _(value: Usd.Relationship) -> RelationshipId:
    return RelationshipId.from_(value)


@to_identifier.register(UsdGeom.Primvar)
def _(value: UsdGeom.Primvar) -> PrimvarId:
    return PrimvarId.from_(value)


@to_identifier.register(Usd.Prim)
def _(value: Usd.Prim) -> PrimId:
    return PrimId.from_(value)


@to_identifier.register(Usd.Stage)
def _(value: Usd.Stage) -> StageId:
    return StageId.from_(value)


@to_identifier.register(Sdf.Layer)
def _(value: Sdf.Layer) -> LayerId:
    return LayerId.from_(value)


@to_identifier.register(Sdf.Spec)
def _(value: Sdf.Spec) -> SpecId:
    return SpecId.from_(value)


@to_identifier.register(Usd.SchemaBase)
def _(value: Usd.SchemaBase) -> SchemaBaseId:
    return SchemaBaseId.from_(value)


def to_identifiers(value: list[AtType] | None) -> list[Identifier[AtType]] | None:
    """
    Iterative version of to_identifier.

    Args:
        value (list[AtType] | None): A list of USD objects.

    Returns:
        A list of identifiers (i.e. stateful representation) to a USD object.
    """
    result: list[Identifier[AtType]] = []
    if value is None:
        return None
    for item in value:
        result.append(to_identifier(item))
    return result
