from rest_framework import routers
from services.viewsets import (
    WpsCapabilityViewSet,
    WfsCapabilityViewSet, WcsCapabilityViewSet, SosCapabilityViewSet, ServerViewSet,
    GeoJsonViewSet, SosObservationsViewSet, ExecutionViewSet, ServerCapabilitiesViewSet,
    ProcessViewSet, WorkflowViewSet
)

routes = routers.DefaultRouter()

routes.register("wps/capabilities", WpsCapabilityViewSet, "wps-capabilities")
routes.register("wfs/capabilities", WfsCapabilityViewSet, "wfs-capabilities")
routes.register("wcs/capabilities", WcsCapabilityViewSet, "wcs-capabilities")
routes.register("sos/capabilities", SosCapabilityViewSet, "sos-capabilities")
routes.register("sos/observations", SosObservationsViewSet, "sos-observations")
routes.register("servers", ServerViewSet, "list-servers")
routes.register("server/capabilities",
                ServerCapabilitiesViewSet, "servers-capabilities")
routes.register("json", GeoJsonViewSet, "geojson")
routes.register("workflow", ExecutionViewSet, "workflow")
routes.register("models", WorkflowViewSet, "models")
routes.register("process", ProcessViewSet, "process")

urlpatterns = [
    *routes.urls,
]
