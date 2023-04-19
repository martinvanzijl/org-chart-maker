/**
 * Finds the intersection point between
 *     * a rectangle centered in point B
 *       with sides parallel to the x and y axes
 *     * a line passing through points A and B (the center of the rectangle)
 *
 * @param width: rectangle width
 * @param height: rectangle height
 * @param xB; rectangle center x coordinate
 * @param yB; rectangle center y coordinate
 * @param xA; point A x coordinate
 * @param yA; point A y coordinate
 * @author Federico Destefanis
 * @see <a href="https://stackoverflow.com/a/31254199/2668213">based on</a>
 */

function lineIntersectionOnRect(width, height, xB, yB, xA, yA) {

  var w = width / 2;
  var h = height / 2;

  var dx = xA - xB;
  var dy = yA - yB;

  //if A=B return B itself
  if (dx == 0 && dy == 0) return {
    x: xB,
    y: yB
  };

  var tan_phi = h / w;
  var tan_theta = Math.abs(dy / dx);

  //tell me in which quadrant the A point is
  var qx = Math.sign(dx);
  var qy = Math.sign(dy);


  if (tan_theta > tan_phi) {
    xI = xB + (h / tan_theta) * qx;
    yI = yB + h * qy;
  } else {
    xI = xB + w * qx;
    yI = yB + w * tan_theta * qy;
  }

  return {
    x: xI,
    y: yI
  };

}
