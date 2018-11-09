#!/usr/bin/python3


import xml.etree.ElementTree as ET
import requests


# Get the buildingblock policies based on their folder id
def getBuildingBlocks(xmlContents, namespaces, folderId):
    tree = ET.parse(xmlContents)
    root = tree.getroot()

    policyDetail = root.findall("l7:References/l7:Item/l7:Resource/l7:Policy/l7:PolicyDetail", namespaces)
    policies = {}
    for idx, detail in enumerate(policyDetail):
        folderId = detail.attrib.get("folderId")
        policyId = detail.attrib.get("id")
        name = detail.find("l7:Name", namespaces).text

        details = [name, folderId]
        policies[policyId] = details

    return policies


# Get the folder id
def getFolderId(username, password, restmanUrl, folderName):
    foldersEndpoint = restmanUrl + "/1.0/folders?name=" + folderName
    folder = requests.get(url=foldersEndpoint, auth=(username, password), verify=False)
    return folder.text


# Gets the bundle
def getBundle(username, password, restmanUrl, resourceType, id):
    endpoint = restmanUrl + "/1.0/bundle"
    parameters = {resourceType: id}
    bundle = requests.get(url=endpoint, auth=(username, password), params=parameters, verify=False)
    return bundle.text


# Adds mapping for building block policies for a given folder. This will create any folders if they are non existant
def extendMapping(buildingBlockPolicies, xmlContents, namespaces):
    tree = ET.parse(xmlContents)
    root = tree.getroot()
    bundle = ET.ElementTree()

    mappings = root.findall("l7:Mappings/l7:Mapping", namespaces)

    for mapping in mappings:
        for prefix, url in namespaces.items():
            ET.register_namespace(prefix, url)
        srcId = mapping.get("srcId")
        if(srcId in buildingBlockPolicies):
            properties = ET.Element("l7:Properties")
            propertiesMapBy = ET.SubElement(properties, "l7:Property")
            stringValueMapBy = ET.SubElement(propertiesMapBy, "l7:StringValue")
            propertiesMapBy.set("key", "MapBy")
            stringValueMapBy.text = "path"

            propertiesMapTo = ET.SubElement(properties, "l7:Property")
            stringValueMapTo = ET.SubElement(propertiesMapTo, "l7:StringValue")
            propertiesMapTo.set("key", "MapTo")
            stringValueMapTo.text = "/buildingBlocks/" + buildingBlockPolicies[srcId][0]
            mapping.insert(0, properties)

    bundle._setroot(root)
    return bundle


# def getServices(username, password, restmanUrl):

namespaces = {"l7": "http://ns.l7tech.com/2010/04/gateway-management"}
folders = ET.parse("dep.xml")
root = folders.getroot()

refdict = {}
references = root.findall("l7:Resource/l7:DependencyList/l7:Reference/l7:Dependencies/l7:Dependency", namespaces)
for reference in references:
    if (reference.find("l7:Type", namespaces).text == "FOLDER"):
        rId = reference.find("l7:Id", namespaces).text
        rName = reference.find("l7:Name", namespaces).text
        refdict[rId] = rName

fold = root.findall("l7:Resource/l7:DependencyList/l7:Dependencies/l7:Dependency", namespaces)

controlType = "FOLDER"
for k,v in refdict.items():
    while controlType == "FOLDER":
        for f in fold:
            fName = f.find("l7:Name", namespaces).text
            fId = f.find("l7:Id", namespaces).text
            fType = f.find("l7:Type", namespaces).text
            controlType = fType
            
            nested = f.findall("l7:Dependencies/l7:Dependency", namespaces)
            for n in nested:
                nName = n.find("l7:Name", namespaces).text
                nId = n.find("l7:Id", namespaces).text
                nType = n.find("l7:Type", namespaces).text
                if (nType == "SERVICE"):
                    print(v + "/" + fName + "/" + nName)