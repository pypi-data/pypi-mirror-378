"""
Serializer utilities for django-bulk-drf.

Provides a base serializer that exposes <fk>_id fields for all ForeignKey fields
and removes relation fields to avoid additional queries during read and write.

Usage:

    class MySerializer(BulkModelSerializer):
        class Meta:
            model = MyModel
            fields = "__all__"

This ensures:
- On write: accepts integer id fields (e.g., loan_account_id) without triggering
  a validation lookup on the related model.
- On read: returns *_id values directly from the instance without fetching relations.
"""

from django.db.models import ForeignKey
from rest_framework import serializers


class BulkModelSerializer(serializers.ModelSerializer):
    """
    Response-only enhancement: automatically include "<fk>_id" values for all
    ForeignKey fields in the serialized output without changing write behavior.

    - Does not mutate declared serializer fields at all for input handling.
    - Avoids extra queries by reading the model's "<fk>_id" attributes.
    - Works with fields = "__all__" or explicit field lists.
    """

    class Meta:
        abstract = True
        include_fk_ids = True           # Add *_id to output
        mutate_fk_fields = False        # Do not alter input fields by default
        remove_fk_relations = False     # Legacy (input-time removal when mutate_fk_fields=True)
        hide_fk_relations_output = "auto"  # Default: hide FK relation fields unless explicitly declared

    def get_fields(self):
        # Preserve original write-time behavior by default
        fields = super().get_fields()

        meta = getattr(self, "Meta", None)
        if not meta or not getattr(meta, "mutate_fk_fields", False):
            return fields

        # Optional: support opt-in mutation of fields (kept for advanced users)
        model = getattr(meta, "model", None)
        if model is None:
            return fields

        declared_fields = getattr(meta, "fields", None)
        explicit_is_all = declared_fields == "__all__"
        explicit_set = (
            set(declared_fields)
            if isinstance(declared_fields, (list, tuple, set))
            else None
        )

        remove_fk = getattr(meta, "remove_fk_relations", False)
        declared = getattr(self, "_declared_fields", {})

        for model_field in model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue

            fk_name = model_field.name
            fk_attname = model_field.attname

            if explicit_set is not None and not explicit_is_all and fk_attname not in explicit_set:
                continue

            if fk_attname not in fields:
                fields[fk_attname] = serializers.IntegerField(
                    required=not model_field.null and model_field.default is serializers.empty,
                    allow_null=model_field.null,
                )

            if remove_fk and fk_name in fields and fk_name not in declared:
                fields.pop(fk_name)

        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)

        meta = getattr(self, "Meta", None)
        if not meta or not getattr(meta, "include_fk_ids", True):
            return data

        # Add all *_id values for ForeignKey concrete fields without extra queries
        fk_names = []
        for model_field in instance._meta.concrete_fields:
            if isinstance(model_field, ForeignKey):
                attname = getattr(model_field, "attname", model_field.name)
                if attname not in data:
                    data[attname] = model_field.value_from_object(instance)
                fk_names.append(model_field.name)

        # Optionally hide relation fields (e.g., loan_account) while keeping *_id
        hide_output = getattr(meta, "hide_fk_relations_output", False)
        if hide_output:
            # Determine which names to hide
            if hide_output is True:
                names_to_hide = set(fk_names)
            elif hide_output == "auto":
                # Hide all FK relation names except those explicitly declared on the serializer
                declared = getattr(self, "_declared_fields", {})
                names_to_hide = set(name for name in fk_names if name not in declared)
            else:
                try:
                    names_to_hide = set(hide_output)
                except TypeError:
                    names_to_hide = set()

            for fk_name in names_to_hide:
                if fk_name in data:
                    data.pop(fk_name)

        return data


