# Geocoding Proxy Service
Jason Dinger / jakedinger@gmail.com

A simple network service that can resolve the lat, lng coordinates for that address
by using third party geocoding services. The service provides a RESTful HTTP interface and uses JSON for data serialization.

The service uses two different third party geocoding services. One serves as
a primary service with an additional backup service used for each request.

Here Geocoder API
https://developer.here.com/documentation/geocoder/topics/quick-start.html

Google Geocoding API https://developers.google.com/maps/documentation/geocoding/start

# How to configure and run the application.

Service credentials must be first retrieved by registering with the above services.
These credentials are then placed in a configuration file used when running the application.

And example config file can be found at config.ini.

Once configured, an application server can be started with
  * python -m geocodex myconfig.ini

When the server is running, the geocode service can be accessed with endpoint
http://localhost:8000/geocode/json?address=YOUR_ADDRESS, where YOUR_ADDRESS is a URL-encoded address.  For example, 
http://localhost:8000/geocode/json?address=1600+Pennsylvania_Ave,+Washington,+DC

# How to run the suite of automated tests.

The automated tests can be run at the command line with
  * python -m unittest discover geocodex

# Additional Comments
This application was built using Python 3.6.
