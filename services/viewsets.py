from rest_framework.viewsets import ModelViewSet, ViewSet
import requests
import re
import json
from services.serializers import (
    WpsCapabilitySerializer, WfsCapabilitySerializer,
    WcsCapabilitySerializer, SosCapabilitySerializer, SosObservationsSerializer,
    ServerSerializer, GeoJsonSerializer, ExecutionSerializer
)
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly, IsAuthenticated, SAFE_METHODS, IsAdminUser
from django.db import connection
from rest_framework.response import Response
from utils import Util
from services.models import Server


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class WpsCapabilityViewSet(ViewSet):
    permission_classes = [ReadOnly]

    serializer_class = WpsCapabilitySerializer

    def list(self, request):
        name = request.GET.get("name", "University of Twente WPS")
        url = request.GET.get("url")
        dtype = request.GET.get("type")
        # limit = request.GET.get("limit", 100)
        prefix = request.GET.get("prefix", "gs:")
        if dtype == "ILWIS":
            response = json.loads(requests.get(url).text)
        else:
            response = Util.getWpsProcesses(url, 100, prefix)
        if response is None:
            records = {"success": False, "operations": [], "name": name}
        else:
            records = {"success": True, "operations": response, "name": name}

        serializer = WpsCapabilitySerializer(instance=records, many=False)
        return Response(serializer.data)


class WfsCapabilityViewSet(ViewSet):
    permission_classes = [ReadOnly]

    serializer_class = WfsCapabilitySerializer

    def list(self, request):
        name = request.GET.get("name", "University of Twente WFS")
        url = request.GET.get("url")
        limit = request.GET.get("limit", 100)

        response = Util.getWfsCapabilities(url, limit)
        if response is None:
            records = {"success": False, "features": [], "name": name}
        else:
            records = {"success": True, "features": response, "name": name}

        serializer = WfsCapabilitySerializer(instance=records, many=False)
        return Response(serializer.data)


class WcsCapabilityViewSet(ViewSet):
    permission_classes = [ReadOnly]

    serializer_class = WcsCapabilitySerializer

    def list(self, request):
        name = request.GET.get("name", "University of Twente WCS")
        url = request.GET.get("url")
        limit = request.GET.get("limit", 100)

        response = Util.getWcsCapabilities(url, limit)
        if response is None:
            records = {"success": False, "coverages": [], "name": name}
        else:
            records = {"success": True, "coverages": response, "name": name}

        serializer = WcsCapabilitySerializer(instance=records, many=False)
        return Response(serializer.data)


class SosCapabilityViewSet(ViewSet):
    permission_classes = [ReadOnly]

    serializer_class = SosCapabilitySerializer

    def list(self, request):
        name = request.GET.get("name", "University of Twente WCS")
        url = request.GET.get("url")
        limit = request.GET.get("limit", 100)

        response = Util.getSosCapabilities(url, limit)
        if response is None:
            records = {"success": False, "observations": [], "name": name}
        else:
            records = {"success": True, "observations": response, "name": name}

        serializer = SosCapabilitySerializer(instance=records, many=False)
        return Response(serializer.data)


class SosObservationsViewSet(ViewSet):
    permission_classes = [ReadOnly]

    serializer_class = SosObservationsSerializer

    def list(self, request):
        url = request.GET.get("url")

        response = Util.getSosObservations(url)
        if response is None:
            records = {"success": False, "observations": []}
        else:
            records = {"success": True, "observations": response}

        serializer = SosObservationsSerializer(instance=records, many=False)
        return Response(serializer.data)


class ServerViewSet(ModelViewSet):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ServerSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Server.objects.all()


class GeoJsonViewSet(ViewSet):
    http_method_names = ["get", "post"]
    permission_classes = []

    serializer_class = GeoJsonSerializer

    def list(self, request):
        return Response({})

    @action(detail=False, methods=['get'], name='Transform vector data to target crs')
    def transform(self, request, pk=None):
        url = request.GET.get("url")
        if url is None:
            return Response({"msg": "URL of the GeoJSON data is required"}, status=400)
        srid = request.GET.get("srid")
        if srid is None:
            return Response({"msg": "Target SRID is required"}, status=400)
        response = requests.get(url)
        if response.text == "" or response.status_code > 200:
            return Response({"msg": "No data found"}, status=400)
        transformed = Util.jsonTransform(response.json(), srid)
        results = GeoJsonSerializer(transformed, many=False).data
        return Response(results)


class ExecutionViewSet(ViewSet):
    http_method_names = ["get", "post"]
    serializer_class = ExecutionSerializer

    def list(self, request):
        return Response({})

    @action(detail=False, methods=['post'], name='Execute workflow')
    def execute(self, request):
        workflow = request.POST.get("workflow")
        if workflow:
            workflow = json.loads(workflow)['workflows'][0]

        outputs = Util.executeWorkflow(workflow)
        results = []
        results = []
        for output in outputs:
            results.append({
                "id": output["id"],
                "result": output["data"],
                "type": output["type"]
            })
        return Response(results, status=200)
