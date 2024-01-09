from django.apps import AppConfig
import json


class ServicesConfig(AppConfig):
    name = 'services'

    # def ready(self):
    #     from services.models import Server

    #     from django.conf import settings
    #     if Server.objects.count() == 0:
    #         with open(f"{settings.BASE_DIR}/services/servers.json") as f:
    #             servers = json.loads(f.read())
    #             for item in servers['process']:
    #                 server, ok = Server.objects.get_or_create(
    #                     name=item.get("name"), url=item.get('url'),
    #                     defaults={
    #                         'name': item.get('name'),
    #                         'type': item.get('type'),
    #                         'url': item.get('url'),
    #                         'is_process': True
    #                     }
    #                 )
    #             for item in servers['data']:
    #                 server, ok = Server.objects.get_or_create(
    #                     name=item.get("name"), url=item.get('url'),
    #                     defaults={
    #                         'name': item.get('name'),
    #                         'type': item.get('type'),
    #                         'url': item.get('url'),
    #                         'is_process': False
    #                     }
    #                 )
    #     return super().ready()
