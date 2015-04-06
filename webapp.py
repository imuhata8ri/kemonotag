# coding: utf-8
import sys
import os
stdin = sys.stdin
stdout = sys.stdout
sys.path.insert(0,'lib')
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout
#sys.path.append(os.pardir)
sys.path.append(os.pardir + '/lib/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


import mechanize
from BeautifulSoup3.BeautifulSoup import BeautifulSoup as BeautifulSoup
import lxml

import logging
import logging.handlers
import cookielib
import urllib, urllib2

import traceback
import time
import csv
import re
import datetime
import wsgiref.handlers
import string
import datetime


import webapp2

from google.appengine.api import datastore
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import memcache
#from google.appengine.dist import use_library
#use_library('django', '1.4')

from graph import *

import network
#import network

charttype = "Pie"
chartrange = "30"
datas = u'ケモノ'
 
##################################################
# Browser
br = mechanize.Browser()
# Browser options
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Cookie
#cj = mechanize.LWPCookieJar()
#try: # Load cookie if there is any
  #cj.load(cookie_file)
#except:
    #pass
#cj = cookielib.CookieJar()
#br.set_cookiejar(cj)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2')]
##################################################

##################################################
class MainHTML(webapp.RequestHandler):
  def get(self):
    datas = MyData.all().order('-time').fetch(1000, 0)
    params = {'datas':datas,}
    fpath = os.path.join(os.path.dirname(__file__),'views','home.html')
    html = template.render(fpath,params)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(html)
  def post(self):
    tg = self.request.get('name')
    pixivLogin()
    tgnm = parser(tg)
    obj = MyData(tag=tg,tagnum=tgnm,key_name=tg)
    obj.save()
    tg = u'ケモノ'
    obj = MyRtagDataVertex(tag=tg,key_name=tg)
    obj2 = MyRtagDataNodes(tag=tg,key_name=tg)
    obj.save()
    obj2.save()
    self.redirect('/')

class GraphD3(webapp.RequestHandler):
  def get(self):
    params = {}
    fpath = os.path.join(os.path.dirname(__file__),'d3','index.html')
    html = template.render(fpath,params)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(html)
  def post(self):
    timespan = self.request.get("timespan")

class Graph(webapp.RequestHandler):
  def get(self):
    params = {}
    fpath = os.path.join(os.path.dirname(__file__),'views','graph.html')
    html = template.render(fpath,params)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(html)
  def post(self):
    global charttype, chartrange, chartnumber
    charttype = self.request.get("graphtype")
    chartrange = self.request.get("range")
    chartnumber = self.request.get("number")
    params = {
              "graphtype" : charttype,
              "range" : chartrange,
              "number": chartnumber
              }
    fpath = os.path.join(os.path.dirname(__file__),'views','graph.html')
    html = template.render(fpath,params)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(html)




class JSHandler(webapp.RequestHandler):
    def get(self):
        global chartrange,chartnumber,charttype
        arraylist = []
        if chartrange is '':
            chartrange = "tagnum"
        if chartnumber is '':
            chartnumber = int(1000)
        queries = MyData.all().order(chartrange).fetch(int(chartnumber), 0)
        for query in queries:
            tag = "'"+str(query.tag)+"'"
            tagnum = str(query.tagnum)
            array = "          ["+tag+", "+tagnum+"]"
            arraylist.append(str(array))
        dataarray = ",\n".join(arraylist)

        js_code = head+str(dataarray)+tail+charttype+tail2
        global js_code
        page= str(self.request.get("page"))
        self.response.out.write(js_code)

class MainXML(webapp.RequestHandler):
  def get(self):
    datas = MyData.all().order('tag').fetch(1000, 0)
    params = {'datas':datas,}
    xpath = os.path.join(os.path.dirname(__file__),'views','pixivtags.xml')
    xml = template.render(xpath,params)
    self.response.headers['Content-Type'] = 'application/xml'
    self.response.out.write(xml)


class RelatedTagXML(webapp.RequestHandler):
  def get(self, xmlreload):
    xml = memcache.get(key="xml")
    if xml is None or "reload" in xmlreload:
      datas = MyRtagData.gql("ORDER BY pagenum, parenttag ASC")
      params = {'datas':datas,}
      xpath = os.path.join(os.path.dirname(__file__),'views','rtag.xml')
      xml = template.render(xpath,params)
      memcache.set(key="xml", value=xml)
      logging.debug("MyRtagData has been reloaded.")
    self.response.headers['Content-Type'] = 'application/xml'
    self.response.out.write(xml)


class PixivRelatedTagXML(webapp.RequestHandler):
  def get(self):
    datas = MyPixivRtagData.gql("ORDER BY pagenum, parenttag ASC")
    params = {'datas':datas,}
    xpath = os.path.join(os.path.dirname(__file__),'views','rtag.xml')
    xml = template.render(xpath,params)
    self.response.headers['Content-Type'] = 'application/xml'
    self.response.out.write(xml)



class RelatedTagQueryXML(webapp.RequestHandler):
  def get(self,page,tag):
    pixivLogin()
    params = {'datas':reltagparser(page,tag),}
    xpath = os.path.join(os.path.dirname(__file__),'views','rtagquery.xml')
    xml = template.render(xpath,params)
    self.response.headers['Content-Type'] = 'application/xml'
    self.response.out.write(xml)


class XMLNum(webapp.RequestHandler):
  def get(self):
    datas = MyData.all().order('tagnum').fetch(100, 0)
    params = {'datas':datas,}
    xpath = os.path.join(os.path.dirname(__file__),'views','pixivtags.xml')
    xml = template.render(xpath,params)
    self.response.headers['Content-Type'] = 'application/xml'
    self.response.out.write(xml)

class RelatedTagCSV(webapp.RequestHandler):
  def get(self):
    datas = MyRtagData.gql("ORDER BY pagenum, parenttag ASC").fetch(1000)
    #datas = db.GqlQuery("SELECT * FROM MyRtagData parenttag != NULL").fetch(1000)
    #datas = MyRtagData.all().filter('parenttag !=', "None").filter('tag !=', "None").fetch(1000, 0)
    #print "Type of 'datas': ",type(datas)
    #datas = [w.replace('NULL', u'ケモノ') for w in datas]
    params = {'datas':datas,}
    encoding = 'utf_8'
    xpath = os.path.join(os.path.dirname(__file__),'views','rtag.csv')
    csvdata = template.render(xpath,params)
    self.response.headers['Content-Type'] = "application/x-csv; charset=%s" % (encoding)
    self.response.out.write(csvdata)
    obj = CsvData(csv=csvdata)
    obj.put()

class PixivRelatedTagCSV(webapp.RequestHandler):
  def get(self):
    datas = MyPixivRtagData.gql("ORDER BY pagenum, parenttag ASC").fetch(1000)
    #datas = db.GqlQuery("SELECT * FROM MyRtagData parenttag != NULL").fetch(1000)
    #datas = MyRtagData.all().filter('parenttag !=', "None").filter('tag !=', "None").fetch(1000, 0)
    #print "Type of 'datas': ",type(datas)
    #datas = [w.replace('NULL', u'ケモノ') for w in datas]
    params = {'datas':datas,}
    encoding = 'utf_8'
    xpath = os.path.join(os.path.dirname(__file__),'views','rtag.csv')
    csvdata = template.render(xpath,params)
    self.response.headers['Content-Type'] = "application/x-csv; charset=%s" % (encoding)
    self.response.out.write(csvdata)
    #obj = CsvData(csv=csvdata)
    #obj.put()

    
class CreateNetworkJson(webapp.RequestHandler):
  def get(self):
    csvdata = db.GqlQuery("SELECT * FROM CsvData ORDER BY time DESC limit 30")

    #Monthly data
    month = []
    for csventity in csvdata:
      json = csventity.csv
      if json.find(',') > 1:
        json.replace(',',u"，")
        json.replace(u"，",',',1)
      month.append(json)
    month = unicode("\n".join(month))
    jsondatamonth = network.createjson(month)
    memcache.set(key = "jsonmonth", value=jsondatamonth)
    obj = JsonDataMonth(json=jsondatamonth)
    obj.put()

    #Weekly data
    week = []
    for n in range (0, 7):
      json = csvdata[n].csv
      if json.find(',') > 1:
        json.replace(',',u"，")
        json.replace(u"，",',',1)
      week.append(json)
    week = unicode("\n".join(week))
    jsondataweek = network.createjson(week)
    memcache.set(key = "jsonweek", value=jsondataweek)
    obj = JsonDataWeek(json=jsondataweek)
    obj.put()

    #Day data
    for n in range (0, 1):
      day = csvdata[n].csv
    #for csventity in csvdata:
      #json = csventity.csv
      if day.find(',') > 1:
        day.replace(',',u"，")
        day.replace(u"，",',',1)
    jsondata = network.createjson(day)
    memcache.set(key = "json", value=jsondata)
    obj = JsonData(json=jsondata)
    obj.put()

class Script(webapp.RequestHandler):
  def get(self,timespan):
    logging.debug(timespan)
    fpath = os.path.join(os.path.dirname(__file__),"d3","script.js")
    js = template.render(fpath, timespan)
    self.response.headers['Content-Type'] = "text/javascript"
    self.response.out.write(js)
    

class RecallJson(webapp2.RequestHandler):
  def get(self,timespan):

    logging.debug(timespan)

    json = memcache.get(key="json"+timespan)
    if json is None:
      if "week" in timespan:
        jsonfile = db.GqlQuery("SELECT * FROM JsonDataWeek ORDER BY time DESC limit 1")
      elif "month" in timespan:
        jsonfile = db.GqlQuery("SELECT * FROM JsonDataMonth ORDER BY time DESC limit 1")
      elif "year" in timespan:
        jsonfile = ndb.GqlQuery("SELECT * FROM JsonDataYear ORDER BY time DESC limit 1")
      else:
        jsonfile = db.GqlQuery("SELECT * FROM JsonData ORDER BY time DESC limit 1")
      for n in jsonfile:
        json = n.json

    encoding = 'utf_8'
    self.response.headers['Content-Type'] = "application/json; charset=%s" % (encoding)
    self.response.out.write(json)


#class CSVHandler(webapp.RequestHandler):
#  def get(self,datenumber):
#    encoding = 'Shift_JIS'
#    if not re.search('utf', datenumber) == None:
#      encoding = 'utf_8'
#    self.response.headers['Content-Type'] = "application/x-csv; charset=%s" % (encoding)
#    title = '"time","tag","tagnum"'
#    self.response.out.write(title + "\r\n")
#    query = MyData.gql("ORDER BY tag DESC")
#    for q in query:
#      tm = q.time
#      tg = q.tag.encode(encoding)
#      tgnm = q.tagnum.encode(encoding)
#      self.response.out.write('"%s","%s","%s"\r\n' % (tm, tg, tgnm))


class Reload(webapp.RequestHandler):
  def get(self):
    size = 5
    datas = MyData.all().fetch(100)
    print len(datas)
    for i in range(0, len(datas), size):
      params = {}
      for j in range(0, size):
        if i+ j >= len(datas):
          break
        params["tag"+str(j)] = datas[i+j].tag
        #print datas[i+j].tag
        #print params["tag"+str(j)]
        #print '-----------------------'
      taskqueue.add(url='/reloadtask', params = params)

class ReloadTask(webapp.RequestHandler):
  def post(self):
    pixivLogin()
    for i in range(0, 5):
      for tg in self.request.get_all(argument_name="tag"+str(i)):
        print tg
        tgnm = parser(tg)
        obj = MyData(tag=tg,tagnum=tgnm,key_name=tg)
        obj.put()
        time.sleep(5)


class RelatedTag(webapp.RequestHandler):
  def get(self):
    size = 10
    obj = MyRtagData(tag=u'ケモノ',pagenum = int(0))
    obj.save()

    #Delete all tags in MyRtagData.
    query = MyRtagData.all().order('time').fetch(1500)
    db.delete(query)

    #Find Relative tags of kemono x 5 pages
    kemono='ケモノ'
    kemonotag = []
    pixivLogin()

    for i in range(1, 6):
      print i
      kemonosubtag = []
      tgnm = reltagparser(i,kemono)
      for j in range(0, len(tgnm)):
        tg = tgnm[j]
        obj = MyRtagData(tag=tg,pagenum = int(i), parenttag=kemono)
        obj.save()
        kemonosubtag.append(tg)
      kemonotag.append(kemonosubtag)
    #Request relative tags in RtagDataVertex
    datas = MyRtagData.all().fetch(100)
    for i in range(0, len(datas), size):
      params = {}
      for j in range(0, size):
        if i+ j >= len(datas):
          break
        params["tag"+str(j)] = datas[i+j].tag
        params["pagenum"+str(j)] = datas[i+j].pagenum
      taskqueue.add(url='/rtagtask', params = params)


class RelatedTagTask(webapp.RequestHandler):
  def post(self):
    #Find Relative children tags of above.
    pixivLogin()
    for i in range(0, 10):
      for k in self.request.get_all(argument_name="tag"+str(i)):
        pgnm = self.request.get(argument_name="pagenum"+str(i))
        tgchldrn = reltagparser(1,k)
        print tgchldrn
        for l in tgchldrn:
          tgchld = l
          obj = MyRtagData(tag=tgchld, pagenum = int(pgnm),parenttag=k)
          obj.save()

class PixivRelatedTag(webapp.RequestHandler):
  def get(self):
    size = 10
    obj = MyPixivRtagData(tag=u'ケモノ',pagenum = int(0), paretntag=u'ケモノ')
    obj.save()

    #Delete all tags in MyRtagData.
    query = MyPixivRtagData.all().order('time').fetch(1500)
    db.delete(query)

    #Find Relative tags of kemono x 5 pages
    kemono='ケモノ'
    kemonotag = []

    for i in range(1, 6):
      print i
      kemonosubtag = []
      tgnm = reltagparser(i,kemono)
      for j in range(0, len(tgnm)):
        tg = tgnm[j]
        obj = MyPixivRtagData(tag=tg,pagenum = int(i), parenttag=kemono)
        obj.save()
        kemonosubtag.append(tg)
      kemonotag.append(kemonosubtag)
    #Request relative tags in RtagDataVertex
    datas = MyPixivRtagData.all().fetch(100)
    for i in range(0, len(datas), size):
      params = {}
      for j in range(0, size):
        if i+ j >= len(datas):
          break
        params["tag"+str(j)] = datas[i+j].tag
        params["pagenum"+str(j)] = datas[i+j].pagenum
      taskqueue.add(url='/pixivrtagtask', params = params)


class PixivRelatedTagTask(webapp.RequestHandler):
  def post(self):
    #Find Relative children tags of above.
    for i in range(0, 10):
      for k in self.request.get_all(argument_name="tag"+str(i)):
        pgnm = self.request.get(argument_name="pagenum"+str(i))
        tgchldrn = reltagparser(1,k)
        print tgchldrn
        for l in tgchldrn:
          tgchld = l
          obj = MyPixivRtagData(tag=tgchld, pagenum = int(pgnm),parenttag=k)
          obj.save()

class DataBackup(webapp.RequestHandler):
  def get(self):
    #size = 5
    #datas = MyData.all().fetch(100)
    query = MyData.gql("ORDER BY tag DESC")
    for q in query:
      tm = q.time
      tg = q.tag
      tgnm = q.tagnum
      obj = MyEntireData(time=tm,tag=tg,tagnum=tgnm)
      obj.put()
      #taskqueue.add(url='/databackuptask', params = params)

class DataBackupTask(webapp.RequestHandler):
  def post(self):
    for i in range(0, len(datas), size):
      MyData.gql("ORDER BY tag DESC")
      for q in self:
        tm = q.time
        tg = q.tag
        tgnm = q.tagnum
        obj = MyEntireData(time=tm,tag=tg,tagnum=tgnm)
        obj.put()
    
app = webapp.WSGIApplication([
  ('/', MainHTML),
  ('/xml',MainXML),
  ('/xmlrtag(.*)',RelatedTagXML),
  ('/xmlrtag/(.*)/(.*)',RelatedTagQueryXML),
  ('/xmlrtagpixiv/',PixivRelatedTagXML),
  ('/graph',Graph),
  ('/script(.*)',Script),
  ('/code.js', JSHandler),
  ('/reload',Reload),
  ('/reloadtask',ReloadTask),
  ('/rtag',RelatedTag),
  ('/rtagtask',RelatedTagTask),
  ('/pixivrtag',PixivRelatedTag),
  ('/pixivrtagtask',PixivRelatedTagTask),
  ('/xmlnum',XMLNum),
  ('/csv',RelatedTagCSV),
  ('/csvpixiv',PixivRelatedTagCSV),
  ('/jsondata',CreateNetworkJson),
  ('/json(.*)',RecallJson),
#  ('/download/(.*).csv',CSVHandler),
  ('/databackup',DataBackup),
  ('/databackuptask',DataBackupTask)
], debug=True)

################################################## 
class MyData(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  def get_jst(self):
    return self.time + datetime.timedelta(hours=9)
  def epoc2datetime(self):
    sDt = time.gmtime(self)
    return datetime.datetime(sDt[0],sDt[1],sDt[2],sDt[3],sDt[4],sDt[5],sDt[6])
  tag = db.StringProperty(required=True,multiline=False)
  tagnum = db.IntegerProperty(required=True)

class MyEntireData(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=False)
  tag = db.StringProperty(required=True,multiline=False)
  tagnum = db.IntegerProperty(required=True)
class MyRtagData(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  tag = db.StringProperty(required=True,multiline=False)
  pagenum = db.IntegerProperty(required=True)
  parenttag = db.StringProperty(required=False,multiline=False)
class MyRtagDataVertex(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  tag = db.StringProperty(required=True,multiline=False)
  count = db.IntegerProperty(required=False)
class MyRtagDataNodes(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  source = db.StringProperty(required=True,multiline=False)
  target = db.StringProperty(required=True,multiline=False)
  type = db.StringProperty(required=True,multiline=False)
class MyPixivRtagData(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  tag = db.StringProperty(required=True,multiline=False)
  pagenum = db.IntegerProperty(required=True)
  parenttag = db.StringProperty(required=False,multiline=False)

class CsvData(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  csv = db.TextProperty()
class JsonData(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  json = db.TextProperty()
class JsonDataWeek(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  json = db.TextProperty()
class JsonDataMonth(db.Model):
  time = db.DateTimeProperty(required=True,auto_now_add=True)
  json = db.TextProperty()

##################################################

##################################################
def pixivLogin():
    '''Log in to Pixiv, return 0 if success'''
    print 'attempting to login'
    
    try:
        req = 'http://www.pixiv.net/login.php'
        br.open(req)
        
        form = br.select_form(nr=1)
        br['pixiv_id'] = 'kemono-research'
        br['pass'] = 'p3a6ragu'
        br.find_control('skip').items[0].selected = True

        response = br.submit()
        if response.geturl().find('pixiv.net/login.php') == -1:
            print 'login completed'
            #cj.save("cookie_file")
        else :
            print 'login failed'

    except:
        print 'Error at pixivLogin():',sys.exc_info()
        print 'failed'
        return
##################################################

##################################################
#Enter query and returns tag number
def parser (tag):
    pageurl = "http://www.pixiv.net/search.php?" + \
              urllib.urlencode( {"s_mode":"s_tag","word":tag.encode("utf8")} )

    #Switch to online scraping
    page = br.open(pageurl)

    print 'tag url opened!'
    readpage = page.read()
    soup = BeautifulSoup(readpage)

    #Scrape Tag number with BeautifulSoup
    for div in soup('div', {'class':'column-label'}):
        for span in div('span', {'class':'count-badge'}):
            tagnum = span.text
            tagnum = re.sub(unicode(r'件$'),'', tagnum)
            tagnum = int(tagnum)
            return tagnum

def r18parser (tag):
    pageurl = "http://www.pixiv.net/search.php?" + \
            urllib.urlencode( 
              {"s_mode":"s_tag",
               "word":tag.encode("utf8"),
               "r18":"1"} 
            )

    #Switch to online scraping
    page = br.open(pageurl)

    print 'tag url opened!'
    readpage = page.read()
    soup = BeautifulSoup(readpage)

    #Scrape Tag number with BeautifulSoup
    for div in soup('div', {'class':'column-label'}):
        for span in div('span', {'class':'count-badge'}):
            tagnum = span.text
            tagnum = re.sub(unicode(r'件$'),'', tagnum)
            tagnum = int(tagnum)
            return tagnum

def reltagparser (page,tag):
  first_block = None
  rtaglist = []
  pageurl = "http://www.pixiv.net/search.php?" + \
            urllib.urlencode( 
              {"s_mode":"s_tag_full",
               "p": page,               
               "order": "date_d",
               "word":tag.encode("utf8")
             } 
            )
  print pageurl
  page = br.open(pageurl)
  print 'tag url opened!'
  readpage = page.read()
  soup = BeautifulSoup(readpage)
  try:
    for dd in soup.findAll('dl', {'class':'column-related inline-list'}, limit=1):
      for tag in dd.findAll('a', {'class':'text'}):
        relatedtag = str(tag.string)
        relatedtag.replace(',', u'，')
        rtaglist.append(relatedtag)
      if len(rtaglist) > 8:
        rtaglist = list(set(rtaglist))
      return rtaglist
  except:
    print 'Error at pixivLogin():',sys.exc_info()
    print 'failed'
    return
  
##################################################
    
def main():
    wsgiref.handlers.CGIHandler().run(app)
    #run_wsgi_app(app)
