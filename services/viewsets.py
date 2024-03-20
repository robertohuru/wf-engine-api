from rest_framework.viewsets import ModelViewSet, ViewSet
import requests
import re
import json
from services.serializers import (
    WpsCapabilitySerializer, WfsCapabilitySerializer,
    WcsCapabilitySerializer, SosCapabilitySerializer, SosObservationsSerializer,
    ServerSerializer, GeoJsonSerializer, ExecutionSerializer, ServerCapabilitiesSerializer
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
    http_method_names = ["get", "post"]
    # permission_classes = [ReadOnly]
    serializer_class = WpsCapabilitySerializer

    def list(self, request):
        url = request.GET.get("url")
        dtype = request.GET.get("resource")
        identifier = request.GET.get("identifier")
        response = None
        if dtype == "ILWIS":
            response = json.loads(requests.get(url).text)
        else:
            if identifier is not None:
                response = Util.getWpsCapacilities(url, identifier)
        if response is None:
            records = {"success": False, "operation": None}
        else:
            records = {"success": True, "operation": response}

        serializer = WpsCapabilitySerializer(instance=records, many=False)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='Get process metadata')
    def metadata(self, request):
        url = request.POST.get("url")
        dtype = request.POST.get("resource")
        identifier = request.POST.get("identifier")
        if dtype == "ILWIS":
            response = json.loads(requests.get(url).text)
        elif dtype == "GeoServer":
            response = "Geoserver"
        else:
            response = Util.getWpsCapacilities(url, identifier)
        if not response:
            records = {"success": False, "operation": None}
        else:
            records = {"success": True, "operation": response}

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
        name = request.GET.get("name", "University of Twente SOS")
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


class ServerCapabilitiesViewSet(ViewSet):
    http_method_names = ["get"]

    serializer_class = ServerCapabilitiesSerializer

    def list(self, request):
        url = request.GET.get("url")
        dtype = request.GET.get("type")
        name = request.GET.get("name")
        is_process = request.GET.get("type", False)
        limit = 100

        if url is None:
            servers = Server.objects.filter(enabled=True)
        else:
            server = Server()
            server.url = url
            server.type = dtype
            server.name = name
            server.is_process = is_process

            servers = [server]

        results = []
        for server in servers:
            if server.is_process and server.type == "WPS":
                response = Util.getWpsProcesses(server.url, limit,  "gs:")
                if response:
                    results.append(
                        {
                            "name": server.name,
                            "records": response,
                            "is_process": True,
                            "type": "WPS",
                            "url": server.url
                        }
                    )
            elif server.type == "WCS":
                response = Util.getWcsCapabilities(server.url, limit)
                if response:
                    results.append(
                        {
                            "name": server.name,
                            "records": response,
                            "is_process": False,
                            "type": "WCS",
                            "url": server.url
                        }
                    )
            elif server.type == "WFS":
                response = Util.getWfsCapabilities(server.url, limit)
                if response:
                    results.append(
                        {
                            "name": server.name,
                            "records": response,
                            "is_process": False,
                            "type": "WFS",
                            "url": server.url
                        }
                    )
            elif server.type == "SOS":
                response = Util.getSosCapabilities(server.url, 100)
                if response:
                    results.append(
                        {
                            "name": server.name,
                            "records": response,
                            "is_process": False,
                            "type": "SOS",
                            "url": server.url
                        }
                    )
        serializer = ServerCapabilitiesSerializer(instance=results, many=True)
        return Response(results)


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

    @action(detail=False, methods=['post'], name='Download workflow')
    def download(self, request):
        package = request.POST.get("package")
        workflow = request.POST.get("workflow")
        if not workflow:
            return Response({"message": "Workflow required"}, status=500)
        workflowJSON = json.loads(workflow)
        if package is None:
            package = 'QGIS'

        # if package == "ILWIS":
        #     print(workflow)
        if package == "QGIS":
            result = Util.piwToQgisWorkflow(workflowJSON)
            return Response(result, status=200)
        return Response(workflow, status=200)

    @action(detail=False, methods=['post'], name='Upload workflow')
    def upload(self, request):
        package = request.POST.get("package")
        workflow = request.POST.get("workflow")

        url = request.POST.get("url")
        if not workflow and not url:
            return Response({"message": "Workflow required"}, status=500)

        if url:
            req = requests.get(url)
            if req.status_code > 200:
                return Response({"message": "UR: not found"}, status=404)
            workflow = req.text
        workflowJSON = json.loads(workflow)
        if package is None:
            package = 'QGIS'

        if package == "ILWIS":
            result = Util.IlwisWorkflowToPIW(workflowJSON)
            return Response(result, status=200)
        elif package == "QGIS":
            result = Util.QgisWorkflowToPIW(workflowJSON)
            return Response(result, status=200)
        else:
            return Response(workflowJSON, status=200)
