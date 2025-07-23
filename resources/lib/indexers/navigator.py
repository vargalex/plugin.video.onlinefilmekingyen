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
import os,sys,re,xbmc,xbmcgui,xbmcplugin, time, locale, json
import resolveurl
from resources.lib.modules import client, control
from resources.lib.modules.utils import py2_encode, py2_decode, safeopen
from base64 import b64decode

if sys.version_info[0] == 3:
    import urllib.parse as urlparse
    from urllib.parse import quote_plus
else:
    import urlparse
    from urllib import quote_plus

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = control.addonInfo('fanart')

base_url = control.setting("onlinefilmekingyen_base")
dooplayer_url = base_url + "wp-json/dooplayer/v2/%s/%s/%s"
deleteFromPlot = "Online film ,Online mozi "

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            pass
        self.base_path = py2_decode(control.transPath(control.addonInfo('profile')))
        self.searchFileName = os.path.join(self.base_path, "search.history")
        self.downloadSubtitles = control.setting("downloadsubtitles")

    def getRoot(self):
        self.addDirectoryItem('Keresés', 'search', '', 'DefaultFolder.png')
        self.addDirectoryItem('Filmek', 'movies&url=%s%s&page=1' % (base_url, 'movies/'), '', 'DefaultFolder.png')
        self.addDirectoryItem('Sorozatok', 'movies&url=%s%s&page=1' % (base_url, 'tvshows/'), '', 'DefaultFolder.png')
        self.addDirectoryItem('Műfajok', 'submenu&url=genres', '', 'DefaultFolder.png')
        self.addDirectoryItem('Minőség', 'submenu&url=sub-menu', '', 'DefaultFolder.png')
        self.addDirectoryItem('Megjelenés éve', 'submenu&url=releases', '', 'DefaultFolder.png')
        self.endDirectory()
    
    def getSubMenuItems(self, ulclass):
        url_content=client.request(base_url)
        li = client.parseDOM(url_content, 'ul', attrs={'class': '%s.*?' % ulclass})[0]
        lis = client.parseDOM(li, 'li')
        for li in lis:
            caption = client.replaceHTMLCodes(client.parseDOM(li, 'a')[0])
            url = client.parseDOM(li, 'a', ret='href')[0]
            if not url.startswith("http"):
                url = "%s%s" % (base_url, url)
            self.addDirectoryItem(caption, 'movies&url=%s&page=1' % url, '', 'DefaultFolder.png')
        self.endDirectory()

    def getGenreMovies(self, url_content, url, page):
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content right.*?'})[0]
        items = client.parseDOM(content, 'div', attrs={'class': '[^"]*?items full'})[0]
        articles = client.parseDOM(items, 'article', attrs={'class': 'item.*?'})
        for article in articles:
            poster = client.parseDOM(article, 'div', attrs={'class': 'poster'})[0]
            thumb = client.parseDOM(poster, 'img', ret='data-src')[0]
            data = client.parseDOM(article, 'div', attrs={'class': 'data'})[0]
            h3 = client.parseDOM(data, 'h3')
            movieurl = client.parseDOM(h3, 'a', ret='href')[0]
            title = client.replaceHTMLCodes(client.parseDOM(h3, 'a')[0])
            datum = client.parseDOM(data, 'span')[0]
            try:
                quality = client.parseDOM(poster, 'span', attrs={'class': 'quality'})[0]
            except:
                quality = ""
            #info = client.parseDOM(article, 'div')[2]
            #info = client.parseDOM(article, 'div', attrs={'class': 'animation-1 dtinfo'})[0]
            #title = client.parseDOM(info, 'div',attrs={'class': 'title'})[0]
            #title = py2_encode(client.replaceHTMLCodes(client.parseDOM(title, 'h4')[0]))
            #meta = client.parseDOM(info, 'div', attrs={'class': 'metadata'})[0]
            #year = py2_encode(client.parseDOM(meta, 'span')[0])
            #duration = "0"
            #matches = re.search(r'^(.*)<span>([0-9]*) min</span>(.*)$', meta, re.S)
            #if matches != None:
            #    duration = matches.group(2)
            #plot = py2_encode(client.parseDOM(info, 'div', attrs={'class': 'texto'})[0])
            #self.addDirectoryItem('%s (%s)' % (title, year), 'movie&url=%s' % quote_plus(movieurl), thumb, 'DefaultMovies.png', meta={'title': title, 'duration': int(duration)*60, 'fanart': thumb, 'plot': plot})
            self.addDirectoryItem('%s (%s) [COLOR yellow]%s[/COLOR]' % (title, datum, quality), 'movie&url=%s' % quote_plus(movieurl), thumb, 'DefaultMovies.npg', meta={'title': title, 'fanart': thumb}) 
        try:
            pagination = client.parseDOM(content, 'div', attrs={'class': 'pagination'})[0]
            span = client.parseDOM(pagination, 'span')[0]
            matches = re.search(r'^Oldal ([0-9]*) / ([0-9]*)$', span, re.S)
            if matches != None:
                if int(matches.group(2))>int(page):
                    self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal (%d/%s)  >>[/I]' % (int(page)+1, matches.group(2)), "movies&url=%s&page=%d" % (url, int(page)+1), '', 'DefaultFolder.png')
        except:
            pass
        self.endDirectory('movies')

    def getQualityMovies(self, url_content, url, page):
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content right full'})
        slider = client.parseDOM(content, 'div', attrs={'class': 'slider full'})[0]
        articles = client.parseDOM(slider, 'article', attrs={'class': 'item'})
        for article in articles:
            image = client.parseDOM(article, 'div', attrs={'class': 'image'})[0]
            href = client.parseDOM(image, 'a')[0]
            thumb = client.parseDOM(href, 'img', ret='data-src')[0]
            movieurl = client.parseDOM(image, 'a', ret='href')[0]
            data = client.parseDOM(article, 'div', attrs={'class': 'data'})[0]
            title = client.replaceHTMLCodes(client.parseDOM(data, 'h3', attrs={'class': 'title'})[0])
            year = client.parseDOM(data, 'span')[0]
            self.addDirectoryItem('%s (%s)' % (title, year), 'movie&url=%s' % quote_plus(movieurl), thumb, 'DefaultMovies.png', meta={'title': title, 'fanart': thumb})
        try:
            pagination = client.parseDOM(content, 'div', attrs={'class': 'pagination'})[0]
            span = client.parseDOM(pagination, 'span')[0]
            matches = re.search(r'^Oldal ([0-9]*) / ([0-9]*)$', span, re.S)
            if matches != None:
                if int(matches.group(2))>int(page):
                    self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal (%d/%s)  >>[/I]' % (int(page)+1, matches.group(2)), "movies&url=%s&page=%d" % (url, int(page)+1), '', 'DefaultFolder.png')
        except:
            pass
        self.endDirectory('movies')

    def getMovies(self, url, page):
        url_content = client.request("%spage/%s/" % (url, page))
        if '/quality/' in url:
            self.getQualityMovies(url_content, url, page)
        else:
            self.getGenreMovies(url_content, url, page)

    def getSearches(self):
        self.addDirectoryItem('Új keresés', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = open(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                self.addDirectoryItem(item, 'historysearch&search=%s&page=1' % (quote_plus(item)), '', 'DefaultFolder.png')
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
        url_content = client.request("%spage/%s/?s=%s" % (base_url, page, quote_plus(search_text)))
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content rigth csearch'})[0]
        searchpage = client.parseDOM(url_content, 'div', attrs={'class': 'search-page'})[0]
        results = client.parseDOM(searchpage, 'div', attrs={'class': 'result-item'})
        for result in results:
            image = client.parseDOM(result, 'div', attrs={'class': 'image'})
            thumb = client.parseDOM(image, 'img', ret='data-src')[0]
            details = client.parseDOM(result, 'div', attrs={'class': 'details'})[0]
            titlediv = client.parseDOM(details, 'div', attrs={'class': 'title'})[0]
            movieurl = client.parseDOM(titlediv, 'a', ret='href')[0]
            title = py2_encode(client.replaceHTMLCodes(client.parseDOM(titlediv, 'a')[0]))
            meta = client.parseDOM(details, 'div', attrs={'class': 'meta'})[0]
            year = py2_encode(client.parseDOM(meta, 'span', attrs={'class': 'year'})[0])
            contenido = client.parseDOM(details, 'div', attrs={'class': 'contenido'})
            plot = py2_encode(client.parseDOM(contenido, 'p')[0]).replace(deleteFromPlot, "")
            plot = client.replaceHTMLCodes(plot.split("<")[0])
            sorozatStr = ""
            if "tvshows" in movieurl:
                sorozatStr = "[COLOR yellow] - sorozat[/COLOR]"
            self.addDirectoryItem('%s (%s)%s' % (title, year, sorozatStr), 'movie&url=%s' % quote_plus(movieurl), thumb, 'DefaultMovies.png', meta={'title': title, 'fanart': thumb, 'plot': plot})
        try:
            pagination = client.parseDOM(content, 'div', attrs={'class': 'pagination'})[0]
            span = client.parseDOM(pagination, 'span')[0]
            matches = re.search(r'^Oldal ([0-9]*) / ([0-9]*)$', span, re.S)
            if matches != None:
                if int(matches.group(2))>int(page):
                    self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal (%d/%s)  >>[/I]' % (int(page)+1, matches.group(2)), "historysearch&search=%s&page=%d" % (search_text, int(page)+1), '', 'DefaultFolder.png')
        except:
            pass
        self.endDirectory('movies')

    def getSources(self, url, season):
        url_content = client.request(url)
        content = client.parseDOM(url_content, 'div', attrs={'class': 'content right'})[0]
        sheader = client.parseDOM(content, 'div', attrs={'class': 'sheader'})[0]
        poster = client.parseDOM(sheader, 'div', attrs={'class': 'poster'})[0]
        thumb = client.parseDOM(poster, 'img', ret='data-src')[0]
        data = client.parseDOM(sheader, 'div', attrs={'class': 'data'})[0]
        title = py2_encode(client.parseDOM(data, 'h1')[0])
        extra = client.parseDOM(data, 'div', attrs={'class': 'extra'})[0]
        date = client.parseDOM(extra, 'span', attrs={'class': 'date'})[0]
        try:
            runtime = client.parseDOM(extra, 'span', attrs={'class': 'runtime'})[0]
        except:
            runtime = ""
        matches = re.search(r'^(.*), ([0-9]*)$', date, re.S)
        year = ""
        if matches != None:
            year = matches.group(2)
        matches = re.search(r'^([0-9]*) (.*)$', runtime, re.S)
        duration = 0
        if matches != None:
            duration = int(matches.group(1))*60
        try:            
            info = client.parseDOM(content, 'div', attrs={'id': 'info'})[0]
            description = client.parseDOM(info, 'div', attrs={'class': 'wp-content'})[0]
            em = client.parseDOM(description, 'em')
            if len(em) > 0:
                description = em[0]
            plot=py2_encode(client.replaceHTMLCodes(description)).replace(deleteFromPlot, "")
            plot = client.replaceHTMLCodes(plot.split("<")[0])
            #matches = re.search(r'^(.*?)<div.*$', plot, re.S)
            #if matches:
                #plot = matches.group(1)
        except:
            plot=""
        if not "tvshow" in url:
            playeroptions = client.parseDOM(content, 'ul', attrs={'id': 'playeroptionsul'})[0]
            lis = client.parseDOM(playeroptions, 'li')
            sourceCnt = 0
            for li in lis:
                sourceCnt+=1
                type = client.parseDOM(playeroptions, 'li', ret='data-type')[sourceCnt-1]
                post = client.parseDOM(playeroptions, 'li', ret='data-post')[sourceCnt-1]
                nume = client.parseDOM(playeroptions, 'li', ret='data-nume')[sourceCnt-1]
                quality = py2_encode(client.parseDOM(li, 'span', attrs={'class': 'title'})[0])
                server = py2_encode(client.parseDOM(li, 'span', attrs={'class': 'server'})[0])
                self.addDirectoryItem('%s | %s | [B]%s[/B]' % (format(sourceCnt, '02'), quality, server), 'playmovie&type=%s&post=%s&nume=%s' % (quote_plus(type), quote_plus(post), quote_plus(nume)), thumb, 'DefaultMovies.png', isFolder=False, meta={'title': title, 'plot': plot, 'duration': int(duration)})
            try:
                linkstable = client.parseDOM(content, 'div', attrs={'class': 'links_table'})[0]
                tbody = client.parseDOM(linkstable, 'tbody')[0]
                trs = client.parseDOM(tbody, 'tr')
                for tr in trs:
                    sourceCnt+=1
                    td0 = client.parseDOM(tr, 'td')[0]
                    server = urlparse.parse_qs(urlparse.urlparse(client.parseDOM(td0, 'img', ret='src')[0]).query)['domain'][0]
                    quality = py2_encode(client.parseDOM(tr, 'strong', attrs={'class': 'quality'})[0])
                    url = client.parseDOM(td0, 'a', ret='href')[0]
                    lang = "[COLOR yellow]%s[/COLOR]" % client.parseDOM(tr, 'td')[2]
                    self.addDirectoryItem('%s | %s | [B]%s[/B] %s' % (format(sourceCnt, '02'), quality, server, lang), 'playtablemovie&url=%s' % url, thumb, 'DefaultMovies.png', isFolder=False, meta={'title': title, 'plot': plot, 'duration': int(duration)})
            except:
                pass
        else:
            try:
                seasons = json.loads(re.findall(r"const seasons = ([^;]*);", content)[0])
                if season == None:
                    for season in seasons:
                        episodeCnt = 0
                        if "episodes" in seasons[season]:
                            episodeCnt = len(seasons[season]["episodes"])
                        else:
                            episodeCnt = len(seasons[season])
                        self.addDirectoryItem("%s. évad (%d epizód)" % (py2_encode(season), episodeCnt), 'movie&url=%s&season=%s' % (quote_plus(url), season), thumb, 'DefaultMovies.png', meta={'title': title, 'fanart': thumb, 'plot': plot})
                else:
                    episodes = None
                    if "episodes" in seasons[season]:
                        episodes = seasons[season]["episodes"]
                    else:
                        episodes = seasons[season]
                    for episode in episodes:
                        self.addDirectoryItem("%s. évad %s. epizód" % (py2_encode(season), py2_encode(episode)), 'playdirecturl&url=%s' % episodes[episode], thumb, 'DefaultMovies.png', isFolder=False, meta={'title': title, 'fanart': thumb, 'plot': plot})
            except:
                pass
        self.endDirectory('movies')

    def resolveURL(self, url):
        xbmc.log('onlinefilmekingyen: resolving url: %s' % url, xbmc.LOGINFO)
        hmf = resolveurl.HostedMediaFile(url, subs=self.downloadSubtitles)
        subtitles = None
        if hmf:
            resp = hmf.resolve()
            if self.downloadSubtitles:
                direct_url = resp.get("url")
            else:
                direct_url = resp
            xbmc.log('OnlineFilmekIngyen: ResolveURL resolved URL: %s' % direct_url, xbmc.LOGINFO)
            direct_url = py2_encode(direct_url)
            if self.downloadSubtitles:
                subtitles = resp.get('subs')
            play_item = xbmcgui.ListItem(path=direct_url)
            if self.downloadSubtitles:
                if subtitles:
                    errMsg = ""
                    try:
                        if not os.path.exists("%s/subtitles" % self.base_path):
                            errMsg = "Hiba a felirat könyvtár létrehozásakor!"
                            os.mkdir("%s/subtitles" % self.base_path)
                        for f in os.listdir("%s/subtitles" % self.base_path):
                            errMsg = "Hiba a korábbi feliratok törlésekor!"
                            os.remove("%s/subtitles/%s" % (self.base_path, f))
                        finalsubtitles=[]
                        errMsg = "Hiba a felirat letöltésekor!"
                        for sub in subtitles:
                            subtitle = client.request(subtitles[sub])
                            errMsg = "%s (%s)" % (errMsg, subtitles[sub])
                            if len(subtitle) > 0:
                                errMsg = "Hiba a felirat file kiírásakor!"
                                file = safeopen(os.path.join(self.base_path, "subtitles", "%s.srt" % sub.strip()), "w")
                                file.write(subtitle)
                                file.close()
                                errMsg = "Hiba a felirat file hozzáadásakor!"
                                finalsubtitles.append(os.path.join(self.base_path, "subtitles", "%s.srt" % sub.strip()))
                            else:
                                xbmc.log("FilmPapa: Subtitles not found in source", xbmc.LOGINFO)
                        if len(finalsubtitles)>0:
                            errMsg = "Hiba a feliratok beállításakor!"
                            play_item.setSubtitles(finalsubtitles)
                    except:
                        xbmcgui.Dialog().notification("OnlineFilmekIngyen hiba", errMsg, xbmcgui.NOTIFICATION_ERROR)
                        xbmc.log("Hiba a %s URL-hez tartozó felirat letöltésekor, hiba: %s" % (py2_encode(url), py2_encode(errMsg)), xbmc.LOGERROR)
                else:
                    xbmc.log("OnlineFilmekIngyen: ResolveURL did not find any subtitles", xbmc.LOGINFO)
            xbmc.log('OnlineFilmekIngyen: playing URL: %s' % direct_url, xbmc.LOGINFO)
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def playmovie(self, mtype, post, nume):
        url_content = client.request(dooplayer_url % (post, mtype, nume))
        data = json.loads(url_content)
        if "type" in data:
            if data["type"] == "dtshcode":
                url = client.parseDOM(data["embed_url"], 'iframe', ret='src')[0]
            else:
                url = data["embed_url"]
        else:
            url = data["embed_url"]
        if 'youtube' in url:
            u = urlparse.urlparse(url)
            url = "%s://%s%s" % (u.scheme, u.netloc, u.path)
        #url = client.parseDOM(url_content, 'iframe', ret='src')[0]
        self.resolveURL(url)

    def playdirecturl(self, url):
        url = b64decode(url).decode('utf-8')
        self.resolveURL(url)

    def playTableMovie(self, url):
        url_content = client.request(url)
        src = client.parseDOM(url_content, 'a', attrs={'id': 'link'}, ret='href')[0]
        self.resolveURL(src)

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        if thumb == '': thumb = icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((py2_encode(context[0]), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
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
