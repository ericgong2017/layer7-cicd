#!/usr/bin/python3

import os
import argparse
import pathlib
import subprocess

from prettytable import PrettyTable

parser = argparse.ArgumentParser(description="Script to list and export layer 7 services...because why not")
parser.add_argument("-z", "--argFile", required=True, help="The properties file for reading args.")
parser.add_argument("-i", "--id", required=True, help="id to export")
parser.add_argument("-o", "--output", required=True, help="output path to export to, this should be directory path until the name of the provider")
parser.add_argument("-n", "--name", required=True, help="service file name to save as, .xml will be appended to the file so don't include this")
parser.add_argument("-p", "--plaintextEncryptionPassphrase", required=True, help="Plaintext passphrase for encryption, Use the prefix, '@file:' to read passphrase from a file.")
parser.add_argument("-g", "--gateway", required=True, help="Name of the gateway")
parser.add_argument("-a", "--action", required=True, help="Mapping action: [New, Update, Existing, ForceNew,Delete, Ignore, NewOrExisting, NewOrUpdate,DeleteOrIgnore]")
args = parser.parse_args()

# Create directory if it doesn't exist
#conf_dir = args.output + "/" + args.gateway + "/conf/"
#doc_dir = args.output + "/" + args.gateway + "/doc/"
#src_dir = args.output + "/" + args.gateway + "/src/"

conf_dir = args.output + "/" + args.name + "/" + args.gateway + "/conf/"
doc_dir = args.output + "/" + args.name + "/" + args.gateway + "/doc/"
src_dir = args.output + "/" + args.name + "/" + args.gateway + "/src/"

pathlib.Path(conf_dir).mkdir(parents=True, exist_ok=True)
pathlib.Path(doc_dir).mkdir(parents=True, exist_ok=True)
pathlib.Path(src_dir).mkdir(parents=True, exist_ok=True)

# Run the export
gmu_migrateOut = subprocess.Popen("gmu migrateOut --argFile " + args.argFile + " --service " + args.id + " --plaintextEncryptionPassphrase " + args.plaintextEncryptionPassphrase + " --dest " + src_dir + args.name + ".xml", stdout=subprocess.PIPE, shell=True)
(output, err) = gmu_migrateOut.communicate()
gmu_migrateOut_status = gmu_migrateOut.wait()

# Template the service
gmu_template_cmd = "gmu template --bundle " + src_dir + args.name + ".xml" + " --template " + conf_dir + args.name + ".properties"
gmu_template = subprocess.Popen(gmu_template_cmd, stdout=subprocess.PIPE, shell=True)
gmu_template_status = gmu_template.wait()

# Add folder property
service_path = os.popen("gmu browse --argFile " + args.argFile + " --id " + args.id + " --recursive --showIds").read()
service_path = service_path[service_path.rindex("/")]

service_properties = open(conf_dir + "/" + args.name + ".properties", "a")
service_properties.write("service.folderpath=/" + service_path)
service_properties.close()

# Create mappings file
gmu_mapping = os.popen("gmu manageMappings --type SERVICE" + " --action " + args.action +  " --bundle " + src_dir + args.name + ".xml --outputFile " + src_dir + args.name + "-mapping.xml")
