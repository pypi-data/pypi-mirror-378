"""
TestResultsExportsFactory tests and validate the city results exports
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2019 - 2025 Concordia CERC group
Project Coder Koa Wells kekoa.wells@concordia.ca
"""
import glob
import subprocess
import csv
import json
from pathlib import Path
from unittest import TestCase

from hub.imports.geometry_factory import GeometryFactory
from hub.imports.construction_factory import ConstructionFactory
from hub.imports.usage_factory import UsageFactory
from hub.imports.energy_systems_factory import EnergySystemsFactory
from hub.imports.weather_factory import WeatherFactory
from hub.imports.results_factory import ResultFactory
from hub.exports.exports_factory import ExportsFactory
from hub.exports.energy_building_exports_factory import EnergyBuildingsExportsFactory
from hub.exports.results_factory import ResultsExportFactory
from hub.helpers.dictionaries import Dictionaries


class TestResultsExportFactory(TestCase):
  """
  TestResultsExportFactory class contains the unit tests for city result export functionality
  """

  def setUp(self):
    """
    Test setup
    :return: None
    """
    self.input_file = (Path(__file__).parent / 'tests_data/test.geojson').resolve()
    self.output_path = (Path(__file__).parent / 'tests_outputs').resolve()

    self.city = GeometryFactory(file_type='geojson',
                                path=self.input_file,
                                height_field='citygml_me',
                                year_of_construction_field='ANNEE_CONS',
                                function_field='CODE_UTILI',
                                aliases_field=['gml_id'],
                                function_to_hub=Dictionaries().montreal_function_to_hub_function).city
    for building in self.city.buildings:
      building.energy_systems = ['system 1 gas']
      building.energy_systems_archetype_name = building.energy_systems[0]
    ConstructionFactory('nrcan', self.city).enrich()
    UsageFactory('nrcan', self.city).enrich()
    WeatherFactory('epw', self.city).enrich()
    ExportsFactory('sra', self.city, self.output_path).export()
    sra_file = Path(f'{self.output_path}/{self.city.name}_sra.xml').resolve()
    subprocess.run(["sra", sra_file],
                   timeout=270,
                   capture_output=True,
                   check=True)
    ResultFactory('sra', self.city, self.output_path).enrich()
    EnergySystemsFactory('montreal_custom', self.city).enrich()
    EnergyBuildingsExportsFactory('insel_monthly_energy_balance', self.city, self.output_path).export()

    insel_files = glob.glob(f'{self.output_path}/*.insel')
    for insel_file in insel_files:
      subprocess.run(['insel', str(insel_file)], stdout=subprocess.DEVNULL)

    ResultFactory('insel_monthly_energy_balance', self.city, self.output_path).enrich()


  def test_csv(self):
    """
    Test ResultsExportFactory with csv handler
    """
    ResultsExportFactory(self.city, 'csv', self.output_path, filename='results_export_factory_test').export()
    self.assertTrue(Path(f"{self.output_path}/results_export_factory_test.csv").exists())

    with open(f"{self.output_path}/results_export_factory_test.csv", 'r', encoding='utf-8') as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      self.assertEqual(len(list(csv_reader)), 18)
      for row in csv_reader:
        self.assertEqual(len(row), 34)


  def test_geojson(self):
    """
    Test ResultsExportFactory with geojson handler
    """
    ResultsExportFactory(self.city, 'geojson', self.output_path, filename='results_export_factory_test').export()
    self.assertTrue(Path(f"{self.output_path}/results_export_factory_test.geojson").exists())

    with open(f"{self.output_path}/results_export_factory_test.geojson", 'r', encoding='utf-8') as geojson_file:
      city = json.load(geojson_file)
      buildings = city['features']
      self.assertEqual(len(buildings), 17)

      for building in buildings:
        building_properties = building['properties']
        self.assertEqual(len(building_properties.keys()), 34)
