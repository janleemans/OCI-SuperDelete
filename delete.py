#Use with PYTHON3!
import sys, getopt
import oci
from ocimodules.functions import *
from ocimodules.EdgeServices import *
from ocimodules.ObjectStorage import *
from ocimodules.Instances import *
from ocimodules.Database import *
from ocimodules.IAM import *
from ocimodules.VCN import *
from ocimodules.BlockStorage import *
from ocimodules.ResourceManager import *
from ocimodules.FileStorage import *
from ocimodules.Monitoring import *
from ocimodules.Notifications import *
from ocimodules.Autoscaling import *
from ocimodules.FunctionsService import *
from ocimodules.DataScience import *
from ocimodules.OKE import *
from ocimodules.kms import *
from ocimodules.Nosql import *
from ocimodules.datacatalog import *
from ocimodules.DigitalAssistant import *
from ocimodules.APIGateway import *
from ocimodules.Analytics import *
from ocimodules.MySQL import *
from ocimodules.Logging import *
from ocimodules.Integration import *
from ocimodules.Blockchain import *
from ocimodules.APM import *
from ocimodules.Artifacts import *
from ocimodules.Events import *
from ocimodules.VulnerabilityScanning import *
from ocimodules.Bastion import *
import logging

########## Configuration ####################
# Specify your config file
configfile = "~/.oci/config"  # Linux
#configfile = "\\Users\\username\\.oci\\config"  # Windows

# Specify the DEFAULT compartment OCID that you want to delete, Leave Empty for no default
DeleteCompartmentOCID = ""

# Search for resources in regions, this is an Array, so you can specify multiple regions:
# If no regions specified, it will be all subscribed regions.
# regions = ["eu-frankfurt-1", "eu-amsterdam-1"]
regions = ["uk-london-1"]

# Specify your home region
homeregion = "eu-frankfurt-1"
#############################################

clear()

# Minimum version requirements for OCI SDK
mv1 = 2
mv2 = 41
mv3 = 1
v1,v2,v3 = oci.__version__.split(".")
print ("OCI SDK Version: {}".format(oci.__version__))
outdated = False
if int(v1) <= mv1:
    if int(v2) < mv2:
        outdated = True
    elif int(v2) > mv2:
        outdated = False
    else:
        if int(v3) < mv3:
            outdated = True
        else:
            outdated = False
else:
    outdated = False

if outdated:
    print ("Your version ({}.{}.{}) of the OCI SDK is out-of-date. Please first upgrade your OCI SDK Library bu running the command:".format(v1,v2,v3))
    print ("pip install --upgrade oci")
    quit()
debug = False

class MyWriter:

    filename = "log.txt"

    def __init__(self, stdout, filename):
        self.stdout = stdout
        self.filename = filename
        self.logfile = open(self.filename, "a")

    def write(self, text):
        self.stdout.write(text)
        self.logfile.write(text)

    def close(self):
        self.stdout.close()
        self.logfile.close()

    def flush(self):
        self.logfile.close()
        self.logfile = open(self.filename, "a")


writer = MyWriter(sys.stdout, 'log.txt')
sys.stdout = writer

try:
    opts, args = getopt.getopt(sys.argv[1:], "c:", ["compid="])
except getopt.GetoptError:
    print ("delete.py -c <compartmentID>")
    sys.exit(2)

for opt, arg in opts:
    print ("{} - {}".format(opt,arg))
    if opt == "-c":
        DeleteCompartmentOCID = arg

if DeleteCompartmentOCID =="":
    print ("No compartment specified")
    sys.exit(2)

config = oci.config.from_file(configfile)

if debug:
    config['log_requests'] = True
    logging.basicConfig()
    logging.getLogger('oci').setLevel(logging.DEBUG)

print ("\n--[ Login check and getting all compartments from starting compartment ]--")
compartments = Login(config, DeleteCompartmentOCID)

if len(regions) == 0:
    # No specific region specified, getting all subscribed regions.
    regions=SubscribedRegions(config)

processCompartments=[]

print ("\n--[ Compartments to process ]--")

# Add all active compartments, but exclude the ManagementCompartmentForPaas (as this is locked compartment)
for compartment in compartments:
    if compartment.lifecycle_state== "ACTIVE" and compartment.name != "ManagedCompartmentForPaaS":
        processCompartments.append(compartment)
        print (compartment.name)


confirm = input ("\ntype yes to delete all contents from these compartments: ")

if confirm == "yes":

    for region in regions:

        print ("============[ Deleting resources in {} ]================".format(region))
        config["region"] = region

        print ("\n--[ Moving and Scheduling KMS Vaults for deletion ]--")
        DeleteKMSvaults(config, processCompartments, DeleteCompartmentOCID)

        print ("\n--[ Deleting Vulnerability Scanning Services ]--")
        DeleteScanResults(config, processCompartments)
        DeleteTargets(config, processCompartments)
        DeleteRecipes(config, processCompartments)

        print ("\n--[ Deleting Bastion Services ]--")
        DeleteBastion(config, processCompartments)

        print ("\n--[ Deleting Edge Services ]--")
        DeleteWAFs(config,processCompartments)
        DeleteHTTPHealthchecks(config, processCompartments)
        DeletePINGHealthchecks(config, processCompartments)
        DeleteTrafficSteeringsAttachments(config, processCompartments)
        DeleteTrafficSteerings(config, processCompartments)
        DeleteZones(config, processCompartments)
        DeleteDNSViews(config, processCompartments)

        print ("\n--[ Deleting Object Storage ]--")
        DeleteBuckets(config, processCompartments)

        print ("\n--[ Deleting OKE Clusters ]--")
        DeleteClusters(config, processCompartments)

        print ("\n--[ Deleting Repositories ]--")
        DeleteContainerRepositories(config, processCompartments)
        DeleteRepositories(config, processCompartments)

        print ("\n--[ Deleting Auto Scaling Configurations ]--")
        DeleteAutoScalingConfigurations(config, processCompartments)

        print ("\n--[ Deleting Compute Instances ]--")
        DeleteInstancePools(config,processCompartments)
        DeleteInstanceConfigs(config, processCompartments)
        DeleteInstances(config,processCompartments)
        DeleteImages(config, processCompartments)
        DeleteBootVolumes(config, processCompartments)
        DeleteBootVolumesBackups(config, processCompartments)
        DeleteDedicatedVMHosts(config, processCompartments)

        print ("\n--[ Deleting DataScience Components ]--")
        DeleteNotebooks(config, processCompartments)
        DeleteModelDeployments(config, processCompartments)
        DeleteModels(config, processCompartments)
        DeleteProjects(config, processCompartments)

        print("\n--[ Deleting Application Functions ]--")
        DeleteApplications(config, processCompartments)

        print("\n--[ Deleting Deployments ]--")
        DeleteDeployments(config, processCompartments)

        print("\n--[ Deleting APIs ]--")
        DeleteAPIs(config, processCompartments)

        print("\n--[ Deleting API Gateways ]--")
        DeleteAPIGateways(config, processCompartments)
        DeleteCertificates(config, processCompartments)

        print ("\n--[ Deleting Database Instances ]--")
        DeleteDBCS(config,processCompartments)
        DeleteAutonomousDB(config,processCompartments)
        DeleteDBBackups(config, processCompartments)

        print("\n--[ Deleting MySQL Database Instances ]--")
        DeleteMySQL(config, processCompartments)

        print("\n--[ Deleting Nosql tables ]--")
        DeleteNosql(config, processCompartments)

        print("\n--[ Deleting Data Catalogs ]--")
        DeleteDataCatalog(config, processCompartments)

        print("\n--[ Deleting Digital Assistants ]--")
        DeleteDigitalAssistant(config, processCompartments)

        print("\n--[ Deleting Analytics ]--")
        DeleteAnalytics(config, processCompartments)
        DeleteStreams(config, processCompartments)
        DeleteStreamPools(config, processCompartments)
        DeleteConnectHarnesses(config, processCompartments)
        DeleteServiceConnectors(config, processCompartments)

        print("\n--[ Deleting Integration ]--")
        DeleteIntegration(config, processCompartments)

        print("\n--[ Deleting Blockchain ]--")
        DeleteBlockchain(config, processCompartments)

        print ("\n--[ Deleting Resource Manager Stacks ]--")
        DeleteStacks(config, processCompartments)

        print ("\n--[ Deleting Block Volumes ]--")
        DeleteVolumeGroups(config, processCompartments)
        DeleteVolumeGroupBackups(config, processCompartments)
        DeleteVolumes(config, processCompartments)
        DeleteBlockVolumesBackups(config, processCompartments)

        print ("\n--[ Deleting FileSystem and Mount Targets ]--")
        DeleteMountTargets(config, processCompartments)
        DeleteFileStorage(config, processCompartments)

        print ("\n--[ Deleting VCNs ]--")
        DeleteVCN(config, processCompartments)

        print ("\n--[ Deleting Alarms ]--")
        DeleteAlarms(config, processCompartments)

        print ("\n--[ Deleting Notifications ]--")
        DeleteNotifications(config, processCompartments)

        print ("\n--[ Deleting Events ]--")
        DeleteEvents(config, processCompartments)

        print ("\n--[ Deleting Policies ]--")
        DeletePolicies(config, processCompartments)

        print("\n--[ Deleting Log Groups ]--")
        DeleteLogGroups(config, processCompartments)

        print("\n--[ Deleting Application Performance Monitoring ]--")
        DeleteAPM(config, processCompartments)

        print("\n--[ Deleting Tag Namespaces ]--")
        DeleteTagDefaults(config, processCompartments)
        DeleteTagNameSpaces(config, processCompartments)


    print ("\n--[ Hopefully deleting compartments, if empty ]--")
    config["region"] = homeregion
    DeleteCompartments(config,processCompartments, DeleteCompartmentOCID)

else:
    print ("ok, doing nothing")



