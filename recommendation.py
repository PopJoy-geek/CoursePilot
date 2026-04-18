from typing import List, Optional, Dict, Any, Set
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime
from enum import Enum

router = APIRouter()

# Local data storage
DATA_FILE = "app/sample_data.json"

# Major course sets based on the DKU 2025-2026 bulletin (grouped by major/track)
# Notes:
# 1. These sets are mainly used for recommendation priority calculation, so all
#    required/restricted elective courses appearing in the major requirements are
#    treated as "major-related courses".
# 2. For actual graduation audits, it is still recommended to rely on
#    request.graduation_requirements.
MAJOR_REQUIREMENT_COURSES: Dict[str, Set[str]] = {
        "Applied Mathematics and Computational Sciences/Computer Science": {'INTGSCI 205', 'MATH 105', 'STATS 102', 'COMPSCI 308', 'MATH 201', 'MATH 206', 'COMPSCI 310', 'PHYS 121', 'BIOL 110', 'COMPSCI 101', 'MATH 202', 'COMPSCI 201', 'MATH 101', 'COMPSCI 203', 'MATH 302', 'COMPSCI 306', 'COMPSCI 205', 'COMPSCI 311', 'CHEM 110'},
        "Applied Mathematics and Computational Sciences/Mathematics": {'INTGSCI 205', 'MATH 105', 'STATS 102', 'MATH 307', 'MATH 405', 'MATH 409', 'MATH 201', 'MATH 206', 'MATH 401', 'PHYS 121', 'BIOL 110', 'COMPSCI 101', 'MATH 202', 'MATH 308', 'MATH 406', 'COMPSCI 201', 'MATH 403', 'MATH 303', 'MATH 101', 'MATH 302', 'MATH 203', 'CHEM 110'},
        "Arts and Media/Arts": {'HUM 405', 'MEDIART 104', 'MEDIART 207', 'MEDIART 305', 'MEDIART 204', 'MEDIART 101', 'INFOSCI 105', 'HIST 217', 'ARTS 210', 'MEDIART 212', 'HIST 210', 'MEDIART 224', 'HIST 207', 'MEDIART 302', 'LIT 216', 'MEDIART 221', 'LIT 311', 'MEDIART 498', 'ARTS 201', 'ARTS 105', 'MEDIART 405', 'MEDIART 222', 'MEDIART 209', 'MEDIART 217', 'MEDIART 322', 'MEDIART 216', 'MEDIART 210', 'HIST 106', 'MEDIART 301', 'MEDIART 218', 'ARHU 102', 'MEDIART 211', 'MEDIART 118', 'PHYS 105', 'MEDIART 220', 'MEDIART 115', 'MEDIART 202', 'ARHU 101', 'MEDIART 103', 'MEDIART 110', 'INFOSCI 202', 'MEDIART 310', 'MEDIART 223', 'LIT 208', 'HIST 218', 'ARTS 208', 'MEDIART 311', 'MEDIART 205', 'MEDIART 490', 'ARTS 202', 'ARTS 203', 'MEDIART 105', 'MEDIART 117', 'MEDIART 198'},
        "Arts and Media/Media": {'HUM 405', 'MEDIART 207', 'MEDIART 401', 'MEDIART 305', 'MEDIART 104', 'MEDIART 204', 'MEDIART 101', 'INFOSCI 105', 'GLHLTH 202', 'MEDIART 212', 'MEDIA 204', 'MEDIART 224', 'GCULS 201', 'MEDIA 207', 'LIT 204', 'LIT 216', 'MEDIART 221', 'MEDIART 498', 'MEDIART 405', 'MEDIART 222', 'MEDIART 209', 'MEDIART 322', 'MEDIART 216', 'MEDIART 210', 'MEDIART 218', 'MEDIART 301', 'MEDIART 321', 'INFOSCI 309', 'MEDIART 120', 'MEDIART 213', 'ARHU 102', 'MEDIA 201', 'INFOSCI 305', 'MEDIART 211', 'MEDIART 118', 'INFOSCI 104', 'MEDIART 220', 'MEDIART 225', 'MEDIART 115', 'MEDIART 202', 'ARHU 101', 'MEDIART 103', 'MEDIA 202', 'MEDIART 110', 'INFOSCI 202', 'CULANTH 202', 'MEDIART 310', 'MEDIART 223', 'CULANTH 207', 'LIT 307', 'MEDIART 307', 'MEDIART 311', 'MEDIART 205', 'MEDIART 490', 'MEDIART 208', 'MEDIART 117', 'MEDIART 312', 'CULANTH 201', 'MEDIART 198', 'INFOSCI 201', 'MEDIA 104', 'MEDIART 323'},
        "Behavioral Science / Economics": {'BEHAVSCI 201', 'MATH 105', 'ECON 302', 'ECON 304', 'ECON 204', 'BEHAVSCI 102', 'ECON 309', 'MATH 206', 'ECON 305', 'ECON 318', 'BEHAVSCI 202', 'ECON 101', 'BIOL 110', 'ECON 301', 'ECON 303', 'ENVIR 302', 'STATS 101', 'ECON 202', 'BEHAVSCI 401', 'SOSC 101', 'ECON 333', 'MATH 101', 'ECON 310', 'ECON 314', 'ECON 307', 'BEHAVSCI 101', 'ECON 201'},
        "Behavioral Science / Neuroscience": {'NEUROSCI 212', 'BEHAVSCI 201', 'MATH 206', 'BEHAVSCI 102', 'BEHAVSCI 205', 'STATS 101', 'MATH 105', 'BEHAVSCI 202', 'BEHAVSCI 401', 'NEUROSCI 301', 'BEHAVSCI 301', 'NEUROSCI 102', 'BIOL 110', 'BEHAVSCI 101', 'SOSC 101', 'MATH 101'},
        "Behavioral Science / Psychology": {'PSYCH 205', 'BEHAVSCI 201', 'MATH 105', 'PSYCH 101', 'BEHAVSCI 102', 'PSYCH 204', 'MATH 206', 'BEHAVSCI 402', 'BEHAVSCI 202', 'NEUROSCI 102', 'BIOL 110', 'NEUROSCI 212', 'PSYCH 202', 'STATS 101', 'BEHAVSCI 401', 'SOSC 101', 'MATH 101', 'PSYCH 203', 'BEHAVSCI 101'},
        "Computation and Design / Computer Science": {'MATH 105', 'STATS 102', 'COMPDSGN 490', 'COMPSCI 308', 'MATH 206', 'COMPSCI 310', 'PHYS 121', 'BIOL 110', 'INFOSCI 103', 'INFOSCI 102', 'COMPSCI 101', 'INFOSCI 104', 'COMPSCI 201', 'MATH 101', 'COMPSCI 203', 'COMPSCI 306', 'STATS 202', 'COMPSCI 205', 'COMPSCI 311', 'CHEM 110', 'MEDIA 104'},
        "Computation and Design / Digital Media": {'MATH 105', 'STATS 102', 'COMPDSGN 490', 'MEDIART 306', 'INFOSCI 301', 'INFOSCI 309', 'INFOSCI 103', 'INFOSCI 102', 'COMPSCI 101', 'ARHU 102', 'INFOSCI 104', 'ARHU 101', 'INFOSCI 202', 'STATS 101', 'MATH 101', 'MEDIART 206', 'STATS 202', 'INFOSCI 304', 'INFOSCI 201', 'MEDIA 104'},
        "Computation and Design / Social Policy": {'MATH 105', 'STATS 102', 'COMPDSGN 490', 'SOSC 314', 'ECON 302', 'ENVIR 201', 'ENVIR 303', 'GLHLTH 310', 'POLSCI 309', 'SOSC 315', 'ETHLDR 204', 'CULMOVE 101', 'HIST 111', 'INFOSCI 103', 'INFOSCI 102', 'INFOSCI 302', 'COMPSCI 101', 'INFOSCI 305', 'ENVIR 302', 'POLSCI 101', 'INFOSCI 104', 'SOSC 333', 'STATS 101', 'COMPSCI 206', 'ENVIR 101', 'HIST 212', 'SOSC 320', 'SOSC 405', 'ENVIR 203', 'STATS 201', 'SOSC 101', 'PUBPOL 204', 'ECON 333', 'MATH 101', 'ECON 206', 'ECON 310', 'ENVIR 301', 'ECON 314', 'STATS 202', 'ENVIR 206', 'POLECON 201', 'MEDIA 203', 'MEDIA 104'},
        "Cultures and Societies / Cultural Anthropology": {'CULANTH 302', 'RELIG 205', 'GCHINA 305', 'CULANTH 211', 'CULSOC 490', 'CULSOC 101', 'CULSOC 205', 'CULANTH 398', 'CULMOVE 101', 'CULSOC 301', 'CULSOC 201', 'SOSC 101', 'SOSC 102', 'CULSOC 390', 'CULANTH 304', 'CULANTH 405', 'CULANTH 314', 'POLSCI 314', 'CULANTH 101'},
        "Cultures and Societies / Sociology": {'SOCIOL 213', 'SOSC 314', 'SOSC 309', 'RELIG 205', 'SOSC 206', 'SOSC 315', 'CULSOC 490', 'SOCIOL 101', 'CULSOC 101', 'CULSOC 205', 'SOCIOL 202', 'CULSOC 301', 'ECON 203', 'SOCIOL 310', 'CULSOC 201', 'STATS 101', 'SOCIOL 380', 'SOCIOL 305', 'SOSC 101', 'SOSC 102', 'CULSOC 390', 'POLECON 301', 'SOCIOL 223'},
        "Data Science": {'COMPSCI 309', 'INTGSCI 205', 'MATH 304', 'MATH 105', 'MATH 305', 'MATH 201', 'MATH 206', 'STATS 303', 'STATS 211', 'STATS 302', 'PHYS 121', 'BIOL 110', 'MATH 202', 'COMPSCI 201', 'STATS 401', 'MATH 101', 'STATS 402', 'CHEM 110', 'COMPSCI 301'},
        "Environmental Science / Biogeochemistry": {'BIOL 208', 'BIOL 313', 'MATH 105', 'ENVIR 202', 'ECON 302', 'ENVIR 304', 'BIOL 312', 'ENVIR 201', 'ENVIR 311', 'BIOL 405', 'MATH 206', 'CHEM 315', 'PHYS 121', 'BIOL 110', 'ENVIR 302', 'BIOL 311', 'STATS 101', 'ENVIR 101', 'ENVIR 315', 'MATH 101', 'ENVIR 301', 'BIOL 319', 'ENVIR 102', 'CHEM 110', 'ENVIR 313'},
        "Environmental Science / Biology": {'BIOL 208', 'MATH 105', 'ENVIR 202', 'ECON 302', 'ENVIR 304', 'ENVIR 201', 'CHEM 201', 'MATH 206', 'BIOL 201', 'PHYS 121', 'BIOL 110', 'ENVIR 302', 'BIOL 305', 'BIOL 212', 'STATS 101', 'ENVIR 101', 'MATH 101', 'ENVIR 301', 'ENVIR 102', 'BIOL 202', 'CHEM 110'},
        "Environmental Science / Chemistry": {'CHEM 401', 'MATH 105', 'ENVIR 202', 'ECON 302', 'ENVIR 304', 'ENVIR 201', 'CHEM 201', 'MATH 201', 'CHEM 301', 'PHYS 122', 'PHYS 121', 'BIOL 110', 'ENVIR 302', 'ENVIR 101', 'MATH 101', 'ENVIR 301', 'ENVIR 102', 'CHEM 150', 'CHEM 402', 'CHEM 202', 'CHEM 110'},
        "Environmental Science / Public Policy": {'PUBPOL 303', 'MATH 105', 'ENVIR 202', 'ECON 302', 'ENVIR 304', 'ENVIR 201', 'PUBPOL 101', 'PUBPOL 205', 'BIOL 110', 'PUBPOL 301', 'ENVIR 302', 'STATS 101', 'ENVIR 101', 'SOSC 101', 'MATH 101', 'ENVIR 301', 'SOSC 102', 'ENVIR 102', 'CHEM 110', 'ECON 201'},
        "Global China Studies": {'GCHINA 306', 'POLSCI 316', 'HIST 217', 'LIT 310', 'SOSC 206', 'GCHINA 203', 'GCHINA 305', 'CHINESE 423', 'POLSCI 303', 'GCHINA 390', 'GCHINA 206', 'HIST 205', 'PHIL 102', 'HIST 201', 'RELIG 302', 'LIT 223', 'HIST 101', 'POLECON 302', 'CHINESE 402B', 'ARTS 217', 'ARHU 101', 'GCHINA 204', 'STATS 101', 'HIST 301', 'SOSC 101', 'CULANTH 206', 'CHINESE 402A', 'GCHINA 301', 'GCHINA 490', 'SOSC 102', 'GCHINA 202', 'PHIL 226', 'HIST 226', 'GCHINA 205', 'ARTS 203', 'POLSCI 398', 'MEDIART 208', 'POLSCI 221', 'GCHINA 108'},
        "Global Health / Biology": {'BIOL 208', 'GLHLTH 307', 'MATH 105', 'GLHLTH 305', 'CHEM 201', 'GLHLTH 310', 'MATH 206', 'GLHLTH 303', 'BIOL 201', 'PHYS 121', 'BIOL 110', 'BIOL 305', 'BIOL 212', 'STATS 101', 'GLHLTH 205', 'GLHLTH 280', 'GLHLTH 306', 'GLHLTH 101', 'GLHLTH 304', 'MATH 101', 'GLHLTH 201', 'BIOL 202', 'CHEM 110'},
        "Global Health / Public Policy": {'GLHLTH 307', 'PUBPOL 303', 'MATH 105', 'GLHLTH 305', 'PUBPOL 101', 'GLHLTH 310', 'GLHLTH 303', 'PUBPOL 205', 'BIOL 110', 'PUBPOL 301', 'STATS 101', 'GLHLTH 205', 'GLHLTH 280', 'GLHLTH 306', 'GLHLTH 101', 'SOSC 101', 'GLHLTH 304', 'MATH 101', 'GLHLTH 201', 'SOSC 102', 'ECON 201'},
        "Humanities / Creative Writing and Translation": {'HUM 405', 'LIT 220', 'WOC 213', 'WOC 108', 'MEDIART 207', 'GCULS 205', 'LIT 310', 'GCULS 105', 'CHINESE 423', 'LIT 216', 'MEDIART 405', 'LIT 314', 'MEDIART 219', 'WOC 190', 'GCULS 302', 'LIT 223', 'HUM 301', 'WOC 290', 'ARHU 102', 'WOC 214', 'WOC 217', 'ARHU 101', 'WOC 216', 'MEDIART 110', 'LIT 315', 'LIT 219', 'MEDIART 310', 'GCULS 202', 'WOC 210', 'CHINESE 414', 'HUM 490', 'WOC 207', 'HIST 314', 'CHINESE 408', 'LIT 311'},
        "Humanities / Literature": {'HUM 405', 'LIT 398', 'GCULS 205', 'LIT 310', 'GCULS 105', 'LIT 216', 'LIT 311', 'LIT 203', 'LIT 298', 'MEDIART 405', 'GCULS 302', 'LIT 223', 'HUM 301', 'LIT 210', 'ARHU 102', 'LIT 214', 'ARHU 101', 'LIT 315', 'GCULS 202', 'RELIG 101', 'HUM 490', 'RELIG 221', 'LIT 314'},
        "Humanities / Philosophy and Religion": {'GCULS 205', 'GCULS 105', 'RELIG 302', 'RELIG 203', 'GCULS 302', 'HUM 301', 'HIST 101', 'HUM 201', 'ARHU 102', 'ARHU 101', 'RELIG 398', 'PHI 102', 'GCULS 202', 'RELIG 101', 'HUM 490', 'RELIG 221', 'PHIL 226', 'PHIL 305', 'PHIL 398', 'PHIL 101'},
        "Humanities / World History": {'GCULS 205', 'HIST 217', 'HIST 401', 'GCULS 105', 'HIST 201', 'RELIG 203', 'GCULS 302', 'HUM 301', 'HIST 229', 'HIST 233', 'HIST 111', 'HIS 212', 'ARHU 102', 'ARTS 217', 'HIST 402', 'ARHU 101', 'HIST 230', 'GCULS 202', 'HIST 309', 'HUM 490', 'HIST 314', 'HIST 228', 'HIST 227'},
        "Materials Science / Chemistry": {'MATH 201', 'MATSCI 301', 'CHEM 301', 'CHEM 401', 'MATH 105', 'PHYS 122', 'MATSCI 302', 'CHEM 201', 'MATSCI 201', 'CHEM 150', 'CHEM 402', 'MATSCI 401', 'PHYS 121', 'BIOL 110', 'CHEM 110', 'CHEM 202', 'MATH 101'},
        "Materials Science / Physics": {'MATH 105', 'CHEM 201', 'MATSCI 201', 'MATSCI 401', 'PHYS 405', 'PHYS 306', 'MATH 201', 'MATSCI 301', 'PHYS 122', 'PHYS 121', 'BIOL 110', 'PHYS 301', 'MATH 202', 'MATSCI 302', 'MATH 101', 'PHYS 201', 'CHEM 110', 'PHYS 304', 'PHYS 302'},
        "Molecular Bioscience / Biogeochemistry": {'BIOL 208', 'BIOL 313', 'MATH 105', 'BIOL 312', 'CHEM 201', 'ENVIR 311', 'MATH 206', 'BIOL 201', 'CHEM 315', 'PHYS 121', 'BIOL 110', 'BIOL 305', 'BIOL 311', 'BIOL 212', 'PHYS 303', 'STATS 101', 'ENVIR 315', 'MATH 101', 'BIOL 320', 'BIOL 319', 'ENVIR 102', 'BIOL 202', 'CHEM 150', 'CHEM 110', 'ENVIR 313'},
        "Molecular Bioscience / Biophysics": {'MATH 105', 'PHYS 404', 'CHEM 201', 'PHYS 306', 'MATH 201', 'BIOL 201', 'PHYS 122', 'PHYS 121', 'BIOL 110', 'PHYS 301', 'MATH 202', 'BIOL 305', 'PHYS 303', 'MATH 101', 'BIOL 320', 'PHYS 406', 'PHYS 201', 'BIOL 202', 'CHEM 110', 'PHYS 304', 'PHYS 302'},
        "Molecular Bioscience / Cell and Molecular Biology": {'BIOL 305', 'BIOL 315', 'MATH 206', 'BIOL 320', 'BIOL 212', 'PHYS 303', 'MATH 105', 'BIOL 201', 'STATS 101', 'CHEM 201', 'BIOL 202', 'BIOL 304', 'BIOL 306', 'PHYS 121', 'BIOL 110', 'CHEM 110', 'BIOL 321', 'MATH 101'},
        "Molecular Bioscience / Genetics and Genomics": {'BIOL 305', 'BIOL 403', 'MATH 206', 'BIOL 320', 'BIOL 407', 'BIOL 314', 'PHYS 303', 'MATH 105', 'BIOL 201', 'STATS 101', 'CHEM 201', 'BIOL 202', 'BIOL 304', 'PHYS 121', 'BIOL 110', 'CHEM 110', 'BIOL 321', 'MATH 101'},
        "Molecular Bioscience / Neuroscience": {'BIOL 305', 'NEUROSCI 212', 'BIOL 320', 'BEHAVSCI 205', 'PHYS 303', 'MATH 105', 'BEHAVSCI 301', 'BIOL 110', 'NEUROSCI 102', 'CHEM 201', 'BIOL 202', 'PHYS 121', 'NEUROSCI 301', 'CHEM 110', 'MATH 101'},
        "Philosophy, Politics, and Economics / Economic History": {'HIST 201', 'SOSC 102', 'SOSC 205', 'PUBPOL 303', 'ETHLDR 202', 'ETHLDR 203', 'STATS 101', 'GCHINA 301', 'POLECON 301', 'ECON 101', 'HIST 227', 'ECON 307', 'PPE 490', 'PPE 101', 'SOSC 101', 'ECON 204', 'ECON 203', 'ECON 201'},
        "Philosophy, Politics, and Economics / Philosophy": {'PHIL 207', 'PHIL 205', 'ARHU 101', 'PUBPOL 303', 'PPE 202', 'PHIL 226', 'HIST 226', 'PPE 303', 'PHIL 305', 'ECON 101', 'PHIL 210', 'PHIL 398', 'PHIL 309', 'PPE 490', 'PPE 101', 'SOSC 101', 'ECON 201'},
        "Philosophy, Politics, and Economics / Political Science": {'POLSCI 307', 'SOSC 102', 'CULSOC 201', 'PUBPOL 303', 'POLSCI 303', 'STATS 101', 'POLSCI 104', 'POLSCI 398', 'ECON 101', 'PPE 490', 'POLSCI 308', 'PPE 101', 'POLSCI 223', 'SOSC 101', 'POLSCI 101', 'ECON 201'},
        "Philosophy, Politics, and Economics / Public Policy": {'PUBPOL 301', 'PUBPOL 221', 'SOSC 102', 'ECON 315', 'PUBPOL 303', 'STATS 101', 'POLSCI 104', 'PUBPOL 223', 'PUBPOL 222', 'ECON 101', 'PPE 490', 'PUBPOL 315', 'PUBPOL 101', 'PPE 101', 'SOSC 101', 'PUBPOL 204', 'ECON 201'},
        "Quantitative Political Economy / Economics": {'MATH 105', 'ECON 302', 'SOSC 314', 'POLECON 490', 'POLSCI 301', 'ECON 204', 'ECON 304', 'ECON 305', 'ETHLDR 202', 'ECON 318', 'ECON 101', 'ECON 301', 'ECON 303', 'ENVIR 302', 'ECON 203', 'SOSC 205', 'PPE 202', 'STATS 101', 'ECON 202', 'SOSC 320', 'SOSC 302', 'ECON 333', 'GCHINA 301', 'MATH 101', 'PUBPOL 315', 'SOSC 102', 'ECON 310', 'ECON 315', 'ECON 314', 'POLECON 301', 'ECON 307', 'POLECON 302', 'POLECON 201', 'ECON 201'},
        "Quantitative Political Economy / Political Science": {'MATH 105', 'SOSC 314', 'POLSCI 308', 'POLSCI 307', 'POLECON 490', 'POLSCI 301', 'ETHLDR 202', 'ECON 101', 'POLSCI 101', 'ECON 203', 'SOSC 205', 'PPE 202', 'STATS 101', 'POLSCI 104', 'POLSCI 302', 'SOSC 320', 'SOSC 302', 'GCHINA 301', 'MATH 101', 'SOSC 102', 'POLECON 301', 'POLECON 302', 'POLECON 201'},
        "Quantitative Political Economy / Public Policy": {'SOSC 102', 'SOSC 205', 'ETHLDR 202', 'PPE 202', 'STATS 101', 'MATH 105', 'GCHINA 301', 'SOSC 314', 'POLECON 301', 'ECON 101', 'POLECON 490', 'SOSC 320', 'POLECON 302', 'POLECON 201', 'POLSCI 301', 'SOSC 302', 'ECON 203', 'MATH 101'}
}

# Common major aliases for compatibility with different formats in the frontend/database
MAJOR_ALIASES: Dict[str, str] = {
    "amcs cs": "Applied Mathematics and Computational Sciences/Computer Science",
    "amcs computer science": "Applied Mathematics and Computational Sciences/Computer Science",
    "applied mathematics and computational sciences/computer science": "Applied Mathematics and Computational Sciences/Computer Science",
    "amcs math": "Applied Mathematics and Computational Sciences/Mathematics",
    "applied mathematics and computational sciences/mathematics": "Applied Mathematics and Computational Sciences/Mathematics",
    "arts and media arts": "Arts and Media/Arts",
    "arts and media media": "Arts and Media/Media",
    "behavioral science economics": "Behavioral Science / Economics",
    "behavioral science neuroscience": "Behavioral Science / Neuroscience",
    "behavioral science psychology": "Behavioral Science / Psychology",
    "computation and design computer science": "Computation and Design / Computer Science",
    "computation and design digital media": "Computation and Design / Digital Media",
    "computation and design social policy": "Computation and Design / Social Policy",
    "cultures and societies cultural anthropology": "Cultures and Societies / Cultural Anthropology",
    "cultures and societies sociology": "Cultures and Societies / Sociology",
    "data science": "Data Science",
    "environmental science biogeochemistry": "Environmental Science / Biogeochemistry",
    "environmental science biology": "Environmental Science / Biology",
    "environmental science chemistry": "Environmental Science / Chemistry",
    "environmental science public policy": "Environmental Science / Public Policy",
    "global china studies": "Global China Studies",
    "global health biology": "Global Health / Biology",
    "global health public policy": "Global Health / Public Policy",
    "humanities creative writing and translation": "Humanities / Creative Writing and Translation",
    "humanities literature": "Humanities / Literature",
    "humanities philosophy and religion": "Humanities / Philosophy and Religion",
    "humanities world history": "Humanities / World History",
    "materials science chemistry": "Materials Science / Chemistry",
    "materials science physics": "Materials Science / Physics",
    "molecular bioscience biogeochemistry": "Molecular Bioscience / Biogeochemistry",
    "molecular bioscience biophysics": "Molecular Bioscience / Biophysics",
    "molecular bioscience cell and molecular biology": "Molecular Bioscience / Cell and Molecular Biology",
    "molecular bioscience genetics and genomics": "Molecular Bioscience / Genetics and Genomics",
    "molecular bioscience neuroscience": "Molecular Bioscience / Neuroscience",
    "ppe economic history": "Philosophy, Politics, and Economics / Economic History",
    "ppe philosophy": "Philosophy, Politics, and Economics / Philosophy",
    "ppe political science": "Philosophy, Politics, and Economics / Political Science",
    "ppe public policy": "Philosophy, Politics, and Economics / Public Policy",
    "quantitative political economy economics": "Quantitative Political Economy / Economics",
    "quantitative political economy political science": "Quantitative Political Economy / Political Science",
    "quantitative political economy public policy": "Quantitative Political Economy / Public Policy",
}


def normalize_text(value: str) -> str:
    return " ".join(value.replace("/", " ").replace("-", " ").lower().split())


def normalize_course_code(code: str) -> str:
    """Normalize a section code / variant course code into SUBJECT NNN format.

    Examples:
    - BIOL110-001R -> BIOL 110
    - compsci-201 -> COMPSCI 201
    - STATS 102 -> STATS 102
    """
    if not code:
        return ""

    normalized = code.upper().strip()
    normalized = normalized.split('-')[0]
    normalized = ''.join(ch for ch in normalized if ch.isalnum() or ch.isspace())
    normalized = ''.join(normalized.split())

    subject_chars = []
    number_chars = []
    for ch in normalized:
        if ch.isalpha() and not number_chars:
            subject_chars.append(ch)
        elif ch.isdigit():
            number_chars.append(ch)

    subject = ''.join(subject_chars)
    number = ''.join(number_chars)

    if subject and number:
        return f"{subject} {number}"
    return normalized


def normalize_course_code_set(codes: List[str]) -> Set[str]:
    return {normalize_course_code(code) for code in codes if code}


def resolve_major_name(raw_major: str) -> Optional[str]:
    if not raw_major:
        return None

    normalized = normalize_text(raw_major)

    if normalized in MAJOR_ALIASES:
        return MAJOR_ALIASES[normalized]

    for major_name in MAJOR_REQUIREMENT_COURSES.keys():
        if normalize_text(major_name) == normalized:
            return major_name

    return None


class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CourseRequirement(BaseModel):
    course_code: str
    requirement_type: str
    credits_needed: int


class StudentProfile(BaseModel):
    student_id: str
    major: str
    current_credits: int
    completed_courses: List[str]
    gpa: float = Field(ge=0.0, le=4.0)
    graduation_year: int
    preferences: Dict[str, Any] = {}


class CourseInput(BaseModel):
    code: str
    name: str
    credits: int
    capacity: int
    current_enrollment: int
    prerequisites: List[str] = []
    corequisites: List[str] = []
    core_requirement: bool = False
    major_requirement: bool = False
    difficulty: float = Field(ge=1.0, le=5.0)
    time_slots: List[Dict[str, Any]]


class GraduationRequirement(BaseModel):
    total_credits: int
    major_credits: int
    core_credits: int
    elective_credits: int
    required_courses: List[str]


class RecommendationRequest(BaseModel):
    student_profile: StudentProfile
    courses: List[CourseInput]
    graduation_requirements: GraduationRequirement


class CourseRecommendation(BaseModel):
    course_code: str
    course_name: str
    priority_score: float = Field(ge=0.0, le=1.0)
    fit_score: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    priority_level: PriorityLevel
    recommendation_reason: str
    risk_warning: Optional[str] = None
    prerequisites_met: bool
    helps_graduation: bool
    enrollment_suggestion: str


class RecommendationResponse(BaseModel):
    recommendations: List[CourseRecommendation]
    generated_at: datetime


def load_sample_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "student_profile": {},
        "graduation_requirements": {},
        "courses": [],
        "historical_seat_data": [],
        "recommendation_history": [],
        "monitor_history": []
    }


def save_recommendation_history(student_id: str, recommendations: List[Dict[str, Any]]):
    data = load_sample_data()
    history_entry = {
        "student_id": student_id,
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations
    }
    data.setdefault("recommendation_history", []).append(history_entry)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class RecommendationEngine:
    @staticmethod
    def is_major_related_course(course: CourseInput, profile: StudentProfile, requirements: GraduationRequirement) -> bool:
        canonical_major = resolve_major_name(profile.major)
        major_course_set = MAJOR_REQUIREMENT_COURSES.get(canonical_major, set())

        normalized_course_code = normalize_course_code(course.code)
        normalized_required_courses = normalize_course_code_set(requirements.required_courses)
        normalized_major_course_set = normalize_course_code_set(list(major_course_set))

        return (
            course.major_requirement
            or normalized_course_code in normalized_required_courses
            or normalized_course_code in normalized_major_course_set
        )

    @staticmethod
    def calculate_priority_score(
        course: CourseInput,
        profile: StudentProfile,
        requirements: GraduationRequirement
    ) -> float:
        score = 0.0
        is_major_related = RecommendationEngine.is_major_related_course(course, profile, requirements)

        if course.core_requirement:
            score += 0.25

        # If the course appears in this major's requirements, grant major priority
        if is_major_related:
            score += 0.45

        if normalize_course_code(course.code) in normalize_course_code_set(requirements.required_courses):
            score += 0.15

        credit_ratio = profile.current_credits / requirements.total_credits if requirements.total_credits > 0 else 0

        # In later stages before graduation, put more emphasis on major/graduation requirement courses
        if credit_ratio > 0.75 and is_major_related:
            score += 0.10
        elif credit_ratio > 0.50 and is_major_related:
            score += 0.05

        return min(score, 1.0)

    @staticmethod
    def calculate_fit_score(course: CourseInput, profile: StudentProfile) -> float:
        score = 0.5

        if profile.gpa >= 3.5 and course.difficulty <= 3.0:
            score += 0.2
        elif profile.gpa >= 3.0 and course.difficulty <= 4.0:
            score += 0.1

        prereq_met = all(prereq in profile.completed_courses for prereq in course.prerequisites)
        if prereq_met:
            score += 0.3

        return min(score, 1.0)

    @staticmethod
    def calculate_risk_score(course: CourseInput) -> float:
        enrollment_ratio = course.current_enrollment / course.capacity if course.capacity > 0 else 0
        difficulty_risk = (course.difficulty - 1) / 4.0
        risk = (enrollment_ratio * 0.6) + (difficulty_risk * 0.4)
        return min(risk, 1.0)

    @staticmethod
    def get_priority_level(
        priority_score: float,
        fit_score: float,
        risk_score: float
    ) -> PriorityLevel:
        weighted_score = (priority_score * 0.5) + (fit_score * 0.3) - (risk_score * 0.2)

        if weighted_score >= 0.7:
            return PriorityLevel.HIGH
        elif weighted_score >= 0.4:
            return PriorityLevel.MEDIUM
        return PriorityLevel.LOW

    @staticmethod
    def get_recommendation_reason(
        course: CourseInput,
        profile: StudentProfile,
        requirements: GraduationRequirement
    ) -> str:
        reasons = []
        is_major_related = RecommendationEngine.is_major_related_course(course, profile, requirements)

        if course.core_requirement:
            reasons.append("Core required course")
        if is_major_related:
            reasons.append("Belongs to current major requirements")
        if normalize_course_code(course.code) in normalize_course_code_set(requirements.required_courses):
            reasons.append("Graduation requirement course")

        missing_prereqs = [p for p in course.prerequisites if p not in profile.completed_courses]
        if not missing_prereqs:
            reasons.append("Prerequisites satisfied")
        else:
            reasons.append(f"Missing prerequisites: {', '.join(missing_prereqs)}")

        if profile.current_credits < requirements.total_credits * 0.5:
            reasons.append("Suitable for the current credit stage")
        elif profile.current_credits < requirements.total_credits * 0.8:
            reasons.append("Suitable for mid-stage course planning")
        else:
            reasons.append("Suitable for completing requirements before graduation")

        return "; ".join(reasons) if reasons else "Generally recommended course"

    @staticmethod
    def get_risk_warning(course: CourseInput) -> Optional[str]:
        warnings = []

        enrollment_ratio = course.current_enrollment / course.capacity if course.capacity > 0 else 0
        if enrollment_ratio > 0.9:
            warnings.append("Seats are very limited")
        elif enrollment_ratio > 0.7:
            warnings.append("Limited seat availability")

        if course.difficulty >= 4.0:
            warnings.append("High course difficulty")
        elif course.difficulty >= 3.5:
            warnings.append("Moderate course difficulty")

        return "; ".join(warnings) if warnings else None

    @staticmethod
    def get_enrollment_suggestion(course: CourseInput, priority_level: PriorityLevel) -> str:
        enrollment_ratio = course.current_enrollment / course.capacity if course.capacity > 0 else 0

        if priority_level == PriorityLevel.HIGH:
            if enrollment_ratio > 0.8:
                return "Enroll immediately and set a reminder"
            return "Prioritize enrollment and complete it early"
        elif priority_level == PriorityLevel.MEDIUM:
            if enrollment_ratio > 0.7:
                return "Enroll as soon as possible and monitor seat changes"
            return "Enroll at an appropriate time and plan accordingly"
        return "Can be used as a backup option depending on the situation"


@router.post("", response_model=RecommendationResponse)
async def get_course_recommendations(request: RecommendationRequest):
    try:
        recommendations = []
        engine = RecommendationEngine()

        for course in request.courses:
            priority_score = engine.calculate_priority_score(
                course, request.student_profile, request.graduation_requirements
            )
            fit_score = engine.calculate_fit_score(course, request.student_profile)
            risk_score = engine.calculate_risk_score(course)

            priority_level = engine.get_priority_level(priority_score, fit_score, risk_score)

            prerequisites_met = all(
                prereq in request.student_profile.completed_courses
                for prereq in course.prerequisites
            )

            helps_graduation = (
                course.core_requirement
                or engine.is_major_related_course(
                    course, request.student_profile, request.graduation_requirements
                )
            )

            recommendation = CourseRecommendation(
                course_code=course.code,
                course_name=course.name,
                priority_score=round(priority_score, 2),
                fit_score=round(fit_score, 2),
                risk_score=round(risk_score, 2),
                priority_level=priority_level,
                recommendation_reason=engine.get_recommendation_reason(
                    course, request.student_profile, request.graduation_requirements
                ),
                risk_warning=engine.get_risk_warning(course),
                prerequisites_met=prerequisites_met,
                helps_graduation=helps_graduation,
                enrollment_suggestion=engine.get_enrollment_suggestion(course, priority_level)
            )
            recommendations.append(recommendation)

        recommendations.sort(key=lambda x: (x.priority_score, x.fit_score, -x.risk_score), reverse=True)

        save_recommendation_history(
            request.student_profile.student_id,
            [rec.model_dump() for rec in recommendations]
        )

        return RecommendationResponse(
            recommendations=recommendations,
            generated_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")