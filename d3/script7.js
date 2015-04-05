var width = 1024,
height = 768

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var color = d3.scale.category20();

data = d3.json("/graphdata", function(error, json) {
    var link = svg.selectAll(".link")
	.data(json.links)
	.enter().append("line")
	.attr("class", "link");

    var node = svg.selectAll(".node")
	.data(json.nodes)
	.enter().append("g")
	.attr("class", "node")
	.call(force.drag)
};


function tick(e) {
    circle
	.each(cluster(10 * e.alpha * e.alpha))
	    .each(collide(.5))
		.attr("cx", function(d) { return d.x; })
	.attr("cy", function(d) { return d.y; });
}
var mouseOverFunction = function(d) {
  var circle = d3.select(this);

  node
    .transition(500)
      .style("opacity", function(o) {
        return isConnected(o, d) ? 1.0 : 0.2 ;
      })
      .style("fill", function(o) {
        if (isConnectedAsTarget(o, d) && isConnectedAsSource(o, d) ) {
          fillcolor = 'green';
        } else if (isConnectedAsSource(o, d)) {
          fillcolor = 'red';
        } else if (isConnectedAsTarget(o, d)) {
          fillcolor = 'blue';
        } else if (isEqual(o, d)) {
          fillcolor = "hotpink";
        } else {
          fillcolor = '#000';
        }
        return fillcolor;
      });

  link
    .transition(500)
      .style("stroke-opacity", function(o) {
        return o.source === d || o.target === d ? 1 : 0.2;
      })
      .transition(500)
      .attr("marker-end", function(o) {
        return o.source === d || o.target === d ? "url(#arrowhead)" : "url()";
      });

  circle
    .transition(500)
      .attr("r", function(){ return 1.4 * node_radius(d)});
}

var mouseOutFunction = function() {
  var circle = d3.select(this);

  node
    .transition(500);

  link
    .transition(500);

  circle
    .transition(500)
      .attr("r", node_radius);
}

function isConnected(a, b) {
    return isConnectedAsTarget(a, b) || isConnectedAsSource(a, b) || a.index == b.index;
}

function isConnectedAsSource(a, b) {
    return linkedByIndex[a.index + "," + b.index];
}

function isConnectedAsTarget(a, b) {
    return linkedByIndex[b.index + "," + a.index];
}

function isEqual(a, b) {
    return a.index == b.index;
}

function tick() {
  link
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

  node
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
}

function node_radius(d) { return Math.pow(40.0 * d.size, 1/3); }

var width = 1000;
var height = 500;

var nodes = data.nodes
var links = data.links

var force = d3.layout.force()
              .nodes(nodes)
              .links(links)
              .charge(-3000)
              .friction(0.6)
              .gravity(0.6)
              .size([width,height])
              .start();

var linkedByIndex = {};
links.forEach(function(d) {
  linkedByIndex[d.source.index + "," + d.target.index] = true;
});

var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

var link = svg.selectAll("line")
              .data(links)
            .enter().append("line")

var node = svg.selectAll(".node")
              .data(nodes)
            .enter().append("g")
              .attr("class", "node")
              .call(force.drag);

node
  .append("circle")
  .attr("r", node_radius)
  .on("mouseover", mouseOverFunction)
  .on("mouseout", mouseOutFunction);

svg
  .append("marker")
  .attr("id", "arrowhead")
  .attr("refX", 6 + 7) // Controls the shift of the arrow head along the path
  .attr("refY", 2)
  .attr("markerWidth", 6)
  .attr("markerHeight", 4)
  .attr("orient", "auto")
  .append("path")
    .attr("d", "M 0,0 V 4 L6,2 Z");

link
  .attr("marker-end", "url()");

force
  .on("tick",tick);
