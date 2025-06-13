const dane_z3 = [10, 20, 30, 40, 50];

const svg = d3.select("#barChart_z3");
const margin = {top: 30, right: 30, bottom: 30, left: 40};
const width = +svg.attr("width") - margin.left - margin.right;
const height = +svg.attr("height") - margin.top - margin.bottom;

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

const x = d3.scaleBand()
    .domain(dane_z3.map((_, i) => i))
    .range([0, width])
    .padding(0.3);

const y = d3.scaleLinear()
    .domain([0, d3.max(dane_z3)])
    .range([height, 0]);

g.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).tickFormat(d => d + 1)); // opcjonalnie numeruj 1,2,3,...

g.append("g")
    .call(d3.axisLeft(y));

const bars = g.selectAll(".bar")
    .data(dane_z3)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d, i) => x(i))
    .attr("y", height)    // Start od dołu
    .attr("width", x.bandwidth())
    .attr("height", 0)    // Start od zera
    .attr("fill", "green")
    .on("click", function() {
        d3.select(this)
            .transition()
            .duration(300)
            .attr("fill", "red");
    });

bars.transition()
    .duration(1000)
    .attr("y", d => y(d))
    .attr("height", d => height - y(d));

g.selectAll(".label")
    .data(dane_z3)
    .enter()
    .append("text")
    .attr("class", "label")
    .attr("x", (d, i) => x(i) + x.bandwidth() / 2)
    .attr("y", d => y(d) - 5)
    .attr("text-anchor", "middle")
    .text(d => d);