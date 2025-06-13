d3.csv("data.csv").then(data => {

    console.log("Wszystkie dane:", data);

    const filteredData = data.filter(d => +d.value > 25);

    console.log("Po filtracji (value > 25):", filteredData);

    const sortedData = filteredData.sort((a, b) => +b.value - +a.value);

    console.log("Po sortowaniu malejąco:", sortedData);

}).catch(error => {
    console.error("Błąd podczas wczytywania pliku CSV:", error);
});
