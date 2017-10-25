from unittest import TestCase, skip
from unittest.mock import Mock, MagicMock, patch
from geocodex import Geocode, GoogleGeocodeServiceProxy, GoogleGeocodeDataMapper, HereGeocodeServiceProxy, HereGeocodeDataMapper

import json
from os import path


class TestBuildGeocodeGoogle(TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_buildGeocode(self):
    with open(path.join(path.dirname(__file__), 'google_geocode.json')) as data_file:
      self.google_json = json.load(data_file)
    mapper = GoogleGeocodeDataMapper()
    g_code = mapper.buildGeocode(self.google_json)
    self.assertIsInstance(g_code, Geocode)
    self.assertEqual(38.8976633, g_code.lat)
    self.assertEqual(-77.03657389999999, g_code.lng)
    self.assertEqual(
        "1600 Pennsylvania Ave NW, Washington, DC 20500, USA", g_code.address)

  def test_buildGeocode_errormsg(self):
    with open(path.join(path.dirname(__file__), 'google_geocode_error.json')) as data_file:
      self.google_json = json.load(data_file)
    mapper = GoogleGeocodeDataMapper()
    g_code = mapper.buildGeocode(self.google_json)
    self.assertIsNone(g_code)

  def test_buildGeocode_none(self):
    mapper = GoogleGeocodeDataMapper()
    g_code = mapper.buildGeocode(None)
    self.assertIsNone(g_code)


class TestBuildGeocodeHere(TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_buildGeocode(self):
    with open(path.join(path.dirname(__file__), 'here_geocode.json')) as data_file:
      self.here_json = json.load(data_file)
    mapper = HereGeocodeDataMapper()
    g_code = mapper.buildGeocode(self.here_json)
    self.assertIsInstance(g_code, Geocode)
    self.assertEqual(41.88432, g_code.lat)
    self.assertEqual(-87.6387699, g_code.lng)
    self.assertEqual(
        "425 W Randolph St, Chicago, IL 60606, United States", g_code.address)

  def test_buildGeocode_errormsg(self):
    with open(path.join(path.dirname(__file__), 'here_geocode_error.json')) as data_file:
      self.here_json = json.load(data_file)
    mapper = HereGeocodeDataMapper()
    g_code = mapper.buildGeocode(self.here_json)
    self.assertIsNone(g_code)

  def test_buildGeocode_none(self):
    mapper = HereGeocodeDataMapper()
    g_code = mapper.buildGeocode(None)
    self.assertIsNone(g_code)


class TestGeocodeServices(TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_fallback(self):
    g = GoogleGeocodeServiceProxy(GoogleGeocodeDataMapper)
    h = HereGeocodeServiceProxy(HereGeocodeDataMapper)
    g.set_fallback(h)
    g.handle_request = Mock(side_effect=Exception('Oh no!'))
    g_code = Geocode("https://www.locateme.com",33.2345,-43.23452345)
    h.handle_request = Mock(return_value=g_code)
    g.geocode("https://www.geolocator.com")
    g.handle_request.assert_called()
    h.handle_request.assert_called()
