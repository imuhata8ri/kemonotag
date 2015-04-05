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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api.labs import taskqueue
#from google.appengine.dist import use_library
#use_library('django', '1.4')

from graph import *

charttype = "Pie"
chartrange = "30"
datas = u'ケモノ'
br = mechanize.Browser()
 
##################################################
# Browser
def browser():
  global br
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
  return br
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
        
        js_code = graphhead+str(dataarray)+graphtail+charttype+graphtail2
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
  def get(self):
    datas = MyRtagData.gql("ORDER BY pagenum, parenttag ASC")
    #datas = MyRtagData.all().order('pagenum').fetch(1000, 0)
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


class CSVHandler(webapp.RequestHandler):
  def get(self,datenumber):
    encoding = 'Shift_JIS'
    if not re.search('utf', datenumber) == None:
      encoding = 'utf_8'
    self.response.headers['Content-Type'] = "application/x-csv; charset=%s" % (encoding)
    title = '"time","tag","tagnum"'
    self.response.out.write(title + "\r\n")
    query = MyData.gql("ORDER BY tag DESC")
    for q in query:
      tm = q.time
      tg = q.tag.encode(encoding)
      tgnm = q.tagnum.encode(encoding)
      self.response.out.write('"%s","%s","%s"\r\n' % (tm, tg, tgnm))


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
    query = MyRtagData.all().order('time').fetch(1000)
    db.delete(query)

    #Find Relative tags of kemono x 5 pages
    tg = u'ケモノ'
    try:
      pixivLogin()
    except:
      pass

    for i in range(1, 6):
      tgnm = reltagparser(i,tg)
      for j in range(0, len(tgnm)):
        tg = tgnm[j]
        obj = MyRtagData(tag=tg,pagenum = int(i))
        obj.save()
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
        print 'printing k: '+k
        pgnm = self.request.get(argument_name="pagenum"+str(i))
        tgchldrn = reltagparser(1,k)
        print tgchldrn
        for l in tgchldrn:
          print 'printing l: '+l
          tgchld = l
          obj = MyRtagData(tag=tgchld, pagenum = int(pgnm),parenttag=k)
          obj.save()

'''
class RelatedTagTask(webapp.RequestHandler):
  def post(self):
    pixivLogin()
    for i in range(0, 10):
      for tg in self.request.get_all(argument_name="tag"+str(i)):
        rtags = reltagparser(1,tg)
        for rtag in rtags:
          entity = MyRtagDataVertex.get_by_key_name(rtag)
          if entity is None:
            countnum = 0
          else:
            countnum = int(entity.count)
          countnum = countnum + 1
          obj = MyRtagDataVertex(tag=rtag,count=countnum,key_name=rtag)
          obj.put()
          obj2 = MyRtagDataNodes(source=tg,target=rtag,type="directed")
          obj2.put()
          
        time.sleep(5)
'''
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
  ('/xmlrtag/',RelatedTagXML),
  ('/xmlrtag/(.*)/(.*)',RelatedTagQueryXML),
  ('/graph',Graph),
  ('/code.js', JSHandler),
  ('/reload',Reload),
  ('/reloadtask',ReloadTask),
  ('/rtag',RelatedTag),
  ('/rtagtask',RelatedTagTask),
  ('/xmlnum',XMLNum),
  ('/download/(.*).csv',CSVHandler),
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
##################################################

##################################################
def pixivLogin():
  '''Log in to Pixiv, return 0 if success'''
  print 'attempting to login'

  try:
      req = 'http://www.pixiv.net/login.php'
      br.open(req)
      time.sleep(5)
      
      br._factory.is_html = True
      print br.viewing_html()
      if not br.viewing_html() == True:
        print 'viewing_html() returned invalid response', br.viewing_html()
        return
      try:
        form = br.select_form(nr=1)
      except:
        return
      try:
        br['pixiv_id'] = 'kemono-research'
        pass
      except:
        return
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
      raise
##################################################

##################################################
#Enter query and returns tag number
def parser (tag):
    br = browser()
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
    br = browser()
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
  br = browser()
  first_block = None
  rtaglist = []
  pageurl = "http://www.pixiv.net/search.php?" + \
            urllib.urlencode( 
              {"s_mode":"s_tag",
               "p": page,
               "word":tag.encode("utf8"),
               "r18":"1"} 
            )

  #Switch to online scraping
  page = br.open(pageurl)
  print pageurl
  print 'tag url opened!'
  readpage = page.read()
  soup = BeautifulSoup(readpage)
  first_block = soup.find('dl', {'class':'column-related inline-list'})
  
  #Scrape Tag number with BeautifulSoup

  for tag in first_block.findAll('a', {'class':'text'}):
    relatedtag = str(tag.string)
    rtaglist.append(relatedtag)
  return rtaglist

##################################################
    
def main():

