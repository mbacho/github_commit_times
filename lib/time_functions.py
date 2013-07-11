import pytz
import datetime
import urllib2
import json


def gps_from_location(location):
    """ Returns a tuple with latitude and longitude of the location provided """

    url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false"
    data = urllib2.urlopen(url % urllib2.quote(location))
    json_string = data.read()
    json_obj = json.loads(json_string)
    lat = json_obj['results'][0]['geometry']['location']['lat']
    long = json_obj['results'][0]['geometry']['location']['lng']
    return (lat, long)


def timezone_from_gps(lat, long):
    """ Returns the timezone of the latitude and longitude """

    url = "https://maps.googleapis.com/maps/api/timezone/json?location=%s,%s&timestamp=1331161200&sensor=false"
    data = urllib2.urlopen(url % (lat, long))
    json_string = data.read()
    json_obj = json.loads(json_string)
    return json_obj['timeZoneId']


def utc_time_from_timezone(date_time, timezone):
    """ Returns the UTC datetime from a datetime in a different timezone """

    tz = pytz.timezone(timezone)
    return pytz.utc.localize(date_time).astimezone(tz)
