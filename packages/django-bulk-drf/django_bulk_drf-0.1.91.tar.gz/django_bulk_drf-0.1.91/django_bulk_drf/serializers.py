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

    def get_fields(self):
        fields = super().get_fields()

        model = self.Meta.model

        meta_fields = self.Meta.fields
        is_all_fields = meta_fields == serializers.ALL_FIELDS
        requested_fields = (
            set(meta_fields) if isinstance(meta_fields, (list, tuple, set)) else None
        )

        declared_fields = self._declared_fields  # explicitly declared on the class

        for model_field in model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue

            fk_name = model_field.name
            fk_attname = model_field.attname

            if (
                requested_fields is not None
                and not is_all_fields
                and fk_attname not in requested_fields
            ):
                continue

            if fk_attname not in fields:
                fields[fk_attname] = serializers.IntegerField(
                    required=not model_field.null
                    and model_field.default is serializers.empty,
                    allow_null=model_field.null,
                )

            if fk_name in fields and fk_name not in declared_fields:
                fields.pop(fk_name)

        return fields

    def to_internal_value(self, data):
        """
        Convert *_id fields to actual field names for validation.
        
        This method handles the conversion from foreign key id fields (e.g., payment_schedule_id)
        to the actual field names (e.g., payment_schedule) that Django expects for validation.
        """
        # Make a copy to avoid modifying the original data
        internal_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        model = self.Meta.model
        
        # Process all foreign key fields
        for model_field in model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue
                
            fk_name = model_field.name
            fk_attname = model_field.attname
            
            # If we have a *_id field but not the actual field, convert it
            if fk_attname in internal_data and fk_name not in internal_data:
                internal_data[fk_name] = internal_data.pop(fk_attname)
        
        return super().to_internal_value(internal_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Add all *_id values for ForeignKey concrete fields without extra queries
        fk_names = []
        for model_field in instance._meta.concrete_fields:
            if isinstance(model_field, ForeignKey):
                attname = getattr(model_field, "attname", model_field.name)
                if attname not in data:
                    data[attname] = model_field.value_from_object(instance)
                fk_names.append(model_field.name)

        declared = getattr(self, "_declared_fields", {})
        names_to_hide = set(name for name in fk_names if name not in declared)

        for fk_name in names_to_hide:
            if fk_name in data:
                data.pop(fk_name)

        return data
