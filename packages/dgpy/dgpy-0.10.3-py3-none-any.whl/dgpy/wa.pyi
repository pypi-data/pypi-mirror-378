# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (2025) Dynamic Graphics, Inc. Lafayette, CA, USA.
#
# This DGPY library (the "Software") may not be used except in connection with
# the Licensees use of the Dynamic Graphics' software pursuant to an
# Agreement (defined below) between Licensee (defined below) and
# Dynamic Graphics, Inc. ("DGI"). This Software shall be deemed part of the
# Licensed Software under the Agreement. Licensees use of the Software must
# comply at all times with any restrictions applicable to the Licensed
# Software, generally, and must be used in accordance with applicable
# documentation. If you have not agreed to an Agreement or otherwise do not
# agree to these terms, you may not use the Software. This license terminates
# automatically upon the termination of the Agreement or Licensees breach of
# these terms.
#
# DEFINITIONS:
#  - Agreement: The software product license agreement, as amended, executed
#               between DGI and Licensee governing the use of the DGI software.
#  - Licensee: The user of the Software, or, if the Software is being used on
#              behalf of a company, the company.
# =============================================================================
"""wa exe wrapper functions"""

from __future__ import annotations

from dgpy.core.exe import ExeFunction, ExeFunctionAsync

__all__: list[str]
__FUNCTIONS__: dict[str, ExeFunction | ExeFunctionAsync]

# Sync functions
_2grid: ExeFunction
_2trend: ExeFunction
_4dvcurtain: ExeFunction
_4dvedit: ExeFunction
addpath: ExeFunction
addpathinterval: ExeFunction
annotate: ExeFunction
append: ExeFunction
attrbitmap: ExeFunction
autoclearance: ExeFunction
bil: ExeFunction
bufferzon: ExeFunction
celledit: ExeFunction
cfc: ExeFunction
clean: ExeFunction
clearance: ExeFunction
clipfaces: ExeFunction
compimportreport: ExeFunction
config: ExeFunction
contour: ExeFunction
dbexport: ExeFunction
dbimport: ExeFunction
dbqa: ExeFunction
depth2el: ExeFunction
dist2surf: ExeFunction
dumbbell: ExeFunction
dump: ExeFunction
dxf: ExeFunction
el2depth: ExeFunction
export: ExeFunction
extract: ExeFunction
facedump: ExeFunction
facesedit: ExeFunction
field: ExeFunction
fieldreport: ExeFunction
finddbid: ExeFunction
flttic: ExeFunction
fp: ExeFunction
getReplacementWP: ExeFunction
gridcurtain: ExeFunction
gridto4dv: ExeFunction
ht2sh: ExeFunction
_import: ExeFunction
inter: ExeFunction
lgd: ExeFunction
lineplot: ExeFunction
maplabel: ExeFunction
package: ExeFunction
packreport: ExeFunction
pathToWA: ExeFunction
pathexport: ExeFunction
pathreport: ExeFunction
plotserver: ExeFunction
pltconvert: ExeFunction
plyarea: ExeFunction
plybld: ExeFunction
plybop: ExeFunction
plyhull: ExeFunction
ptinpoly: ExeFunction
segyimport: ExeFunction
seqbuild: ExeFunction
seqedit: ExeFunction
shapeimport: ExeFunction
siteid: ExeFunction
slice: ExeFunction
stat: ExeFunction
surfclip: ExeFunction
surfer: ExeFunction
surfhide: ExeFunction
sysinfo: ExeFunction
targeterode: ExeFunction
targetexport: ExeFunction
testlibopenplan: ExeFunction
tplot: ExeFunction
travelcyl: ExeFunction
tsolidto4dv: ExeFunction
tsurf4dv: ExeFunction
tunface: ExeFunction
viewipc: ExeFunction
wecopyitem: ExeFunction
wellDataPlot: ExeFunction
wellpath: ExeFunction
wellstrc: ExeFunction
wellsurvey: ExeFunction
welltube: ExeFunction
wenodeinfo: ExeFunction
wmlimport: ExeFunction
x2face: ExeFunction
xformann: ExeFunction
xsec: ExeFunction
zmapgridimport: ExeFunction
zonlin: ExeFunction
zonply: ExeFunction
zonpnt: ExeFunction

# Async functions
_2grid_async: ExeFunctionAsync
_2trend_async: ExeFunctionAsync
_4dvcurtain_async: ExeFunctionAsync
_4dvedit_async: ExeFunctionAsync
addpath_async: ExeFunctionAsync
addpathinterval_async: ExeFunctionAsync
annotate_async: ExeFunctionAsync
append_async: ExeFunctionAsync
attrbitmap_async: ExeFunctionAsync
autoclearance_async: ExeFunctionAsync
bil_async: ExeFunctionAsync
bufferzon_async: ExeFunctionAsync
celledit_async: ExeFunctionAsync
cfc_async: ExeFunctionAsync
clean_async: ExeFunctionAsync
clearance_async: ExeFunctionAsync
clipfaces_async: ExeFunctionAsync
compimportreport_async: ExeFunctionAsync
config_async: ExeFunctionAsync
contour_async: ExeFunctionAsync
dbexport_async: ExeFunctionAsync
dbimport_async: ExeFunctionAsync
dbqa_async: ExeFunctionAsync
depth2el_async: ExeFunctionAsync
dist2surf_async: ExeFunctionAsync
dumbbell_async: ExeFunctionAsync
dump_async: ExeFunctionAsync
dxf_async: ExeFunctionAsync
el2depth_async: ExeFunctionAsync
export_async: ExeFunctionAsync
extract_async: ExeFunctionAsync
facedump_async: ExeFunctionAsync
facesedit_async: ExeFunctionAsync
field_async: ExeFunctionAsync
fieldreport_async: ExeFunctionAsync
finddbid_async: ExeFunctionAsync
flttic_async: ExeFunctionAsync
fp_async: ExeFunctionAsync
getReplacementWP_async: ExeFunctionAsync
gridcurtain_async: ExeFunctionAsync
gridto4dv_async: ExeFunctionAsync
ht2sh_async: ExeFunctionAsync
_import_async: ExeFunctionAsync
inter_async: ExeFunctionAsync
lgd_async: ExeFunctionAsync
lineplot_async: ExeFunctionAsync
maplabel_async: ExeFunctionAsync
package_async: ExeFunctionAsync
packreport_async: ExeFunctionAsync
pathToWA_async: ExeFunctionAsync
pathexport_async: ExeFunctionAsync
pathreport_async: ExeFunctionAsync
plotserver_async: ExeFunctionAsync
pltconvert_async: ExeFunctionAsync
plyarea_async: ExeFunctionAsync
plybld_async: ExeFunctionAsync
plybop_async: ExeFunctionAsync
plyhull_async: ExeFunctionAsync
ptinpoly_async: ExeFunctionAsync
segyimport_async: ExeFunctionAsync
seqbuild_async: ExeFunctionAsync
seqedit_async: ExeFunctionAsync
shapeimport_async: ExeFunctionAsync
siteid_async: ExeFunctionAsync
slice_async: ExeFunctionAsync
stat_async: ExeFunctionAsync
surfclip_async: ExeFunctionAsync
surfer_async: ExeFunctionAsync
surfhide_async: ExeFunctionAsync
sysinfo_async: ExeFunctionAsync
targeterode_async: ExeFunctionAsync
targetexport_async: ExeFunctionAsync
testlibopenplan_async: ExeFunctionAsync
tplot_async: ExeFunctionAsync
travelcyl_async: ExeFunctionAsync
tsolidto4dv_async: ExeFunctionAsync
tsurf4dv_async: ExeFunctionAsync
tunface_async: ExeFunctionAsync
viewipc_async: ExeFunctionAsync
wecopyitem_async: ExeFunctionAsync
wellDataPlot_async: ExeFunctionAsync
wellpath_async: ExeFunctionAsync
wellstrc_async: ExeFunctionAsync
wellsurvey_async: ExeFunctionAsync
welltube_async: ExeFunctionAsync
wenodeinfo_async: ExeFunctionAsync
wmlimport_async: ExeFunctionAsync
x2face_async: ExeFunctionAsync
xformann_async: ExeFunctionAsync
xsec_async: ExeFunctionAsync
zmapgridimport_async: ExeFunctionAsync
zonlin_async: ExeFunctionAsync
zonply_async: ExeFunctionAsync
zonpnt_async: ExeFunctionAsync
