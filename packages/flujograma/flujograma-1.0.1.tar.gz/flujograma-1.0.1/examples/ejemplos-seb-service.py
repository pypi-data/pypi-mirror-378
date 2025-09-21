import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma.diagrams_api import Diagram, ELB, EC2, RDS, S3

with Diagram("Web Services", show=False, filename="web_services_final.png"):
    ELB("lb") >> EC2("web") >> RDS("userdb") >> S3("store")
    ELB("lb") >> EC2("web") >> RDS("userdb") << EC2("stat")
    (ELB("lb") >> EC2("web")) >> EC2("web") >> RDS("userdb")