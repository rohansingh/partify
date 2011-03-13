#!/usr/bin/env python
"""
GrooveWalrus: Tinysong
Copyright (C) 2009
11y3y3y3y43@gmail.com
http://groove-walrus.turnip-town.net
-----
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""

import urllib.request, urllib.error, urllib.parse
try:
    import json
except ImportError:
    from main_thirdp import simplejson as json
#import xml.etree.ElementTree as ET

#Example
#    http://tinysong.com/s/Beethoven?limit=3
#Returns
#    http://tinysong.com/DjY; 564004; Fur Elise; 1833; Beethoven; 268605; The Best Of Beethoven; http://listen.grooveshark.com/song/Fur_Elise/564004
#    http://tinysong.com/N7c; 716886; Moonlight Sonata; 1833; Beethoven; 168699; Ludwig Van Beethoven; http://listen.grooveshark.com/song/Moonlight_Sonata/716886
#    http://tinysong.com/29V; 564008; Moonlight; 1833; Beethoven; 268605; The Best Of Beethoven; http://listen.grooveshark.com/song/Moonlight/564008 


# http://tinysong.com/s/Beethoven?limit=3
# http://www.tinysong.com/index.php?s=u2+lemon
"""
new json format
[{"Url":"http:\/\/tinysong.com\/7Wm7","SongID":8815585,"SongName":"Moonlight Sonata","ArtistID":1833,"ArtistName":"Beethoven","AlbumID":258724,"AlbumName":"Beethoven"},{"Url":"http:\/\/tinysong.com\/6Jk3","SongID":564004,"SongName":"Fur Elise","ArtistID":1833,"ArtistName":"Beethoven","AlbumID":268605,"AlbumName":"Beethoven"},{"Url":"http:\/\/tinysong.com\/8We2","SongID":269743,"SongName":"The Legend Of Lil' Beethoven","ArtistID":7620,"ArtistName":"Sparks","AlbumID":204019,"AlbumName":"Sparks"}]
http://tinysong.com/s/Beethoven?format=json&limit=3
""" #'

TRACK_GETINFO = "http://tinysong.com/s/"
Q_LIMIT = "?format=json&key=cd88f6b636150a11797b572cd9f9011f&limit="


    
# ===================================================================
class Tsong(object):
    def __init__(self):
        pass
        #self.last_similar_file_name = ''        
        #self.last_country_name = ''

    def get_search_results(self, query_string, limit=32):
        # http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&artist=cher&track=believe
        # get an image for track requested
        # <lfm <album <image
        results_array = []
        # replace "of" "and" "a" "the"
        small_words_array = [" the ", " The ", "The ", "the ", " Of ", " And ", " A ", " Are ", " are ", " I ", " if ", " If ", " of ", " and ", " a ", "A ", " is ", " Is ", " to ", " To ", "I'm ", " i'm ", " I'm ", "I'd ", " i'd ", " I'd "]        
        #query_string = query_string.lower()
        for x in small_words_array:
            query_string = query_string.replace(x, ' ')
        query_string = url_quote(query_string)
        #print query_string
        data_url = TRACK_GETINFO + query_string + Q_LIMIT + str(limit)
        print(data_url)
        
        headers = { 'User-Agent' : "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 (.NET CLR 3.5.30729)" }
        url_connection = urllib.request.Request(data_url.replace(' ', '+'), None, headers)
        #raw_results = url_connection.read()
        response = urllib.request.urlopen(url_connection)
        raw_results = response.read()

        results_array = json.loads(bytes.decode(raw_results))

        counter = 0
        # cycle through the results and string any integers
        for x in results_array:            
            #cycle through each dictionary
            for key, value in list(x.items()):
                if IsInteger(value):
                     results_array[counter][key] = str(value)
            counter = counter + 1
        #results_array = raw_results.split('\n')
        return results_array
   
        
def IsInteger(x):
    try:
        if int(x) == x:
            return True
    except:
        return False
    

charset = 'utf-8'
        
def url_quote(s, safe='/', want_unicode=False):
    """
    Wrapper around urllib.quote doing the encoding/decoding as usually wanted:
    
    @param s: the string to quote (can be str or unicode, if it is unicode,
              config.charset is used to encode it before calling urllib)
    @param safe: just passed through to urllib
    @param want_unicode: for the less usual case that you want to get back
                         unicode and not str, set this to True
                         Default is False.
    """
    if isinstance(s, str):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    s = urllib.parse.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
     
# ===================================================================            