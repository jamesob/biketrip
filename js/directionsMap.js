var directionsDisplay;
var directionsService = new google.maps.DirectionsService();
var map;
var geocoder;

/** initialize
 *
 * Initialize a DirectionsDisplay object, a Map, and bind the Map to the
 * DirectionsDisplay object.
 *
 * Parameters:
 *   - `divid`: The div id in which the map will be displayed.
 *   - `origin`: A location String designating the center of the map.
 */
function initialize(divid, origin) {
  directionsDisplay = new google.maps.DirectionsRenderer();
  geocoder = new google.maps.Geocoder();
  var start;
  geocoder.geocode( {'address': origin}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      start = results[0].geometry.location;
    }
  });
  var myOptions = {
    zoom: 7,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    center: start
  }
  map = new google.maps.Map(document.getElementById(divid), myOptions);
  directionsDisplay.setMap(map);
}

/** makeBikeRoute
 *
 * Return a `DirectionsRequest` object based on an array of Strings identifying
 * desired locations along a route.
 *
 * Parameters: 
 *   - `locs`: an array of location Strings
 * Returns:
 *   - a `DirectionsRequest` object.
 */
function makeBikeRoute(locs) {
  var waypts = [];
  locs.map(function (x) {
    waypts = waypts.concat({
      location: x,
      stopover: false
    });
  });
  return {
    origin: locs[0],
    destination: locs[locs.length-1],
    waypoints: waypts,
    travelMode: google.maps.DirectionsTravelMode.BICYCLING
  };
};
  
/** calcRoute
 *
 * Parameters:
 *   - `requestData`: A `DirectionsRequest` object signifying the path to route.
 */
function calcRoute(requestData) {
  directionsService.route(requestData, function(result, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      directionsDisplay.setDirections(result);
    } else {
      alert(status);
    }
  });
}

function drawRoute(locs) {
  calcRoute(makeBikeRoute(locs));
}

