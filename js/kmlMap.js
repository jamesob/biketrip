var map;
var layers = new Array();

/** initialize
 *
 * Initialize a Map.
 *
 * Parameters:
 *   - `divid`: The div id in which the map will be displayed.
 *   - `zoom`: The zoom level to initially set the map to
 */
function initializeMap(divid, zoom) {
  var myOptions = {
    zoom: zoom,
    mapTypeId: google.maps.MapTypeId.TERRAIN,
  }
  map = new google.maps.Map(document.getElementById(divid), myOptions);
}

/** loadKML
 *
 * Parameters:
 *   - `kmlPath`: A String which is the path to some kml
 */
function loadKML(kmlPath) {
    var kmlLayer = new google.maps.KmlLayer(kmlPath);
    kmlLayer.setMap(map);
    layers.push(kmlLayer);
}
