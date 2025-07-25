# -*- coding: utf-8 -*-

'''
    dmdamedia Add-on
    Copyright (C) 2020

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys, xbmcgui
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl


params = dict(parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

url = params.get('url')

search = params.get('search')

thumb = params.get('thumb')

page = params.get('page')

mtype = params.get('type')

post = params.get('post')

nume = params.get('nume')

season = params.get('season')

duration = 0 if params.get('duration') == None else params.get('duration') 

if action == None:
    navigator.navigator().getRoot()

if action == 'submenu':
    navigator.navigator().getSubMenuItems(url)

elif action == 'movies':
    navigator.navigator().getMovies(url, page)

elif action == 'movie':
    navigator.navigator().getSources(url, season)

elif action == 'playmovie':
    navigator.navigator().playmovie(mtype, post, nume)

elif action == 'playtablemovie':
    navigator.navigator().playTableMovie(url)

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'historysearch':
    navigator.navigator().getResults(search, page)

elif action == 'newsearch':
    navigator.navigator().doSearch()

elif action == 'deletesearchhistory':
    navigator.navigator().deleteSearchHistory()

elif action == 'playdirecturl':
    navigator.navigator().playdirecturl(url)

