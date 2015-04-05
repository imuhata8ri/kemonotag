charttype = ""

graphhead = """
      google.load('visualization', '1.0', {'packages':['corechart']});
      google.setOnLoadCallback(drawChart);

      function drawChart() {
        var data = new google.visualization.arrayToDataTable([
          ['Tag', 'Tag Number'],
"""
graphtail = """
        ]);
        var options = {'title':'Pixiv Tag Data',
                       'width':800,
                       'height':600};
        var chart = new google.visualization."""

graphtail2 = """Chart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }"""
