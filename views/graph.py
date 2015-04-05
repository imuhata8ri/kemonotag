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
sys.path.append(os.pardir + '/lib/')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api.labs import taskqueue

charttype = "Pie"

head = "      // Load the Visualization API and the piechart package.
      google.load('visualization', '1.0', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and
      // draws it.
      function drawChart() {

        // Create the data table.
        var data = new google.visualization.arrayToDataTable(["


tail =
        "]);
        // Set chart options
        var options = {'title':'Pixiv Tag Data',
                       'width':400,
                       'height':300};

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization."+charttype+"Chart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }"


class Graph(webapp.RequestHandler):
  def get(self):
    #global charttype
    arraylist = []
    queries = MyData.gql("ORDER BY tag DESC")
    for query in queries:
      tag = "'"+str(query.tag)+"'"
      tagnum = str(query.tagnum)
      array = "["+tag+", "+tagnum+"]\n"
      arraylist.append(array)
    dataarray = ",".join(map(str,array))
    js_code = head+dataarray+tail
    template_value = {
        'js_code' : js_code
    }
    fpath = os.path.join(os.path.dirname(__file__),'views','graph.html')
    html = template.render(fpath,js_code)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(html)
