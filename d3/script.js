var width = 1024,
height = 768

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var color = d3.scale.category20();

var force = d3.layout.force()
    .gravity(.1)
//    .distance(200)
    .charge(-750)
    .size([width, height]);


d3.json("/json", function(error, json) {

    force
    .nodes(json.nodes)
    .links(json.links)
    .start();

    var link = svg.selectAll(".link")
    .data(json.links)
    .enter().append("line")
    .attr("class", "link");

    var node = svg.selectAll(".node")
    .data(json.nodes)
    .enter().append("g")
    .attr("class", "node")
    .call(force.drag);


    var circle = svg.append("g").selectAll("circle")
    .data(force.nodes())
    .enter().append("circle")
    .attr("r", 6)
    .call(force.drag);

    node.append("circle")
    .style("fill", function(d) { return color(d.group); })
    .attr("r",  function(d) { return d.betweenness * 2; })
    .attr("class", "node")
    .call(force.drag);

    node.append("text")
    .attr("dx", 14)
    .attr("dy", ".35em")
    .text(function(d) { return d.id });

    function tick(e) {
	// Push different nodes in different directions for clustering.
	var k = 6 * e.alpha;
	graph.nodes.forEach(function(o, i) {
	    o.y += i & 1 ? k : -k;
	    o.x += i & 2 ? k : -k;
	});
	node.attr("cx", function(d) { return d.x; })
	    .attr("cy", function(d) { return d.y; });
	
    }


    force.on("tick", function() {
	link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

	node
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });
});

