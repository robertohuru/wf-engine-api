from rest_framework import serializers
from services.models import Server


class WpsCapabilitySerializer(serializers.Serializer):
    success = serializers.BooleanField()
    operation = serializers.JSONField()


class WfsCapabilitySerializer(serializers.Serializer):
    success = serializers.BooleanField()
    features = serializers.JSONField()
    name = serializers.CharField()


class WcsCapabilitySerializer(serializers.Serializer):
    success = serializers.BooleanField()
    coverages = serializers.JSONField()
    name = serializers.CharField()


class SosCapabilitySerializer(serializers.Serializer):
    success = serializers.BooleanField()
    observations = serializers.JSONField()
    name = serializers.CharField()


class ServerCapabilitiesSerializer(serializers.Serializer):
    type = serializers.CharField()
    records = serializers.JSONField()
    url = serializers.CharField()
    name = serializers.CharField()
    is_process = serializers.BooleanField()


class SosObservationsSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    observations = serializers.JSONField()


class GeoJsonSerializer(serializers.Serializer):
    type = serializers.CharField()
    crs = serializers.JSONField()
    features = serializers.JSONField()
    name = serializers.CharField()


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('name', 'type', 'url', 'is_process')
        extra_kwargs = {'user': {'write_only': True}}


class ExecutionSerializer(serializers.Serializer):
    worklfow = serializers.JSONField()
