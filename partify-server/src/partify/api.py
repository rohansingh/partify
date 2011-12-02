'''
Created on Jan 18, 2011

@author: Rohan
'''

import time
from uuid import uuid4

import cherrypy
from cherrypy import request

from pymongo import *
from pymongo.objectid import ObjectId
from bson.code import Code

from pyechonest import *
config.ECHO_NEST_API_KEY = "HPBS0ECKDVKGRUIGR"

from groovewalrus import tinysong

mongoConnection = Connection("localhost", 27017)
db = mongoConnection.partify

db.devices.ensure_index([("location", GEO2D)])

class Api:
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def setLocation(self):
        device = { "location": [request.json["lat"], request.json["long"]],
                   "accuracy": request.json["accuracy"],
                   "last_location_update": time.time() }
        
        query = ({ "deviceId": request.json["deviceId"] } if "deviceId" in request.json
            else { "deviceId": str(uuid4()) })
            
        device = db.devices.find_and_modify(query, { "$set": device }, True, new = True)
        
        return { "deviceId":  device["deviceId"] }
    
    @cherrypy.expose
    def getNearbyDevices(self):
        (lat, long, maxDistance) = (request.json["lat"],
                                 request.json["long"],
                                 Api._meters_to_degrees(request.json["maxDistance"]))

        nearby = self._get_nearby_devices(lat, long, maxDistance)
        
        return { "count": nearby.count() }
    
    @cherrypy.expose
    def setTracks(self):
        device = { "last_tracks_update": time.time() }
        
        query = ({ "deviceId" : request.json["deviceId"] } if "deviceId" in request.json
            else { "deviceId": str(uuid4()) })
            
        device["tracks"] = list({ "artist_name": track["artistName"], "track_name": track["trackName"]}
                            for track in request.json["tracks"])
        
        device = db.devices.find_and_modify(query, { "$set": device }, True, new = True)
        
        return { "deviceId": device["deviceId"] }
    
    @cherrypy.expose
    def getPlaylist(self):
        (maxDistance, maxResults, lat, long) = (request.json["maxDistance"],
                                                request.json["maxResults"],
                                                request.json["lat"],
                                                request.json["long"])
        player = { "location": [lat, long], "last_request_date": time.time() }
        
        playerId = request.json["playerId"] if "playerId" in request.json else str(uuid4())
        query = ({ "player_id" : playerId })
        
        player = db.players.find_and_modify(query, { "$set": player }, True, new = True)
        
        if "echo_nest_ticket" not in player:
            self._create_echo_nest_catalog(playerId, lat, long, maxDistance)
            return { "playerId": playerId, "ready": False }
        
        elif  not self._is_catalog_ready(player):
            return { "playerId": playerId, "ready": False }
        
        else:
            db.players.find_and_modify(query, { "$unset": { "echo_nest_ticket": 1 }})
            
            return { "player_id": playerId, "ready": True,
                     "tracks": list(self._get_echo_nest_playlist(player, maxResults)) }
        
    def _is_catalog_ready(self, player):
        cat = catalog.Catalog(player["catalog_id"], "song")
        
        status = cat.status(player["echo_nest_ticket"])
        
        return (status["ticket_status"] != "pending")
    
    def _get_echo_nest_playlist(self, player, maxResults):
        sessionId = player["echo_nest_session"] if "echo_nest_session" in player else None
        
        songs = playlist.Playlist(session_id = sessionId,
                                  type = 'catalog-radio',
                                  seed_catalog = player["catalog_id"])
        
        db.players.find_and_modify({ "_id": player["_id"]}, { "$set": { "echo_nest_session": songs.session_id }})
        
        totalSongs = 0
        foundSongs = 0
        while foundSongs < maxResults and totalSongs < maxResults * 4:
            totalSongs += 1
            
            song = songs.get_next_song();
            tinySongId = self._get_tinysong_id(song.artist_name, song.title)
            
            if not tinySongId:
                continue
            else:
                foundSongs += 1
                yield { "artistName": song.artist_name, "trackName": song.title,
                        "tinySongId": tinySongId }
    
    def _get_tinysong_id(self, artistName, trackName):
        results = tinysong.Tsong().get_search_results("%s %s" % (artistName, trackName), 1)
        
        if results:
            return results[0]["SongID"]
        else:
            return None
        
                   
    def _create_echo_nest_catalog(self, playerId, lat, long, maxDistance):
        newCatalog = catalog.Catalog(playerId, "song")
        
        items = [{"action": "update",
                   "item": { "item_id": str(uuid4()),
                             "artist_name": track["artist_name"],
                             "song_name": track["track_name"] }
                   }
                 for track in self._get_nearby_tracks(lat, long, maxDistance)]
        
        ticket = newCatalog.update(items)
        
        db.players.find_and_modify({ "player_id": playerId },
                                   { "$set": { "catalog_id": newCatalog.id,
                                               "echo_nest_ticket": ticket } })
        
    def _get_nearby_tracks(self, lat, long, maxDistance):
        map = Code("""function () {
            var lat = %(lat)s;
            var long = %(long)s;
            var maxDistance = %(maxDistance)s;
        
            function getDistance(location) {
                var lat2 = location[0];
                var lon2 = location[1];
        
                var R = 6371000; // Radius of the earth in meters
                var dLat = toRad(lat2 - lat); // Javascript functions in radians
                var dLon = toRad(lon2 - long);
        
                var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                    Math.cos(toRad(lat)) * Math.cos(toRad(lat2)) *
                    Math.sin(dLon / 2) * Math.sin(dLon / 2);
        
                var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
                var d = R * c; // Distance in meters
                return d;
            }
        
            function toRad(degrees) { // convert degrees to radians 
                return degrees * Math.PI / 180;
            }
            
            var distance = getDistance(this.location);
            if (distance < maxDistance + this.accuracy) this.tracks.forEach(function (z) {
                emit(z, {
                    count: 1
                })
            });
        }
        """ % { "lat": lat, "long": long, "maxDistance": maxDistance })
        
        reduce = """function (key, values) {
            var total = 0;
            for (var i = 0; i < values.length; i++)
            total += values[i].count;
            return {
                count: total
            };
        }
        """
        
        results = db.devices.map_reduce(map, reduce)
        
        tracks = [result["_id"] for result in results.find()];
        
        return tracks;
        
    def _get_nearby_devices(self, lat, long, maxDistance):
        return db.devices.find({ "location":
                          { "$within":
                           { "$center": [[lat, long], maxDistance] }}})
    
    @staticmethod
    def _meters_to_degrees(meters):
        return meters / 111000.0
    
