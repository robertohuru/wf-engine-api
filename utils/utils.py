import requests
import urllib.request
from urllib.parse import quote, urlparse
import xmltodict
import string
import random
import math
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import fromstring
from xml.etree import ElementTree
from xml.dom import minidom
import json
import datetime
import time
from django.contrib.gis.geos import Point, GEOSGeometry
from django.conf import settings
import os
import rasterio
import numpy as np
min_attributes = ('scheme', 'netloc')


class Util:
    @staticmethod
    def getWpsProcesses(url, limit=100, prefix="gs:"):
        if url is None:
            url = "https://mara.rangelands.itc.utwente.nl/geoserver/ows?"
        if "?" not in url:
            url = url + "?"
        results = requests.get(url + "service=WPS&request=GetCapabilities")
        if results.text == "" or results.status_code > 200:
            return None
        xpars = xmltodict.parse(results.text)
        d = json.loads(json.dumps(xpars))
        gsProcesses = []

        processes = []
        if isinstance(d['wps:Capabilities']['wps:ProcessOfferings']['wps:Process'], dict):
            gsProcesses.append(d['wps:Capabilities']
                               ['wps:ProcessOfferings']['wps:Process'])
        else:
            gsProcesses = d['wps:Capabilities']['wps:ProcessOfferings']['wps:Process']
        for row in gsProcesses:
            identifier = row['ows:Identifier']

            if len(processes) > int(limit):
                break
            if prefix not in identifier:
                continue
            processes.append({
                'id': identifier,
                'metadata': {
                    'label':  identifier,
                    'longname': row['ows:Title'],
                    'resource': 'WPS',
                    'url': url,
                    'description': row.get('ows:Abstract', '')
                }
            })

        return processes

    @staticmethod
    def getWpsCapacilities(url, identifier):
        response = requests.get(
            url + "service=WPS&request=DescribeProcess&identifier=" + identifier)
        response = xmltodict.parse(response.text)
        json2 = json.dumps(response)
        b = json.loads(json2)

        process = {
            'id': identifier,
            'metadata': {
                'label':  identifier,
            }
        }

        inputs = []
        if 'ProcessDescription' in b['wps:ProcessDescriptions']:
            if isinstance(b['wps:ProcessDescriptions']['ProcessDescription']['DataInputs']['Input'], dict):
                inputs = [b['wps:ProcessDescriptions']
                          ['ProcessDescription']['DataInputs']['Input']]
            elif isinstance(b['wps:ProcessDescriptions']['ProcessDescription']['DataInputs']['Input'], list):
                inputs = b['wps:ProcessDescriptions']['ProcessDescription']['DataInputs']['Input']

        inputList = []
        for i, item in enumerate(inputs):

            input = {
                'id': i, 'identifier': item['ows:Identifier'], 'name':  item['ows:Title'],
                'url': '', 'value': '', 'optional': '@minOccurs' in item and item['@minOccurs'] == '0',
                'description': item.get('ows:Abstract', '')
            }
            if 'ComplexData' in item:
                if "text/xml" in str(item['ComplexData']['Default']['Format']['MimeType']) or "application/json" in str(item['ComplexData']['Default']['Format']['MimeType']):
                    input['type'] = "geom"
                elif "image" in str(item['ComplexData']['Default']['Format']['MimeType']):
                    input['type'] = "coverage"
                else:
                    input['type'] = item['ComplexData']['Default']['Format']

            if 'LiteralData' in item and item['LiteralData']:
                if 'ows:DataType' in item['LiteralData']:
                    if '@ows:reference' in item['LiteralData']['ows:DataType']:
                        input['type'] = item['LiteralData']['ows:DataType']['#text']
                    else:
                        input['type'] = item['LiteralData']['ows:DataType']
                elif 'ows:AllowedValues' in item['LiteralData']:
                    input['type'] = '|'.join(
                        item['LiteralData']['ows:AllowedValues']['ows:Value'])
                else:
                    if '@ows:reference' in item['LiteralData']:
                        input['type'] = item['LiteralData']['@ows:reference']
                    else:
                        input['type'] = "text"
            inputList.append(input)
        process['metadata']['inputparametercount'] = len(inputList)
        process['inputs'] = inputList

        if 'ProcessOutputs' not in b['wps:ProcessDescriptions']['ProcessDescription'] or 'Output' not in b['wps:ProcessDescriptions']['ProcessDescription']['ProcessOutputs']:
            output = {'id': 0, 'identifier': '', 'name': '',
                      'value': '', 'description': '', 'type': ''}
            process['metadata']['outputparametercount'] = 1
            process['outputs'] = [output]
        else:
            outputList = []
            outputs = b['wps:ProcessDescriptions']['ProcessDescription']['ProcessOutputs']['Output']
            if isinstance(outputs, dict):
                outputs = [outputs]

            for i, item in enumerate(outputs):
                output = {
                    'id': i, 'identifier': item['ows:Identifier'],
                    'name': item['ows:Title'], 'value': "", 'description': item['ows:Title']
                }
                if 'ComplexOutput' in item:
                    if "text/xml" in str(item['ComplexOutput']['Default']['Format']['MimeType']) or "application/json" in str(item['ComplexOutput']['Default']['Format']['MimeType']):
                        output['type'] = "geom"
                    elif "image" in str(item['ComplexOutput']['Default']['Format']['MimeType']):
                        output['type'] = "coverage"
                    else:
                        output['type'] = item['ComplexOutput']['Default']['Format']

                if 'LiteralOutput' in item:
                    if item['LiteralOutput'] is None:
                        output['datatype'] = item['LiteralOutput']
                    else:
                        if 'ows:DataType' in item['LiteralOutput']:
                            output['type'] = item['LiteralOutput']['ows:DataType']
                        else:
                            output['type'] = item['LiteralOutput']
                outputList.append(output)

            process['metadata']['outputparametercount'] = len(outputList)
            process['outputs'] = outputList
        return process

    @staticmethod
    def getWfsCapabilities(url, limit=100):
        if url is None:
            url = "https://mara.rangelands.itc.utwente.nl/geoserver/ows?"
        if "?" not in url:
            url += "?"

        # Result of the GetCapabilities
        results = requests.get(url+"service=WFS&request=GetCapabilities")
        if results.text == "" or results.status_code > 200:
            return None
        features = []
        jsonResponse = xmltodict.parse(results.text)
        for row in jsonResponse['wfs:WFS_Capabilities']['FeatureTypeList']['FeatureType']:
            if len(features) > limit:
                continue

            feature = {}
            if "mapserv" in url:
                feature['url'] = url + "service=WFS&request=GetFeature&typeName=" + \
                    row['Name']+"&outputFormat=geojson&srsname=EPSG:3857"
            else:
                feature['url'] = url + "service=WFS&request=GetFeature&typeName=" + \
                    row['Name'] + "&outputFormat=application/json"
            feature['name'] = row['Name']
            feature['title'] = row['Title']
            feature['abstract'] = row['Abstract']
            feature['defaultCRS'] = row['DefaultCRS']
            features.append(feature)
        return features

    @staticmethod
    def getWcsCapabilities(url, limit=100):
        if url is None:
            url = "https://mara.rangelands.itc.utwente.nl/geoserver/ows?"
        if "?" not in url:
            url += "?"

        # Result of the GetCapabilities
        results = requests.get(
            url + "version=1.0.0&service=WCS&request=DescribeCoverage")
        if results.text == "" or results.status_code > 200:
            return None
        coverages = []
        jsonResponse = xmltodict.parse(results.text)
        for row in jsonResponse['wcs:CoverageDescription']['wcs:CoverageOffering']:
            if len(coverages) > limit:
                continue
            coverage = {}
            coverage['name'] = row['wcs:name']
            coverage['url'] = url + "version=2.0.0&service=WCS&request=GetCoverage&coverageId=" + \
                row['wcs:name'] + "&format=image/geotiff"
            coverage['title'] = row['wcs:label']
            coverage['abstract'] = row['wcs:description']
            coverage['defaultCRS'] = row['wcs:lonLatEnvelope']['@srsName']
            coverage['properties'] = {"min": [float((row['wcs:lonLatEnvelope']['gml:pos'][0]).split(" ")[0]), float((row['wcs:lonLatEnvelope']['gml:pos'][0]).split(
                " ")[1])], "max": [float((row['wcs:lonLatEnvelope']['gml:pos'][1]).split(" ")[0]), float((row['wcs:lonLatEnvelope']['gml:pos'][1]).split(" ")[1])]}
            coverages.append(coverage)
        return coverages

    @staticmethod
    def getSosCapabilities(url, limit=100):
        if url is None:
            # url = "https://pegelonline.wsv.de/webservices/gis/gdi-sos?"
            url = "https://gip.itc.utwente.nl/services/ogc/sos.py?"

        if "?" not in url:
            url += "?"

        # Result of the GetCapabilities
        results = requests.get(
            url + "service=SOS&request=GetCapabilities")
        if results.text == "" or results.status_code > 200:
            return None
        root = fromstring(results.text)
        colors = ['#e41a1c', '#377eb8', '#4daf4a',
                  '#984ea3', '#4dacff', '#f47671', '#0088ff']
        count = 0
        observations = []
        for child in root[4][0]:
            if len(observations) > limit:
                continue
            if "sos.py" in url or list(child.attrib.values())[0] == "LUFTTEMPERATUR" or list(child.attrib.values())[0] == "WASSERTEMPERATUR" or list(child.attrib.values())[0] == "LUFTFEUCHTE":
                feature = {}
                feature["offering"] = list(child.attrib.values())[0]
                feature["color"] = colors[count]
                featuresOfInterest = []
                for item in child:
                    beginTime = ""
                    endTime = ""
                    if "time" in item.tag:
                        beginTime = item[0][0].text
                        endTime = item[0][1].text
                        feature["beginTime"] = beginTime+"T00:00:00"
                        feature["endTime"] = str(
                            datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                        if "sos.py" in url:
                            feature["url"] = url + "service=SOS&request=GetObservation&version=1.0.0&observedProperty=" + \
                                feature["offering"].capitalize() + "&offering=" + feature["offering"]+"&eventTime=" + \
                                beginTime+"/" + \
                                str(datetime.datetime.now().strftime(
                                    '%Y-%m-%dT%H:%M:%S'))
                        else:
                            feature["url"] = url + "service=SOS&request=GetObservation&version=1.0.0&observedProperty=" + \
                                feature[
                                "offering"].capitalize() + "&offering=" + feature[
                                "offering"] + "&responseformat=text/xml;subtype=%22om/1.0.0%22"+"&eventTime="+beginTime+"/"+str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

                    if "observedProperty" in item.tag:
                        observedProperty = list(item.attrib.values())[0]
                        feature["name"] = observedProperty
                        if "sos.py" in url:
                            feature["observedProperty"] = "aa:" + \
                                observedProperty
                        else:
                            feature["observedProperty"] = "52n:" + \
                                observedProperty

                    if "featureOfInterest" in item.tag:
                        featureOfInterest = list(item.attrib.values())[0]
                        procedure = observedProperty + "-" + featureOfInterest
                        feature["procedure"] = procedure
                        if "sos.py" in url:
                            describeURL = url + 'service=SOS&request=DescribeSensor&procedure=' + procedure
                        else:
                            describeURL = url + 'service=SOS&request=DescribeSensor&procedure=' + \
                                procedure + '&outputformat=text/xml;subtype="sensorML/1.0.1"&version=1.0.0'

                        result = requests.get(describeURL)
                        xmlstring = result.text
                        if result.status_code < 300:
                            xml = fromstring(xmlstring)
                            for x in xml[0][0]:
                                if "position" in x.tag:
                                    coord = [float(x[0][0][0][0][0][1].text), float(
                                        x[0][0][0][1][0][1].text)]
                                    coords = Util.coordinateTransform(coord, int(
                                        x[0].attrib['referenceFrame'].split("EPSG::")[1]), 3857)
                                    featuresOfInterest.append({
                                        "name": featureOfInterest,
                                        "abstract": xml[0][0][0].text,
                                        "location": coords,
                                        "defaultCRS": x[0].attrib['referenceFrame'],
                                        "beginTime": feature["beginTime"]+"T00:00:00",
                                        "endTime": feature["endTime"],
                                        "url": url + "service=SOS&request=GetObservation&procedure="+procedure+"&version=1.0.0&offering="+feature["offering"]+"&observedProperty="+observedProperty+"&featureOfInterest="+featureOfInterest+'&responseformat=text/xml;subtype=%22om/1.0.0%22'
                                    })
                                    feature["defaultCRS"] = x[0].attrib['referenceFrame']
                        feature["featuresOfInterest"] = featuresOfInterest
                observations.append(feature)
        return observations

    @staticmethod
    def getSosObservations(url):
        if url is None:
            url = "https://gip.itc.utwente.nl/services/ogc/sos.py?service=SOS&request=GetObservation&version=1.0.0&observedProperty=Rainfall_sensors&offering=rainfall_SENSORS&responseformat=text/xml;subtype=%22om/1.0.0%22"

        # Result of the GetObservations
        results = requests.get(url)
        if results.text == "" or results.status_code > 200:
            return None
        obersevations = []
        chartData = []
        xmlstring = results.text
        root = fromstring(xmlstring)
        for child in root[1][0][4][0]:
            if "values" not in child.tag:
                continue
            values = child.text.split(";")
            for item in values:
                if item == "":
                    continue
                item = item.split(",")
                date = item[0]
                if "\n" in date:
                    date = date.split("\n")[1]
                date = datetime.datetime.strptime(
                    date.split(".")[0], '%Y-%m-%dT%H:%M:%S')
                pattern = '%Y-%m-%d %H:%M:%S'
                epoch = int(time.mktime(time.strptime(
                    date.strftime(pattern), pattern)))

                obersevations.append({
                    "timestamp": epoch,
                    "sensor": item[1],
                    "value": item[2]
                })
                chartData.append([epoch*1000, float(item[2])])
        return {"obersevations": obersevations, "chartdata": chartData}

    @staticmethod
    def coordinateTransform(coord, fromSRID=4326, toSRID=32736):
        point = Point(coord[0], coord[1], srid=fromSRID)
        point.transform(toSRID)
        return [point.x, point.y]

    @staticmethod
    def jsonTransform(geojson, toSRID=3857):
        crs = geojson.get("crs")
        if crs:
            srid = crs.get('properties').get('name').split(":")[-1]
            crs['properties']['name'] = crs.get('properties').get(
                'name').replace(srid, str(toSRID))
            geojson['crs'] = crs
        else:
            srid = 4326
            geojson['crs'] = {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::4326"
                }
            }

        if int(srid) == int(toSRID):
            return geojson

        transformed_features = []
        features = geojson.get("features")
        for feature in features:
            geometry = GEOSGeometry(json.dumps(
                feature.get("geometry")), srid=int(srid))
            geometry.transform(toSRID)
            feature['geometry'] = geometry.json
            transformed_features.append(feature)

        geojson['features'] = transformed_features
        return geojson

    @staticmethod
    def executeWorkflow(workflow):
        operations = workflow["operations"]
        orderedIDs = Util.getExecutionOrder(workflow)
        outputs = {}
        j = 1
        result = []
        for id in orderedIDs:
            operation = Util.getOperationByID(id, operations)
            if len(outputs) > 0:
                for i in range(0, len(operation["inputs"])):
                    if "_to_" in operation["inputs"][i]["value"]:
                        value = operation["inputs"][i]["value"].split("_to_")
                        operation["inputs"][i]["value"] = outputs[value[0]][0]
            output = Util.executeOperation(operation)
            outputs[str(id)] = [output]
            result.append(
                {"type": operation["outputs"][0]["type"], "data": output, "id": id})
            j = j + 1
        return result

    @staticmethod
    def getExecutionOrder(workflow):
        operations = workflow["operations"]
        connections = workflow["connections"]
        nodeIDs = set()
        operIDs = set()
        for operation in operations:
            operIDs.add(operation["id"])
            for connection in connections:
                if connection["fromOperationID"] == operation["id"]:
                    nodeIDs.add(operation["id"])
                    break

        leafIDs = list(operIDs.difference(nodeIDs))
        orderID = []
        orderID.extend(leafIDs)
        for id in leafIDs:
            Util.recursiveF(connections, orderID, id)
        return orderID

    @staticmethod
    def recursiveF(connections, orderID, id):
        for connection in connections:
            if connection["toOperationID"] == id:
                if connection["fromOperationID"] in orderID:
                    orderID.remove(connection["fromOperationID"])
                orderID.insert(0, connection["fromOperationID"])
                Util.recursiveF(connections, orderID,
                                connection["fromOperationID"])
        return orderID

    @staticmethod
    def getOperationByID(id, operations):
        oper = []
        for operation in operations:
            if str(operation["id"]) == str(id):
                oper = operation
                break
        return oper

    @staticmethod
    def executeOperation(operation):
        output = ""
        if operation["metadata"]["resource"] == "WPS":
            if operation['outputs'][0]['type'] == "geom":
                output = Util.executeWPS(operation, 'application/json')
                if isinstance(output, dict):
                    output['crs'] = {
                        "type": "name",
                        "properties": {
                            "name": "urn:ogc:def:crs:EPSG::3857"
                        }
                    }
            elif operation['outputs'][0]['type'] == "coverage":
                output = Util.executeWPS(operation, 'image/tiff')
            else:
                output = Util.executeWPS(operation)

        if operation["metadata"]["resource"] == "RESTful WPS":
            output = Util.executeWPSREST(operation)

        if operation["metadata"]["resource"] == "REST":
            output = Util.executeREST(operation)
        if operation["metadata"]["resource"] == "ILWIS":
            output = Util.executeILWIS(operation)
            if output is not None:
                # Change this URL when using another server for ILWIS
                output = settings.ILWIS_API + \
                    json.loads(output)["path"]

        if operation["metadata"]["resource"] == "GeoServer":
            output = Util.publishRaster(operation)
            if output:
                output = output
        return output

    @staticmethod
    def executeREST(operation):
        headers = {'content-type': 'application/json'}
        results = requests.post(
            operation["metadata"]["url"], data=json.dumps(operation), headers=headers)
        if results.text == "":
            results = []
        else:
            results = json.loads(results.text)
        return results

    @staticmethod
    def executeWPS(operation, type='application/json'):
        root = Util.wpsHead()
        label = operation['metadata']['label']
        ows_Identifier = SubElement(root, 'ows:Identifier')
        ows_Identifier.text = label
        wps_DataInputs = SubElement(root, 'wps:DataInputs')
        for input in operation['inputs']:
            if len(input['value']) < 1:
                continue
            if input['type'] == 'geom':
                wps_Input = SubElement(wps_DataInputs, 'wps:Input')
                ows_Identifier = SubElement(wps_Input, 'ows:Identifier')
                ows_Identifier.text = input['identifier']
                if input['url'] == "":
                    wps_Data = SubElement(wps_Input, 'wps:Data')
                    wps_ComplexData = SubElement(
                        wps_Data, 'wps:ComplexData')
                    wps_ComplexData.set('mimeType', 'application/json')
                    wps_ComplexData.text = input['value']
                    if isinstance(input['value'], dict):
                        wps_ComplexData.text = json.dumps(input['value'])
                else:
                    wps_Reference = SubElement(wps_Input, 'wps:Reference')
                    wps_Reference.set('mimeType', 'application/json')
                    wps_Reference.set('xlink:href', input['value'])
                    wps_Reference.set('method', 'GET')
            elif input['type'] == 'coverage':
                wps_Input = SubElement(wps_DataInputs, 'wps:Input')
                ows_Identifier = SubElement(wps_Input, 'ows:Identifier')
                ows_Identifier.text = input['identifier']
                wps_Data = SubElement(wps_Input, 'wps:Data')
                wps_ComplexData = SubElement(wps_Data, 'wps:ComplexData')
                wps_ComplexData.set('mimeType', 'image/tiff')
                wps_ComplexData.text = input['value']
            else:
                wps_Input = SubElement(wps_DataInputs, 'wps:Input')
                ows_Identifier = SubElement(wps_Input, 'ows:Identifier')
                ows_Identifier.text = input['identifier']
                wps_Data = SubElement(wps_Input, 'wps:Data')
                wps_LiteralData = SubElement(wps_Data, 'wps:LiteralData')
                wps_LiteralData.text = input['value']
        wps_ResponseForm = SubElement(root, 'wps:ResponseForm')
        wps_RawDataOutput = SubElement(wps_ResponseForm, 'wps:RawDataOutput')
        wps_RawDataOutput.set('mimeType', type)
        ows_Identifier = SubElement(wps_RawDataOutput, 'ows:Identifier')
        ows_Identifier.text = 'result'
        url = operation['metadata']['url']
        headers = {'content-type': 'text/xml'}
        response = requests.post(
            url, data=Util.prettify(root), headers=headers)
        if response.status_code < 300:
            return response.json() if operation['outputs'][0]['type'] == 'geom' else response.text

    @staticmethod
    def executeWPSREST(operation):
        body = {}
        body["Identifier"] = operation['metadata']['label']
        inputs = []
        for input in operation["inputs"]:
            if input["type"] == "geom":
                if input["url"] == "" and input["value"] != "":
                    inputs.append({
                        "ComplexData": {
                            "_mimeType": "application/vnd.geo+json",
                            "_text": json.dumps(input["value"])
                        },
                        "_id": input["identifier"]
                    })
                else:
                    inputs.append({
                        "Reference": {
                            "_mimeType": "application/vnd.geo+json",
                            "_href": input["url"]
                        },
                        "_id": input["identifier"]
                    })
            elif input["type"] == "coverage":
                inputs.append({
                    "Reference": {
                        "_mimeType": "application/geotif",
                        "_href": input["url"]
                    },
                    "_id": input["identifier"]
                })
            else:
                inputs.append({
                    "LiteralData": {
                        "_text": str(input["value"])
                    },
                    "_id": input["identifier"]
                })
        outputs = []
        for output in operation["outputs"]:
            if output["type"] == "geom":
                outputs.append({
                    "_mimeType": "application/vnd.geo+json",
                    "_id": output["identifier"],
                    "_transmission": "value"
                })
            else:
                outputs.append({
                    "_mimeType": "text/plain",
                    "_id": output["identifier"],
                    "_transmission": "value"
                })
        body["Input"] = inputs
        body["output"] = outputs
        body["_version"] = "2.0.0"
        body["_service"] = "WPS"
        wpsExecuteBody = {}
        wpsExecuteBody["Execute"] = body
        headers = {'content-type': 'application/json'}

        r = requests.post(operation['metadata']['url'] + "/jobs",
                          data=json.dumps(wpsExecuteBody), headers=headers)
        url = r.headers["Location"]
        response = requests.get(url)
        statusInfo = response.json()["StatusInfo"]
        status = statusInfo["Status"]
        while status == "Running":
            r = requests.get(url)
            statusInfo = response.json()["StatusInfo"]
            status = statusInfo["Status"]

        if status == "Failed":
            return "Failed"
        else:
            responseOutput = statusInfo["Output"]
            response = requests.get(responseOutput)
            return response.json()["Result"]["Output"][0]

    @staticmethod
    def executeILWIS(operation):
        label = operation['metadata']['label']
        maps = []
        texts = []
        for input in operation['inputs']:
            if input['type'] == 'geom' or input['type'] == 'coverage':
                maps.append(quote(input['value']))
            else:
                texts.append(input['value'])
        maps = ";".join(maps)
        texts = "$".join(texts)
        inputs = quote(maps + "textinputs" + texts)
        results = requests.get(
            operation["metadata"]["url"] + "/execute/" + inputs + "/" + label)
        if results.text == "":
            results = []
        else:
            results = results.text
        return results

    @staticmethod
    def bpmnHead():
        root = Element('bpmn2:definitions')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xmlns:camunda', 'http://camunda.org/schema/1.0/bpmn')
        root.set('xmlns:bpmndi', 'http://www.omg.org/spec/BPMN/20100524/DI')
        root.set('xmlns:bpmn2', 'http://www.omg.org/spec/BPMN/20100524/MODEL')
        root.set('xmlns:dc', 'http://www.omg.org/spec/DD/20100524/DC')
        root.set('xmlns:di', 'http://www.omg.org/spec/DD/20100524/DI')
        root.set('xmlns:ext', 'http://org.eclipse.bpmn2/ext')
        root.set('xmlns:xs', 'http://www.w3.org/2001/XMLSchema')
        root.set('id', 'Definitions_1')
        root.set('exporter', 'org.eclipse.bpmn2.modeler.core')
        root.set('exporterVersion', '2018.2019_thesis')
        root.set('targetNamespace', 'http://org.eclipse.bpmn2/default/process')
        return root

    @staticmethod
    def wpsHead():
        root = Element('wps:Execute')
        root.set('service', 'WPS')
        root.set('version', '1.0')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xmlns', 'http://www.opengis.net/wps/1.0.0')
        root.set('xmlns:wfs', 'http://www.opengis.net/wfs')
        root.set('xmlns:wps', 'http://www.opengis.net/wps/1.0.0')
        root.set('xmlns:ows', 'http://www.opengis.net/ows/1.1')
        root.set('xmlns:gml', 'http://www.opengis.net/gml')
        root.set('xmlns:ogc', 'http://www.opengis.net/ogc')
        root.set('xmlns:wcs', 'http://www.opengis.net/wcs/1.1.1')
        root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        root.set('xsi:schemaLocation',
                 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd')
        return root

    def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    @staticmethod
    def publishRaster(operation):
        file = Util.downloadRasterFile(operation["inputs"][0]["value"])
        file = file["file"]
        base = os.path.basename(file)
        projection = "EPSG:32736"
        if os.path.exists(file):
            with rasterio.open(file) as ds:
                projection = ds.crs
                host = quote(operation["inputs"][1]["value"])
                host = operation["inputs"][1]["value"]
                workspace = operation["inputs"][2]["value"]
                if workspace is None or workspace == "":
                    workspace = "maris_mamase"
                username = operation["inputs"][3]["value"]
                password = operation["inputs"][4]["value"]

                sld_file = Util.generateSLD(file, os.path.splitext(base)[0])

                config_file = settings.MEDIA_ROOT + os.path.sep + \
                    Util.id_generator() + str(int(time.time())) + ".json"
                with open(config_file, "w") as f:
                    f.write(json.dumps({
                        "geoserver": [
                            {
                                "host": host,
                                "port": 80,
                                "user": username,
                                "password": password
                            }
                        ],
                        "developer": "robertohuru@gmail.com"
                    }))

                publishcommand = f"java -jar {settings.GEOJAR_FILE} {workspace} {file} {sld_file} {projection} {config_file} No"
                os.system(publishcommand)
                extent = ds.bounds
                southwest = [extent.left, extent.bottom]
                northeast = [extent.right, extent.top]

                southwest = Util.coordinateTransform(
                    southwest, projection.to_epsg(), toSRID=3857)
                northeast = Util.coordinateTransform(
                    northeast, projection.to_epsg(), toSRID=3857)
                extent = southwest + northeast
                os.remove(sld_file)
                os.remove(file)
                os.remove(config_file)
                return {"extent": extent, "layer": workspace + ":" + os.path.splitext(base)[0]}

    @staticmethod
    def downloadRasterFile(url):
        path = settings.MEDIA_ROOT + os.path.sep + \
            Util.id_generator() + str(int(time.time())) + ".tif"
        urllib.request.urlretrieve(url, path)
        return {"file": path}

    @staticmethod
    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        """
        Generate unique names for files
        :param chars:
        :return:
        """
        file = ''.join(random.choice(chars) for _ in range(size))
        return ("ds" + file).lower()

    @staticmethod
    def is_url(url, qualifying=None):
        qualifying = min_attributes if qualifying is None else qualifying
        token = urlparse(url)
        return all([getattr(token, qualifying_attr)
                    for qualifying_attr in qualifying])

    @staticmethod
    def generateSLD(file, sldName):
        with rasterio.open(file) as ds:
            pixArr = ds.read(1)
            pixArr = pixArr.flatten()
            root = Element('StyledLayerDescriptor')
            root.set('version', '1.0.0')
            root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            root.set('xmlns', 'http://www.opengis.net/sld')
            root.set('xmlns:ogc', 'http://www.opengis.net/ogc')
            root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
            root.set('xsi:schemaLocation',
                     'http://www.opengis.net/sld StyledLayerDescriptor.xsd')
            namedLayer = SubElement(root, 'NamedLayer')
            name = SubElement(namedLayer, 'Name')
            name.text = "raster_style"
            userStyle = SubElement(namedLayer, 'UserStyle')
            title = SubElement(userStyle, 'Title')
            title.text = "raster_style"
            abstract = SubElement(userStyle, "Abstract")
            abstract.text = "Automatically generated raster styles"
            featureTypeStyle = SubElement(userStyle, 'FeatureTypeStyle')
            rule = SubElement(featureTypeStyle, "Rule")
            name = SubElement(rule, "Name")
            name.text = "Rule1"
            title = SubElement(rule, "Title")
            title.text = "Raster_style"
            abstract = SubElement(rule, "Abstract")
            abstract.text = "Raster with different classes"
            rasterSymbolizer = SubElement(rule, "RasterSymbolizer")
            opacity = SubElement(rasterSymbolizer, "Opacity")
            opacity.text = "1"
            colorMap = SubElement(rasterSymbolizer, "ColorMap")
            colorMap.set("type", "intervals")
            pixArr = set(pixArr)
            pixArr = list(pixArr)
            pixArr.sort()
            pixArr = np.array(pixArr)
            n = int(len(pixArr) / 7)
            colors = ["#FFFFFF", "#8c510a", "#d8b365", "#f6e8c3",
                      "#f5f5f5", "#c7eae5", "#5ab4ac", "#01665e"]
            divisions = pixArr[list(range(0, len(pixArr) - 1, n))]
            divisions[divisions == -np.inf] = math.floor(pixArr[1])
            divisions[divisions == np.inf] = math.ceil(pixArr[-2])
            max = np.nanmax(divisions)
            for idx, div in enumerate(divisions):
                colorMapEntry = SubElement(colorMap, "ColorMapEntry")
                colorMapEntry.set("color", colors[idx])
                colorMapEntry.set("quantity", str(div))
                colorMapEntry.set("label", str(div))
                colorMapEntry.set("opacity", "0" if idx == 0 else "1")

            colorMapEntry = SubElement(colorMap, "ColorMapEntry")
            colorMapEntry.set("color", "#003300")
            colorMapEntry.set("quantity", str(max))
            colorMapEntry.set("label", str(max))
            colorMapEntry.set("opacity", "1")
            xml = Util.prettify(root)
            sldFile = open(settings.MEDIA_ROOT +
                           os.path.sep + sldName + ".xml", "w")
            sldFile.write(xml)
            sldFile.close()
            return settings.MEDIA_ROOT + os.path.sep + sldName + ".xml"
