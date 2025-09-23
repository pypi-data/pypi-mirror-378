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
    Replace ForeignKey relation fields with their "<fk>_id" integer counterparts
    for both read and write. This eliminates validation lookups and relation fetches.

    Notes:
    - This intentionally skips existence validation for FK ids. If you need validation,
      declare an explicit write-only PrimaryKeyRelatedField alongside the *_id field.
    - Works with fields = "__all__" or explicit field lists. For explicit lists,
      include the *_id names you want exposed.
    """

    class Meta:
        abstract = True
        include_fk_ids = True
        remove_fk_relations = True

    def get_fields(self):
        fields = super().get_fields()

        meta = getattr(self, "Meta", None)
        if not meta or not getattr(meta, "include_fk_ids", True):
            return fields

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

        remove_fk = getattr(meta, "remove_fk_relations", True)

        for model_field in model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue

            fk_name = model_field.name  # e.g., "loan_account"
            fk_attname = model_field.attname  # e.g., "loan_account_id"

            # If an explicit field list is provided (not __all__), only add when requested
            if explicit_set is not None and not explicit_is_all and fk_attname not in explicit_set:
                # respect the whitelist; do not inject
                continue

            # Add integer field for *_id if absent
            if fk_attname not in fields:
                fields[fk_attname] = serializers.IntegerField(
                    source=fk_attname,
                    required=not model_field.null and model_field.default is serializers.empty,
                    allow_null=model_field.null,
                )

            # Optionally remove relation field to ensure no relation access
            if remove_fk and fk_name in fields:
                fields.pop(fk_name)

        return fields


