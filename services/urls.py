from rest_framework import routers
from services.viewsets import (
    WpsCapabilityViewSet,
    WfsCapabilityViewSet, WcsCapabilityViewSet, SosCapabilityViewSet, ServerViewSet,
    GeoJsonViewSet, SosObservationsViewSet, ExecutionViewSet, ServerCapabilitiesViewSet
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
routes.register("process", ExecutionViewSet, "process")

urlpatterns = [
    *routes.urls,
]
