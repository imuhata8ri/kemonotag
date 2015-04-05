   var width = 960,
    height = 500;

    var fill = d3.scale.category10();


    d3.json("/graphdata" , function(error, json){

       var root = json.nodes[0];

       root.radius = 0;
       root.fixed = true;  

      var force = d3.layout.force()
         .nodes(json.nodes)
         .size([width, height])
         .gravity(0.06)
         .charge(function(d, i) { return i ? 0 : -2000; })
         .on("tick", tick)
         .start();

      var svg = d3.select("body").append("svg")
         .attr("width", width)
         .attr("height", height);

      var elem = svg.selectAll(".elem")
         .data(json.nodes)
         .enter()
         .append("g")
         .attr("class", "elem");

  elem.append("circle")
  .attr("cx", function(d) { return d.x; })
  .attr("cy", function(d) { return d.y; })
  .attr("r", 40)
  .style("fill", function(d, i) { return fill(i & 3); })
  .style("stroke", function(d, i) { return d3.rgb(fill(i & 3)).darker(2); })
  .call(force.drag)
  .on("mousedown", function() { d3.event.stopPropagation(); });

  elem.append("text")
  .text(function(d){ return d.name; });

  svg.style("opacity", 1e-6)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  d3.select("body")
    .on("mousedown", mousedown);
