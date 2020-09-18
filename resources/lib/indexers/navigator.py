# -*- coding: utf-8 -*-

'''
    dmdamedia Addon
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


import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon,urllib,urlparse,base64,time, locale, json
#import resolveurl as urlresolver
import urlresolver
from resources.lib.modules import client

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

base_url = 'aHR0cHM6Ly93d3cub25saW5lZmlsbWVraW5neWVuLmNvbS8='.decode('base64')
ajax_url = base_url + "d3AtYWRtaW4vYWRtaW4tYWpheC5waHA=".decode('base64')

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass
        self.base_path = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
        self.searchFileName = os.path.join(self.base_path, "search.history")

    def getRoot(self):
        self.addDirectoryItem('Keresés', 'search', '', 'DefaultFolder.png')
        self.addDirectoryItem('Műfajok', 'submenu&url=1989', '', 'DefaultFolder.png')
        self.addDirectoryItem('Minőség', 'submenu&url=2302', '', 'DefaultFolder.png')
        self.endDirectory()
    
    def getSubMenuItems(self, id):
        url_content=client.request(base_url)
        li = client.parseDOM(url_content, 'li', attrs={'id': 'menu-item-%s' % id})[0]
        lis = client.parseDOM(li, 'li')
        for li in lis:
            caption = client.parseDOM(li, 'a')[0]
            url = client.parseDOM(li, 'a', ret='href')[0]
            self.addDirectoryItem(caption, 'movies&url=%s&page=1' % url, '', 'DefaultFolder.png')
        self.endDirectory()

    def getGenreMovies(self, url_content, url, page):
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content'})
        items = client.parseDOM(content, 'div', attrs={'class': 'items'})[0]
        articles = client.parseDOM(items, 'article', attrs={'class': 'item movies'})
        for article in articles:
            poster = client.parseDOM(article, 'div', attrs={'class': 'poster'})[0]
            thumb = client.parseDOM(poster, 'img', ret='src')[0]
            data = client.parseDOM(article, 'div', attrs={'class': 'data'})[0]
            h3 = client.parseDOM(data, 'h3')
            movieurl = client.parseDOM(h3, 'a', ret='href')[0]
            info = client.parseDOM(article, 'div')[2]
            info = client.parseDOM(article, 'div', attrs={'class': 'animation-1 dtinfo'})[0]
            title = client.parseDOM(info, 'div',attrs={'class': 'title'})[0]
            title = client.replaceHTMLCodes(client.parseDOM(title, 'h4')[0]).encode('utf-8')
            meta = client.parseDOM(info, 'div', attrs={'class': 'metadata'})[0]
            year = client.parseDOM(meta, 'span')[0].encode('utf-8')
            duration = "0"
            matches = re.search(r'^(.*)<span>([0-9]*) min</span>(.*)$', meta, re.S)
            if matches != None:
                duration = matches.group(2)
            plot = client.parseDOM(info, 'div', attrs={'class': 'texto'})[0].encode('utf-8')
            self.addDirectoryItem('%s (%s)' % (title, year), 'movie&url=%s' % urllib.quote_plus(movieurl), thumb, 'DefaultMovies.png', meta={'title': title, 'duration': int(duration)*60, 'fanart': thumb, 'plot': plot})
        try:
            pagination = client.parseDOM(content, 'div', attrs={'class': 'pagination'})[0]
            span = client.parseDOM(pagination, 'span')[0]
            matches = re.search(r'^Page ([0-9]*) of ([0-9]*)$', span, re.S)
            if matches != None:
                if int(matches.group(2))>int(page):
                    self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal (%d/%s)  >>[/I]' % (int(page)+1, matches.group(2)), "movies&url=%s&page=%d" % (url, int(page)+1), '', 'DefaultFolder.png')
        finally:
            pass
        self.endDirectory('movies')

    def getQualityMovies(self, url_content, url, page):
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content'})
        slider = client.parseDOM(content, 'div', attrs={'class': 'slider'})[0]
        articles = client.parseDOM(slider, 'article', attrs={'class': 'item'})
        for article in articles:
            image = client.parseDOM(article, 'div', attrs={'class': 'image'})[0]
            href = client.parseDOM(image, 'a')[0]
            thumb = client.parseDOM(href, 'img', ret='src')[0]
            movieurl = client.parseDOM(image, 'a', ret='href')[0]
            data = client.parseDOM(article, 'div', attrs={'class': 'data'})[0]
            title = client.replaceHTMLCodes(client.parseDOM(data, 'h3', attrs={'class': 'title'})[0])
            year = client.parseDOM(data, 'span')[0]
            self.addDirectoryItem('%s (%s)' % (title, year), 'movie&url=%s' % urllib.quote_plus(movieurl), thumb, 'DefaultMovies.png', meta={'title': title, 'fanart': thumb})
        try:
            pagination = client.parseDOM(content, 'div', attrs={'class': 'pagination'})[0]
            span = client.parseDOM(pagination, 'span')[0]
            matches = re.search(r'^Page ([0-9]*) of ([0-9]*)$', span, re.S)
            if matches != None:
                if int(matches.group(2))>int(page):
                    self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal (%d/%s)  >>[/I]' % (int(page)+1, matches.group(2)), "movies&url=%s&page=%d" % (url, int(page)+1), '', 'DefaultFolder.png')
        finally:
            pass
        self.endDirectory('movies')

    def getMovies(self, url, page):
        url_content = client.request("%spage/%s/" % (url, page))
        if '/tag/' in url or '/genre/' in url:
            self.getGenreMovies(url_content, url, page)
        else:
            self.getQualityMovies(url_content, url, page)

    def getSearches(self):
        self.addDirectoryItem('Új keresés', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            items = file.read().splitlines()
            items.sort(cmp=locale.strcoll)
            file.close()
            for item in items:
                self.addDirectoryItem(item, 'historysearch&search=%s&page=1' % (urllib.quote_plus(item)), '', 'DefaultFolder.png')
            if len(items) > 0:
                self.addDirectoryItem('Keresési előzmények törlése', 'deletesearchhistory', '', 'DefaultFolder.png') 
        except:
            pass   
        self.endDirectory()

    def deleteSearchHistory(self):
        if os.path.exists(self.searchFileName):
            os.remove(self.searchFileName)

    def doSearch(self):
        search_text = self.getText(u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            file = open(self.searchFileName, "a")
            file.write("%s\n" % search_text)
            file.close()
            self.getResults(search_text, 1)

    def getResults(self, search_text, page):
        url_content = client.request("%spage/%s/?s=%s" % (base_url, page, search_text))
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content csearch'})[0]
        searchpage = client.parseDOM(url_content, 'div', attrs={'class': 'search-page'})[0]
        results = client.parseDOM(searchpage, 'div', attrs={'class': 'result-item'})
        for result in results:
            image = client.parseDOM(result, 'div', attrs={'class': 'image'})
            thumb = client.parseDOM(image, 'img', ret='src')[0]
            details = client.parseDOM(result, 'div', attrs={'class': 'details'})[0]
            titlediv = client.parseDOM(details, 'div', attrs={'class': 'title'})[0]
            movieurl = client.parseDOM(titlediv, 'a', ret='href')[0]
            title = client.replaceHTMLCodes(client.parseDOM(titlediv, 'a')[0]).encode('utf-8')
            meta = client.parseDOM(details, 'div', attrs={'class': 'meta'})[0]
            year = client.parseDOM(meta, 'span', attrs={'class': 'year'})[0].encode('utf-8')
            contenido = client.parseDOM(details, 'div', attrs={'class': 'contenido'})
            plot = client.parseDOM(contenido, 'p')[0].encode('utf-8')
            self.addDirectoryItem('%s (%s)' % (title, year), 'movie&url=%s' % urllib.quote_plus(movieurl), thumb, 'DefaultMovies.png', meta={'title': title, 'fanart': thumb, 'plot': plot})
        try:
            pagination = client.parseDOM(content, 'div', attrs={'class': 'pagination'})[0]
            span = client.parseDOM(pagination, 'span')[0]
            matches = re.search(r'^Page ([0-9]*) of ([0-9]*)$', span, re.S)
            if matches != None:
                if int(matches.group(2))>int(page):
                    self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal (%d/%s)  >>[/I]' % (int(page)+1, matches.group(2)), "historysearch&search=%s&page=%d" % (search_text, int(page)+1), '', 'DefaultFolder.png')
        finally:
            pass
        self.endDirectory('movies')

    def getSources(self, url):
        url_content = client.request(url)
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content'})[0]
        sheader = client.parseDOM(content, 'div', attrs={'class': 'sheader'})[0]
        poster = client.parseDOM(sheader, 'div', attrs={'class': 'poster'})[0]
        thumb = client.parseDOM(poster, 'img', ret='src')[0]
        data = client.parseDOM(sheader, 'div', attrs={'class': 'data'})[0]
        title = client.parseDOM(data, 'h1')[0].encode('utf-8')
        extra = client.parseDOM(data, 'div', attrs={'class': 'extra'})[0]
        date = client.parseDOM(extra, 'span', attrs={'class': 'date'})[0]
        runtime = client.parseDOM(extra, 'span', attrs={'class': 'runtime'})[0]
        matches = re.search(r'^(.*), ([0-9]*)$', date, re.S)
        year = ""
        if matches != None:
            year = matches.group(2)
        matches = re.search(r'^([0-9]*) (.*)$', runtime, re.S)
        duration = 0
        if matches != None:
            duration = int(matches.group(1))*60
        info = client.parseDOM(content, 'div', attrs={'id': 'info'})[0]
        description = client.parseDOM(info, 'div', attrs={'itemprop': 'description'})[0]
        plot=client.parseDOM(description, 'p')[0].encode('utf-8')

        playeroptions = client.parseDOM(content, 'ul', attrs={'id': 'playeroptionsul'})[0]
        lis = client.parseDOM(playeroptions, 'li')
        sourceCnt = 0
        for li in lis:
            sourceCnt+=1
            type = client.parseDOM(playeroptions, 'li', ret='data-type')[sourceCnt-1]
            post = client.parseDOM(playeroptions, 'li', ret='data-post')[sourceCnt-1]
            nume = client.parseDOM(playeroptions, 'li', ret='data-nume')[sourceCnt-1]
            quality = client.parseDOM(li, 'span', attrs={'class': 'title'})[0].encode('utf-8')
            server = client.parseDOM(li, 'span', attrs={'class': 'server'})[0].encode('utf-8')
            self.addDirectoryItem('%s | %s | [B]%s[/B]' % (format(sourceCnt, '02'), quality, server), 'playmovie&type=%s&post=%s&nume=%s' % (urllib.quote_plus(type), urllib.quote_plus(post), urllib.quote_plus(nume)), thumb, 'DefaultMovies.png', isFolder=False, meta={'title': title, 'plot': plot, 'duration': int(duration)*60})
        self.endDirectory('movies')

    def playmovie(self, mtype, post, nume):
        cookies = client.request(base_url, output='cookie')
        url_content = client.request(ajax_url, post="action=doo_player_ajax&post=%s&nume=%s&type=%s" % (post, nume, mtype), cookie=cookies)
        url = client.parseDOM(url_content, 'iframe', ret='src')[0]
        xbmc.log('onlinefilmekingyen: resolving url: %s' % url, xbmc.LOGNOTICE)
        try:
            direct_url = urlresolver.resolve(url)
            if direct_url:
                direct_url = direct_url.encode('utf-8')
            else:
                direct_url = url
        except Exception as e:
            xbmcgui.Dialog().notification(urlparse.urlparse(url).hostname, e.message)
            return
        if direct_url:
            xbmc.log('onlinefilmekingyen: playing URL: %s' % direct_url, xbmc.LOGNOTICE)
            play_item = xbmcgui.ListItem(path=direct_url)
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        if thumb == '': thumb = icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((context[0].encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart == None: Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if isFolder == False: item.setProperty('IsPlayable', 'true')
        if not meta == None: item.setInfo(type='Video', infoLabels = meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        #xbmcplugin.addSortMethod(syshandle, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)

    def getText(self, title, hidden=False):
        search_text = ''
        keyb = xbmc.Keyboard('', title, hidden)
        keyb.doModal()

        if (keyb.isConfirmed()):
            search_text = keyb.getText()

        return search_text
