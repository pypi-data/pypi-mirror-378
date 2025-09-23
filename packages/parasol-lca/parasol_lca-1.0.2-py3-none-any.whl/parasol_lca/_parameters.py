# coding=utf-8
#
# Copyright 2021-2022 Romain BESSEAU <romain.besseau@ec.europa.eu>
# Copyright 2022-2024 Alejandra CUE GONZALEZ <alejandra.cue_gonzalez@minesparis.psl.eu>
# Copyright 2022-2024 Benoît GSCHWIND <benoit.gschwind@minesparis.psl.eu>
# Copyright 2022-2024 MINES Paris
#
# This file is part of "parasol-lca" and you can used under the
# term of European Union Public Licence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# European Union Public Licence for more details.
#
# Version: 22 April 2025
#
# Code authors: Romain BESSEAU, Benoît GSCHWIND, Alejandra CUE GONZALEZ
#
import lca_algebraic as agb

# Electricity dataset

# Switch parameter for electricity mix

def _ensure_Manufacturing_electricity_mix(context):
    return agb.newEnumParam(
    dbname = context.target_database,
    name = 'Manufacturing_electricity_mix',
    values = ['FR', 'EU', 'US', 'CN','World', 'PV', 'Nuclear','Coal', 'CO2_content'],
    default = 'World',
    description = "Switch on electricty mix used for PV manufacture",
    group = 'PV manufacture')

def _ensure_Electricity_mix_CO2_content(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Electricity_mix_CO2_content",
    default = 0.5, min = 0, max = 1,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV manufacture",
    unit = "ratio or quasi-equivalent in kgCO2eq/kWh")

# Mounting System

# Define parameters for the mounting system
def _ensure_roof_ratio(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "roof_vs_ground_ratio",
    default = 1.0, min = 0.0, max = 1.0,
    distrib = agb.params.DistributionType.LINEAR,
    group = "PV install",
    description = "Proportion of rooftop installations",
    unit = 'fraction')

def _ensure_mounting_system_weight_total(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Mounting_system_weight_total",
    default = 5, min = 2, max = 11.5,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV intall",
    unit = "kg/m²")

def _ensure_mounting_system_weight_alu(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Mounting_system_weight_alu",
    default = 1.5, min = 0.67, max = 2.4,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV install",
    unit = "kg/m²")

def _ensure_mounting_system_weight_wood(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Mounting_system_weight_wood",
    default = 0, min = 0, max = 10,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV install",
    unit = "kg/m²")

def _ensure_ground_coverage_ratio(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = 'Ground_coverage_ratio',
    default = 0.4, min = 0.2, max = 0.5,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV install",
    unit = "fraction",
    description = "Ground coverage ratio")

def _ensure_lifetime(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = 'Power_plant_lifetime',
    default = 30, min = 20, max = 40,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV operation",
    unit = "year",
    description = "Lifetime of the PV plant")

# Electrical installation
def _ensure_P_install(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Power_plant_capacity",
    default = 100,
    min = 3, max = 10000,
    group = "PV install", unit = "kWp")

def _ensure_recycling_rate(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Recycling_rate",
    default=0.9, min=0, max=1,
    group = "PV recycle",
    unit="fraction")

# Silicon production

#parameter to adjust the amount of electricity for silicon manufacturing

def _ensure_silicon_elec_intensity(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Silicon_production_electricity_intensity",
    default = 30, min = 11, max = 180,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV manufacture",
    unit = "kWh/kg")

def _ensure_silicon_heat_intensity(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Silicon_production_heat_intensity",
    default = 185, min = 0, max = 185,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV manufacture",
    unit = "MJ/kg")

def _ensure_silicon_casting_elec_intensity(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Silicon_casting_electricity_intensity",
    default = 15, min = 10, max = 30,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV manufacture",
    unit = "kWh/kg")

## Wafer

# Parameters
def _ensure_diamond_wiring(context):
    return agb.newBoolParam(
    dbname = context.target_database,
    name = "Diamond_wiring_cutting",
    default = 1,
    distrib = agb.DistributionType.LINEAR,
    group = "PV manufacture")

def _ensure_wafer_thickness(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Wafer_thickness",
    default=160, min=128, max=190,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV manufacture",
    unit="µm")

def _ensure_kerf_loss(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Kerf_loss",
    default = 0.3, min=0.3, max=0.50,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV manufacture",
    unit="fraction")

def _ensure_sic_recycled_share(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "SiC_recycled_share",
    default = 0.0, min=0.0, max=0.9,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV install",
    unit="fraction")

def _ensure_manufacturing_efficiency(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Manufacturing_efficiency_gains",
    default = 0, min=0, max=1,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV manufacture",
    description="Manufacturing efficiency gain (elec for wafer)",
    unit="fraction")

# PV Cell manufacturing

def _ensure_silver_amount(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Silver_content",
    default = 9.6, min=2, max=9.6,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV manufacture",
    description="Silver amount for PV cell", unit="g/m²")

# PV Panel

def _ensure_m_aluminium_frame(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Aluminium_frame_surfacic_weight",
    default = 1.5, min=0, max=2.63,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV install",
    unit="kg/m2")

def _ensure_bifaciale(context):
    return agb.newBoolParam(
    dbname = context.target_database,
    name = "Bifaciale_modules",
    default = False,
    group="PV install")

def _ensure_Recycling_rate_Al(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Recycling_rate_Al",
    default = 0.96, min=0.56, max=1,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV recycle",
    unit="fraction")

def _ensure_Recycling_rate_Cu(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Recycling_rate_Cu",
    default = 0.75, min=0.44, max=0.96,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV recycle",
    unit="fraction")

def _ensure_recycling_rate_glass(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Recycling_rate_glass",
    default = 0.9, min=0.6, max=1,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV recycle",
    unit="fraction")

def _ensure_electricity_recycling(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Electricity_consumption_for_recycling",
    default = 50, min=0, max=250,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV recycle",
    description="elec used for recycling", unit="kWh/t")

def _ensure_heat_recycling(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Heat_consumption_for_recycling",
    default = 76, min=0, max=150,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV recycle",
    description="Heat for recycling", unit="MJ/t")

def _ensure_glass_thickness(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Glass_thickness",
    default = 4, min=2, max=4,
    distrib = agb.DistributionType.TRIANGLE,
    group="PV install",
    unit = "mm")

# PV System
def _ensure_module_efficiency(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "PV_module_efficiency",
    default=0.22, min=0.15, max=0.23,
    distrib = agb.DistributionType.TRIANGLE,
    group = "PV install",
    unit="kWp/m²")

def _ensure_inverter_lifetime(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Inverter_lifetime",
    group = "PV operation",
    default=15, min=10, max=30,
    distrib = agb.DistributionType.TRIANGLE,
    unit="year")

def _ensure_inverter_weight_per_kW(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Inverter_weight_per_kW",
    default=2, min=1, max=6,
    group = 'PV install',
    label_fr="poids onduleur",
    unit="kg/kWp")

def _ensure_d_lorry(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Transport_distance_lorry",
    default = 1000, min=40, max=2000,
    unit="km",
    group="PV transport")

def _ensure_d_train(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Transport_distance_train",
    default=500, min=100, max=600,
    unit="km",
    group="PV transport")

def _ensure_d_sea(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Transport_distance_boat",
    default=5000, min=2000, max=6000,
    unit="km",
    group="PV transport")

def _ensure_electrical_installation_weight_per_kW(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = "Electrical_installation_specific_weight",
    default = 3, min=2.15, max=4.6,
    unit="kg/kW",
    group="PV install")

def _ensure_kWhperkWp(context):
    return agb.newFloatParam(
    dbname = context.target_database,
    name = 'Normalised_annual_PV_production_kWh_per_kWp',
    default = 1300, min = 900, max = 1700,
    distrib = agb.params.DistributionType.TRIANGLE,
    group = "PV operation",
    unit = "kWh/kWp/year",
    description = "Durée de vie")
