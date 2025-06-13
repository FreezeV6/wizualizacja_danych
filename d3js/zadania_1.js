// z1
const temperatura = [12, 14, 17, 19, 18, 16, 13];
const daty = ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25", "2025-04-26", "2025-04-27"];

const parseTime = d3.timeParse("%Y-%m-%d");
const data1 = daty.map((d, i) => ({ date: parseTime(d), temp: temperatura[i] }));

const svg1 = d3.select("#lineChart"),
      margin1 = {top: 20, right: 30, bottom: 30, left: 40},
      width1 = +svg1.attr("width") - margin1.left - margin1.right,
      height1 = +svg1.attr("height") - margin1.top - margin1.bottom,
      g1 = svg1.append("g").attr("transform", `translate(${margin1.left},${margin1.top})`);

const x1 = d3.scaleTime()
    .domain(d3.extent(data1, d => d.date))
    .range([0, width1]);

const y1 = d3.scaleLinear()
    .domain([d3.min(data1, d => d.temp) - 2, d3.max(data1, d => d.temp) + 2])
    .range([height1, 0]);

g1.append("g")
    .attr("transform", `translate(0,${height1})`)
    .call(d3.axisBottom(x1)
        .tickFormat(d3.timeFormat("%d.%m.%Y"))
        .ticks(7)
    );

g1.append("g")
    .call(d3.axisLeft(y1));

g1.append("path")
    .datum(data1)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 2)
    .attr("d", d3.line()
        .x(d => x1(d.date))
        .y(d => y1(d.temp))
    );

// z2
const zysk = [50, 80, 45, 60, 90, 30, 70];
const dni = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Niedz"];

const svg2 = d3.select("#barChart"),
      margin2 = {top: 20, right: 30, bottom: 40, left: 40},
      width2 = +svg2.attr("width") - margin2.left - margin2.right,
      height2 = +svg2.attr("height") - margin2.top - margin2.bottom,
      g2 = svg2.append("g").attr("transform", `translate(${margin2.left},${margin2.top})`);

const x2 = d3.scaleBand()
    .domain(dni)
    .range([0, width2])
    .padding(0.2);

const y2 = d3.scaleLinear()
    .domain([0, d3.max(zysk) + 10])
    .range([height2, 0]);

g2.append("g")
    .attr("transform", `translate(0,${height2})`)
    .call(d3.axisBottom(x2));

g2.append("g")
    .call(d3.axisLeft(y2));

g2.selectAll(".bar")
    .data(zysk)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d, i) => x2(dni[i]))
    .attr("y", d => y2(d))
    .attr("width", x2.bandwidth())
    .attr("height", d => height2 - y2(d))
    .attr("fill", "orange");

// z3
const dane = [10, 20, 30, 40];
const oznaczenia = ["A", "B", "C", "D"];

const svg3 = d3.select("#pieChart"),
      width3 = +svg3.attr("width"),
      height3 = +svg3.attr("height"),
      radius3 = Math.min(width3, height3) / 2;

const g3 = svg3.append("g")
    .attr("transform", `translate(${width3/2},${height3/2})`);

const color = d3.scaleOrdinal()
    .domain(oznaczenia)
    .range(d3.schemeCategory10);

const pie = d3.pie();
const arc = d3.arc()
    .innerRadius(0)
    .outerRadius(radius3);

const arcs = g3.selectAll(".arc")
    .data(pie(dane))
    .enter()
    .append("g")
    .attr("class", "arc");

arcs.append("path")
    .attr("d", arc)
    .attr("fill", (d, i) => color(oznaczenia[i]));

arcs.append("text")
    .attr("transform", d => `translate(${arc.centroid(d)})`)
    .attr("text-anchor", "middle")
    .attr("font-size", "14px")
    .text((d, i) => oznaczenia[i]);