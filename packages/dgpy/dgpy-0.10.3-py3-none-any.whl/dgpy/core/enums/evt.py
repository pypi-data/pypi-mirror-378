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
"""EV filetypes enum"""

from __future__ import annotations

from enum import IntEnum

__all__ = ("Evt",)


class Evt(IntEnum):
    """EV filetypes ~ Evt"""

    unknown = 0  # unknown
    _2grd = 1  # 2-D grid
    _2gvue = 2  # 2-D grid vue file (old evview)
    _3grd = 3  # 3-D grid
    _3gvue = 4  # 3-D grid vue file (old evview)
    _3igrd = 5  # Indicator 3-D grid
    _4dv = 6  # Generic 3D file - binary
    _4dvx = 7  # Generic 3D file - XML
    ann = 8  # Annotation
    attr = 9  # Attributes (graphic editor)
    avi = 10  # Microsoft video/audio
    bak = 11  # SQL Server database backup file
    bdat = 12  # Binary scattered data files (new HDF5 format)
    bin = 13  # Binary RESCUE format
    bmp = 14  # Windows bitmap file
    bpw = 15  # Bitmap ArcGIS world file
    bwd = 16  # Binary well display file
    c3grd = 17  # Cellular grid
    cell = 18  # Cellular gridding project
    cgm = 19  # Computer graphics meta-file
    csv = 20  # Comma-separated values
    cur = 21  # Windows cursor file
    dat = 22  # Scattered data
    dip = 23  # Well dip/dip azimuth data
    docx = 24  # Microsoft Word XML Format Document file
    dtarget = 25  # Drillers Target files
    dvue = 26  # Scattered data vue file (old evview)
    dxf = 27  # AutoCAD drawing exchange format
    encfaces = 28  # Old format encrypted faces file
    encnfaces = 29  # New format Encrypted faces file
    epc = 30  # RESQML v2.0
    exp = 31  # WA export file
    faces = 32  # Faces file
    faulttranstable = 33  # Used to translate fault numbers into fault names
    fbclr = 34  # Faultblock color table
    fclr = 35  # Feature color table
    fltlist = 36  # Fault list (Changed for 4.0 from Evt_rel)
    flts = 37  # Well fault picks
    fml = 38  # Formula
    gfw = 39  # GIF ArcGIS world file
    gif = 40  # gif image file
    gtarget = 41  # Geologic Target files
    gtf = 42  # GRIDGENR Text Format
    hpgl = 43  # HP Graphics Language
    htbl = 44  # Horizon table
    html = 45  # HTML
    ico = 46  # Windows icon file
    imreg = 47  # Image registration
    iplt = 48  # Intelligent plot file
    itbl = 49  # Isochore table
    jgw = 50  # JPEG ArcGIS world file
    jpeg = 51  # JPEG image file
    jpegw = 52  # JPEG ArcGIS world file
    jpg = 53  # JPEG image file
    labels = 54  # Well bore label file
    las = 55  # LAS format log file
    lbl = 56  # Labels (for polygon operations)
    lclr = 57  # label (string-based) color file
    lgd = 58  # Legend commands
    lidar = 59  # Lidar data in HDF format
    line = 60  # Lines (for polygon operations)
    lith = 61  # Well lithology
    log = 62  # Log file
    m3grd = 63  # Multigrid file
    mod = 64  # Variogram model
    move4dv = 65  # XML describing 4dv with timesteps + transforms
    nvflt = 66  # Non-vertical fault polygons
    path = 67  # Well paths
    pclr = 68  # Property color table
    pdat = 69  # Property scattered data
    pgw = 70  # PNG ArcGIS world file
    plt = 71  # Plot
    ply = 72  # Generic polygons
    png = 73  # Portable Network Graphics image format
    prod = 74  # Production data file (temporal)
    ps = 75  # PostScript
    real = 76  # File realizations=76 for 3D Viewer
    ressim = 77  # New compact cell grid format
    rgb = 78  # Iris image
    seq = 79  # Sequence file for evseq
    sgi = 80  # sgi image file (same as rgb)
    sgy = 81  # SEG Y data
    sh = 82  # Shell scripts
    slice = 83  # Seismic slice used with Ikon Science's RokDoc
    space = 84  # Space specification for evcell=84 nvwx
    stack = 85  # Grid stack (evsec=85 evfence=85 etc.)
    streamline = 86  # Directory of streamline files
    svg = 87  # Scalable vector graphics
    tet = 88  # Dynamic tetrahedral file
    tetra = 89  # Tetrahedral file
    tfw = 90  # TIFF ArcGIS world file
    thr = 91  # Fault throw data
    tif = 92  # tiff image file
    tiff = 93  # tiff image file
    tiffw = 94  # TIFF ArcGIS world file
    tops = 95  # Well horizon tops
    trans = 96  # Horizon gridder transform
    trv = 97  # Traverses (for evsec=97 evfence=97 etc.)
    tubereg = 98  # Tube image registration
    txt = 99  # Any text
    ufaces = 100  # Unsliced faces file
    var = 101  # Variogram
    vflt = 102  # Vertical fault
    vlist = 103  # Vue list=103 for 3D Viewer
    vply = 104  # Volumetrics polygons
    vsnip = 105  # Vue snippet file parameters for 3D Viewer
    vue = 106  # Vue file=106 for 3D Viewer
    wba = 107  # Well bore annotation
    wd = 108  # Well data file
    wfp = 109  # Work flow project
    wlg = 110  # Well logs
    wlist = 111  # Well list
    wtmp = 112  # Well template file
    xls = 113  # Legacy Excel document
    xlsx = 114  # Excel XML document)
    xml = 115  # Extensible markup language
    xpm = 116  # XPM bitmap file
    zclr = 117  # Elevation (Z) color table
    znclr = 118  # Zone color table

    Evt_unknown = 0  # unknown
    Evt_2grd = 1  # 2-D grid
    Evt_2gvue = 2  # 2-D grid vue file (old evview)
    Evt_3grd = 3  # 3-D grid
    Evt_3gvue = 4  # 3-D grid vue file (old evview)
    Evt_3igrd = 5  # Indicator 3-D grid
    Evt_4dv = 6  # Generic 3D file - binary
    Evt_4dvx = 7  # Generic 3D file - XML
    Evt_ann = 8  # Annotation
    Evt_attr = 9  # Attributes (graphic editor)
    Evt_avi = 10  # Microsoft video/audio
    Evt_bak = 11  # SQL Server database backup file
    Evt_bdat = 12  # Binary scattered data files (new HDF5 format)
    Evt_bin = 13  # Binary RESCUE format
    Evt_bmp = 14  # Windows bitmap file
    Evt_bpw = 15  # Bitmap ArcGIS world file
    Evt_bwd = 16  # Binary well display file
    Evt_c3grd = 17  # Cellular grid
    Evt_cell = 18  # Cellular gridding project
    Evt_cgm = 19  # Computer graphics meta-file
    Evt_csv = 20  # Comma-separated values
    Evt_cur = 21  # Windows cursor file
    Evt_dat = 22  # Scattered data
    Evt_dip = 23  # Well dip/dip azimuth data
    Evt_docx = 24  # Microsoft Word XML Format Document file
    Evt_dtarget = 25  # Drillers Target files
    Evt_dvue = 26  # Scattered data vue file (old evview)
    Evt_dxf = 27  # AutoCAD drawing exchange format
    Evt_encfaces = 28  # Old format encrypted faces file
    Evt_encnfaces = 29  # New format Encrypted faces file
    Evt_epc = 30  # RESQML v2.0
    Evt_exp = 31  # WA export file
    Evt_faces = 32  # Faces file
    Evt_faulttranstable = 33  # Used to translate fault numbers into fault names
    Evt_fbclr = 34  # Faultblock color table
    Evt_fclr = 35  # Feature color table
    Evt_fltlist = 36  # Fault list (Changed for 4.0 from Evt_rel)
    Evt_flts = 37  # Well fault picks
    Evt_fml = 38  # Formula
    Evt_gfw = 39  # GIF ArcGIS world file
    Evt_gif = 40  # gif image file
    Evt_gtarget = 41  # Geologic Target files
    Evt_gtf = 42  # GRIDGENR Text Format
    Evt_hpgl = 43  # HP Graphics Language
    Evt_htbl = 44  # Horizon table
    Evt_html = 45  # HTML
    Evt_ico = 46  # Windows icon file
    Evt_imreg = 47  # Image registration
    Evt_iplt = 48  # Intelligent plot file
    Evt_itbl = 49  # Isochore table
    Evt_jgw = 50  # JPEG ArcGIS world file
    Evt_jpeg = 51  # JPEG image file
    Evt_jpegw = 52  # JPEG ArcGIS world file
    Evt_jpg = 53  # JPEG image file
    Evt_labels = 54  # Well bore label file
    Evt_las = 55  # LAS format log file
    Evt_lbl = 56  # Labels (for polygon operations)
    Evt_lclr = 57  # label (string-based) color file
    Evt_lgd = 58  # Legend commands
    Evt_lidar = 59  # Lidar data in HDF format
    Evt_line = 60  # Lines (for polygon operations)
    Evt_lith = 61  # Well lithology
    Evt_log = 62  # Log file
    Evt_m3grd = 63  # Multigrid file
    Evt_mod = 64  # Variogram model
    Evt_move4dv = 65  # XML describing 4dv with timesteps + transforms
    Evt_nvflt = 66  # Non-vertical fault polygons
    Evt_path = 67  # Well paths
    Evt_pclr = 68  # Property color table
    Evt_pdat = 69  # Property scattered data
    Evt_pgw = 70  # PNG ArcGIS world file
    Evt_plt = 71  # Plot
    Evt_ply = 72  # Generic polygons
    Evt_png = 73  # Portable Network Graphics image format
    Evt_prod = 74  # Production data file (temporal)
    Evt_ps = 75  # PostScript
    Evt_real = 76  # File realizations=76 for 3D Viewer
    Evt_ressim = 77  # New compact cell grid format
    Evt_rgb = 78  # Iris image
    Evt_seq = 79  # Sequence file for evseq
    Evt_sgi = 80  # sgi image file (same as rgb)
    Evt_sgy = 81  # SEG Y data
    Evt_sh = 82  # Shell scripts
    Evt_slice = 83  # Seismic slice used with Ikon Science's RokDoc
    Evt_space = 84  # Space specification for evcell=84 nvwx
    Evt_stack = 85  # Grid stack (evsec=85 evfence=85 etc.)
    Evt_streamline = 86  # Directory of streamline files
    Evt_svg = 87  # Scalable vector graphics
    Evt_tet = 88  # Dynamic tetrahedral file
    Evt_tetra = 89  # Tetrahedral file
    Evt_tfw = 90  # TIFF ArcGIS world file
    Evt_thr = 91  # Fault throw data
    Evt_tif = 92  # tiff image file
    Evt_tiff = 93  # tiff image file
    Evt_tiffw = 94  # TIFF ArcGIS world file
    Evt_tops = 95  # Well horizon tops
    Evt_trans = 96  # Horizon gridder transform
    Evt_trv = 97  # Traverses (for evsec=97 evfence=97 etc.)
    Evt_tubereg = 98  # Tube image registration
    Evt_txt = 99  # Any text
    Evt_ufaces = 100  # Unsliced faces file
    Evt_var = 101  # Variogram
    Evt_vflt = 102  # Vertical fault
    Evt_vlist = 103  # Vue list=103 for 3D Viewer
    Evt_vply = 104  # Volumetrics polygons
    Evt_vsnip = 105  # Vue snippet file parameters for 3D Viewer
    Evt_vue = 106  # Vue file=106 for 3D Viewer
    Evt_wba = 107  # Well bore annotation
    Evt_wd = 108  # Well data file
    Evt_wfp = 109  # Work flow project
    Evt_wlg = 110  # Well logs
    Evt_wlist = 111  # Well list
    Evt_wtmp = 112  # Well template file
    Evt_xls = 113  # Legacy Excel document
    Evt_xlsx = 114  # Excel XML document)
    Evt_xml = 115  # Extensible markup language
    Evt_xpm = 116  # XPM bitmap file
    Evt_zclr = 117  # Elevation (Z) color table
    Evt_znclr = 118  # Zone color table
