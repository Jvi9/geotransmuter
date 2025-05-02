let baseMaps = {};  // Si tienes mapas base (como satélite, calles, etc.)
let overlayMaps = {};  // Aquí pondremos los shapefiles

const map = L.map('map').setView([-13.15, -74.21], 18); // Ayacucho

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri, USGS, NASA, <a href="https://www.esri.com/">Esri</a>'
            }).addTo(map);

// Función para asignar colores a las capas
function getLayerColor(layerName) {
  // Aquí puedes especificar un color para cada capa según su nombre
  const colorMap = {
    'Buildings': '#013a63',
    'Land Use': '#31572c',
    'Natural': 'brown',
    'Places': 'red',
    'POFW': 'purple',
    'POIs': 'orange',
    'Railways': 'gray',
    'Roads': '#3f0d12',
    'Traffic': 'yellow',
    'Transport': 'pink',
    'Waterways': 'cyan',
    'Water': 'teal'
  };

  // Si no se encuentra el nombre en el mapa, asigna un color por defecto
  return colorMap[layerName] || 'blue';
}

// Load and show the GeoJSON layer
function addLayerToMap(name, url) {
  fetch(url)
    .then(res => res.json())
    .then(data => {
      const color = getLayerColor(name);  // Get the color for this layer
      
      const layer = L.geoJSON(data, {
        style: { color: color, weight: 2 },  // Use the assigned color
        onEachFeature: function (feature, layer) {
          // Add a popup to each feature to show its properties when clicked
          if (feature.properties) {
            let popupContent = '<strong>Attributes:</strong><ul>';
            
            // Loop through each property and add it to the popup content
            for (const [key, value] of Object.entries(feature.properties)) {
              popupContent += `<li><strong>${key}:</strong> ${value}</li>`;
            }
            
            popupContent += '</ul>';
            
            // Bind the popup to the layer
            layer.bindPopup(popupContent);
          }
        }
      }).addTo(map);

      // Crear checkbox para la capa en el panel lateral
      const layerCheckbox = document.createElement('div');
      layerCheckbox.classList.add('layer');
      layerCheckbox.innerHTML = `
        <input type="checkbox" id="${name}" checked>
        <label for="${name}">${name}</label>
      `;
      
      // Al hacer clic en el checkbox, se muestra u oculta la capa
      layerCheckbox.querySelector('input').addEventListener('change', function () {
        if (this.checked) {
          map.addLayer(layer);
        } else {
          map.removeLayer(layer);
        }
      });

      // Añadir al panel lateral
      document.querySelector('.side-panel').appendChild(layerCheckbox);
    });
}

// Añadir capas (esto es solo un ejemplo, debes usar las rutas correctas)
const availableLayers = {
  'gis_osm_buildings': 'Buildings',
  'gis_osm_landuse': 'Land Use',
  // 'gis_osm_natural': 'Natural',
  // 'gis_osm_places': 'Places',
  // 'gis_osm_pofw': 'POFW',
  // 'gis_osm_pois': 'POIs',
  'gis_osm_railways': 'Railways',
  'gis_osm_roads': 'Roads',
  //'gis_osm_traffic': 'Traffic',
  //'gis_osm_transport': 'Transport',
  'gis_osm_waterways': 'Waterways',
  'gis_osm_water': 'Water'
};

// Loop through each layer and add it to the map using key-value pairs
Object.entries(availableLayers).forEach(([layerKey, layerDisplayName]) => {
  addLayerToMap(layerDisplayName, `/geojson/${layerKey}`);
});

