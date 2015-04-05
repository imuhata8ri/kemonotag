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
    //      .linkStrength(function(d) { return d.length *0.1; })
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

    //  var text = svg.append("g").selectAll("text")
    //      .data(force.nodes())
    //    .enter().append("text")
    //      .attr("x", 8)
    //      .attr("y", ".31em")
    //      .text(function(d) { return d.name; });

    node.append("circle")
	.style("fill", function(d) { return color(d.group); })
	.attr("r",  function(d) { return d.betweenness * 3; })
	.attr("class", "node")
	.call(force.drag);

    //  node.append("image")
    //      .attr("xlink:href", "https://github.com/favicon.ico")
    //      .attr("x", -8)
    //      .attr("y", -8)
    //      .attr("width", 16)
    //      .attr("height", 16);

    node.append("text")
	.attr("dx", 12)
	.attr("dy", ".35em")
	.text(function(d) { return d.id });


    force.on("tick", function() {
	circle
	    .each(cluster(10))
		.each(collide(.5))
		    .attr("cx", function(d) { return d.x; })
	    .attr("cy", function(d) { return d.y; });
	link
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

	node
	//        .each(cluster(10 * e.alpha * e.alpha))
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });
});