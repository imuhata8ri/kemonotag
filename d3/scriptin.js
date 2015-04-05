var width = 1024,
height = 768

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var color = d3.scale.category20();

var force = d3.layout.force()
    .gravity(.1)
    .distance(200)
    .charge(-200)
    .size([width, height]);


d3.json("/graphdata", function(error, json) {


    var root = json.nodes[0];
    root.radius = 0;
    root.fixed = true;


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
	.attr("r",  function(d) { return d.betweenness * 3; })
	.attr("class", "node")
	.call(force.drag);

    node.append("text")
	.attr("dx", 12)
	.attr("dy", ".35em")
	.text(function(d) { return d.id });


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
var width = 1024,
height = 768

var color = d3.scale.category20();

d3.json("/graphdata", function(error, json) {
    var root = json.nodes[0];
    root.radius = 0;
    root.fixed = true;

    var force = d3.layout.force()
	.gravity(.1)
	.distance(200)
	.charge(-200)
	.size([width, height]);

    var svg = d3.select("body").append("svg")
	.attr("width", width)
	.attr("height", height);

    var link = svg.selectAll(".link")
	.data(json.links)
	.enter().append("line")
	.attr("class", "link");

    var node = svg.selectAll(".node")
	.data(json.nodes)
	.enter()
	.append("g")
	.attr("class", "node")
	.call(force.drag);

    var circle = svg.append("g").selectAll("circle")
	.data(force.nodes())
	.enter().append("circle")
	.attr("r", 6)
	.call(force.drag);

    var groups = d3.nest()
	.key(function(d) { return d.group; })
	.map(json.nodes)

    node.append("circle")
	.attr("cx", function(d) { return d.x; })
	.attr("cy", function(d) { return d.y; })
	.attr("r",  function(d) { return d.betweenness * 3; })
	.style("fill", function(d) { return color(d.group); })
	.attr("class", "node")
	.call(force.drag)
	.on("mousedown", function() { d3.event.stopPropagation(); });

    node.append("text")
	.attr("dx", 12)
	.attr("dy", ".35em")
	.text(function(d) { return d.id });

    svg.style("opacity", 1e-6)
	.transition()
	.duration(1000)
	.style("opacity", 1);

    d3.select("body")
	.on("mousedown", mousedown);


    force.on("tick", function() {
	link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

	node
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });

    function collide(node) {
	var r = node.radius + 16,
	nx1 = node.x - r,
	nx2 = node.x + r,
	ny1 = node.y - r,
	ny2 = node.y + r;
	return function(quad, x1, y1, x2, y2) {
	    if (quad.point && (quad.point !== node)) {
		var x = node.x - quad.point.x,
		y = node.y - quad.point.y,
		l = Math.sqrt(x * x + y * y),
		r = node.radius + quad.point.radius;
		if (l < r) {
		    l = (l - r) / l * .5;
		    node.x -= x *= l;
		    node.y -= y *= l;
		    quad.point.x += x;
		    quad.point.y += y;
		}
	    }
	    return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
	};
    }

    svg.on("mousemove", function() {
	var p1 = d3.mouse(this);
	root.px = p1[0];
	root.py = p1[1];
	force.resume();
    }); 

    function tick(e) {
	circle
	    .each(cluster(10 * e.alpha * e.alpha))
		.each(collide(.5))
		    .attr("cx", function(d) { return d.x; })
	    .attr("cy", function(d) { return d.y; });
    }

    function cluster(alpha) {
	return function(d) {
	    var cluster = clusters[d.cluster];
	    document.write(cluster)
	    if (cluster === d) return;
	    var x = d.x - cluster.x,
            y = d.y - cluster.y,
            l = Math.sqrt(x * x + y * y),
            r = d.radius + cluster.radius;
	    if (l != r) {
		l = (l - r) / l * alpha;
		d.x -= x *= l;
		d.y -= y *= l;
		cluster.x += x;
		cluster.y += y;
	    }
	};
    }


    function mousedown() {
	json.nodes.forEach(function(o, i) {
	    o.x += (Math.random() - .5) * 40;
	    o.y += (Math.random() - .5) * 40;
	});

	force.resume();
    }
});
