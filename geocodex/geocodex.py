# Geocoding Proxy Project Module

from abc import ABCMeta, abstractmethod
from urllib.request import urlopen
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.error import URLError, HTTPError
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import json

google_url = 'https://maps.googleapis.com/maps/api/geocode/json'
here_url = 'https://geocoder.cit.api.here.com/6.2/geocode.json'

class Geocode:
  """The Geocode spatial representation for a postal address.

    Attributes:
        address (str): string representation of address
        lat (str): Latitude
        ln (:obj:`int`, optional): Longitude
  """

  def __init__(self, address, lat, lng):
    self.address = address
    self.lat = lat
    self.lng = lng


class GeocodeHTTPRequestHandler(BaseHTTPRequestHandler):
  """The Geocode HTTP Request Handler.

     Provides REST resources.
  """
  def __init__(self, request, client_address, server):
    """
    Initialize new geocode HTTP request handler

    Args:
        geocoder (GeocodeServiceProxy): Geocode service proxy chained
          with fallbacks if service should fail.
    """
    self.geocoder = GoogleGeocodeServiceProxy(GoogleGeocodeDataMapper())
    self.geocoder.set_fallback = HereGeocodeServiceProxy(
        HereGeocodeDataMapper())
    super().__init__(request, client_address, server)

  def do_GET(self):
    """
    HTTP GET function for service.
    """
    if re.search('/geocode/json/*', self.path):
      try:
        query = parse_qs(urlparse(self.path).query)
        address = query['address']
        g_code = self.geocoder.geocode(address)
        response = json.dumps(g_code.__dict__, sort_keys=True, indent=4)
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())
      except Exception:
        self.send_response(400, 'Bad Request')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
    else:
      self.send_response(403)
      self.send_header('Content-Type', 'application/json')
      self.end_headers()
    return


class GeocodeDatamapper(metaclass=ABCMeta):
  """
  Abstract class for mapping json date received from service into Geocode object.
  """
  @abstractmethod
  def buildGeocode(self, json):
    pass


class GoogleGeocodeDataMapper(GeocodeDatamapper):
  def buildGeocode(self, json):
    g_code = None
    if json is not None:
      try:
        # Service returns multiple results.  For now just use first.
        result = json["results"][0]
        address = result["formatted_address"]
        location = result["geometry"]["location"]
        g_code = Geocode(address, location["lat"], location["lng"])
      except (KeyError, IndexError) as ex:
        print(ex)
    return g_code


class HereGeocodeDataMapper(GeocodeDatamapper):
  def buildGeocode(self, json):
    g_code = None
    if json is not None:
      try:
        result = json["Response"]["View"][0]["Result"][0]
        location = result["Location"]
        address = location["Address"]["Label"]
        g_code = Geocode(address, location["DisplayPosition"]
                         ["Latitude"], location["DisplayPosition"]["Longitude"])
      except (KeyError, IndexError) as ex:
        print(ex)
    return g_code


class GeocodeServiceProxy(metaclass=ABCMeta):
  """
  Abstract geocoding service handler.

  Implementing classes should set fallback class in case of service failure
  or empty result and throw Exception to continue to fallback service proxy.
  """

  def __init__(self, datamapper, fallback=None):
    self.datamapper = datamapper
    self.fallback = fallback

  def set_fallback(self, fallback):
    """
    Set the next service to handle request in case of failure.

    Args:
        fallback (GeocodeHTTPRequestHandler): Next responsible request handler.

    Returns:
        GeocodeHTTPRequestHandler: Next responsible request handler.
    """
    self.fallback = fallback
    return self.fallback

  def geocode(self, address):
    """
    Resolve the lat, lng coordinates for an address

    Args:
      address (String): a standard postal address description

    Returns:
      Geocode: location latitude and longitude
    """
    try:
      return self.handle_request(address)
    except Exception as ex:
      if self.fallback is not None:
        self.fallback.geocode(address)

  @abstractmethod
  def handle_request(self, address):
    pass


class GoogleGeocodeServiceProxy(GeocodeServiceProxy):
  def handle_request(self, address):
    g_code = None
    e_address = urlencode({'address': address})
    try:
      response = urlopen(google_url+'?address=' + e_address + '&key=' + google_api_key)
      if response.status == HTTPStatus.OK:
        data = json.loads(response.read())
        g_code = self.datamapper.buildGeocode(data)
      else:
        raise(ServiceException(status=HTTP.Status, message='Not OK'))
    except URLError as e:
      raise(ServiceException(message=e.reason))
    except HTTPError as e:
      raise(ServiceException(status=e.code, message=e.reason))

    return g_code


class HereGeocodeServiceProxy(GeocodeServiceProxy):
  def handle_request(self, address):
    g_code = None
    e_address = urlencode({'address': address})
    with urlopen(here_url+'?app_id='+here_api_id+'&app_code='+here_api_code+'&searchtext=' + e_address) as response:
      if response.status != HTTPStatus.OK:
        raise(Exception('Not OK'))
      data = json.loads(response.read())
      g_code = self.datamapper.buildGeocode(data)
    return g_code


class ServiceException(Exception):
  """Exception raised for services.

  Attributes:
      status -- http status returned from service
      message -- explanation of the error if available
  """

  def __init__(self, status, message):
    self.status = status
    self.message = message


def run(server_class=HTTPServer, handler_class=GeocodeHTTPRequestHandler, config=None):
  if (config is not None):
    global google_api_key, here_api_id, here_api_code
    google_api_key = config['google']['api_key']
    here_api_id=config['here']['app_id']
    here_api_code=config['here']['app_code']
  server_address=('', 8000)
  httpd=server_class(server_address, handler_class)
  print('Server starting ...')
  httpd.serve_forever()
