# TLS-SAK - TLS Swiss Army Knife
# https://github.com/RBT-itsec/TLS-SAK
# Copyright (C) 2016 by Mirko Hansen / ARGE Rundfunk-Betriebstechnik
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# generic imports
import json

# TLS SAK imports
from lib.tls.tlsexceptions import TLS_Exception

class TLS_Rating:
    def __init__(self, status='unknown', rating=0, pfs=False, children={}):
        self.status = status
        self.rating = rating
        self.pfs = pfs
        self.children = children

    def __getattr__(self, name):
        if name in self.children:
            return self.children[name]
        return None

    def __dir__(self):
        return self.children.keys()

    def __str__(self):
        children = ''
        for k in self.children:
            children += ';'
            children += k + '='
            children += str(self.children[k])
        return self.status + '/' + str(self.rating) + children

    @staticmethod
    def getParentRating(ratings=None):
        ratingList = ratings
        if type(ratingList) is dict:
            ratingList = [item for item in ratingList.values()]
        if type(ratingList) is not list:
            raise TLS_Exception('ratingList is not a list: ' + str(ratingList))

        unset = True
        rating = 0
        status = 'unknown'
        pfs = False

        for item in ratingList:
            if type(item) is not TLS_Rating:
                raise TLS_Exception('item in ratingList is not a rating: ' + str(item))
            if unset or item.rating < rating:
                unset = False
                rating = item.rating
                status = item.status
            if item.pfs:
                pfs = True

        return TLS_Rating(status=status, rating=rating, pfs=pfs, children=ratings)

class TLS_Ratings_Database():
    instance = None

    @staticmethod
    def getInstance():
        if TLS_Ratings_Database.instance is None:
            TLS_Ratings_Database.instance = TLS_Ratings_Database()
        return TLS_Ratings_Database.instance

    def __init__(self):
        self.loadDatabase()

    def loadDatabase(self):
        with open('data/ratings.json') as f:
            data = f.read().replace('\n', '')

        self.database = json.loads(data)

    def getRating(self, param, setting, default=TLS_Rating(status='unknown', rating=0)):
        if param in self.database and setting in self.database[param]:
            return TLS_Rating(**self.database[param][setting])
        else:
            return default

    def getAllParameters(self):
        return self.database.keys()

    def getAllRatings(self, param):
        if param not in self.database:
            return {}
        return self.database[param]
