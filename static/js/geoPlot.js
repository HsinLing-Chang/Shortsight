async function drawMixedMap() {
  const geoData = await fetch("/api/report/geolocation", {
    credentials: "include",
  }).then((r) => r.json());
  const interactionData = geoData.data;
  console.log(interactionData);

  //   const interactionData = [
  //     {
  //       country: "Taiwan",
  //       city: "Taipei",
  //       interactions: 120,
  //       lat: 25.0478,
  //       lon: 121.532,
  //     },
  //     {
  //       country: "Taiwan",
  //       city: "Kaohsiung",
  //       interactions: 70,
  //       lat: 22.6273,
  //       lon: 120.3014,
  //     },
  //     {
  //       country: "France",
  //       city: "France",
  //       interactions: 48,
  //       lat: 48.85,
  //       lon: 2.35,
  //     },
  //   ];

  // Choropleth trace
  const choropleth = {
    type: "choropleth",
    locationmode: "country names",
    locations: interactionData.map((d) => d.country),
    z: interactionData.map((d) => d.interactions),
    zauto: true,
    // featureidkey: "properties.city",
    colorscale: [
      [0, "#e0f3ff"],
      [0.2, "#a6c8ff"],
      [0.5, "#4a90e2"],
      [0.75, "#2166ac"],
      [1, "#08306b"],
    ],
    colorbar: {
      title: "區塊熱度",
      tickvals: [1, 3, 5, 7, 10],
    },
    showscale: true,
    marker: {
      line: {
        color: "rgba(255,255,255,0.5)",
        width: 1,
      },
    },
  };

  // Scattergeo trace
  const scatter = {
    type: "scattergeo",
    mode: "markers+text",
    lat: interactionData.map((d) => d.latitude),
    lon: interactionData.map((d) => d.longitude),
    text: interactionData.map((d) => `${d.city}: ${d.interactions}`),
    marker: {
      size: interactionData.map((d) => Math.sqrt(d.interactions) * 10),
      color: "red",
      opacity: 0.8,
      line: { width: 1, color: "#fff" },
    },
    name: "城市互動熱點",
  };

  Plotly.newPlot("geoMap", [choropleth, scatter], {
    geo: {
      scope: "world",
      projection: { type: "natural earth" },
      showland: true,
      landcolor: "rgb(240,240,240)",
      fitbounds: "locations",
    },
    margin: { t: 20, b: 20 },
  });
}

drawMixedMap();
