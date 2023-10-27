#%%
from qgis.core import *

#%%
# Supply the path to the qgis install location

QgsApplication.setPrefixPath('C:/PROGRA~1/QGIS32~1.3/apps/qgis', True)


# Create a reference to the QgsApplication.

# Setting the second argument to True enables the GUI.  We need

# this since this is a custom application.


qgs = QgsApplication([], True)


# load providers

qgs.initQgis()


# Write your code here to load some layers, use processing

# algorithms, etc.


# Finally, exitQgis() is called to remove the

# provider and layer registries from memory

qgs.exitQgis()
# %%
