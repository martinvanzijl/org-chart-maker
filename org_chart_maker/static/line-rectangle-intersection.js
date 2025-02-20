function lineIntersectsRectangle(x1, y1, x2, y2, bx1, by1, bx2, by2) {
  let t = 0;

    //  If the start or end of the line is inside the rect then we assume
    //  collision, as rects are solid for our use-case.

  if ((x1 >= bx1 && x1 <= bx2 && y1 >= by1 && y1 <= by2) ||
      (x2 >= bx1 && x2 <= bx2 && y2 >= by1 && y2 <= by2)) {
    return true;
  }

  if (x1 < bx1 && x2 >= bx1) { //  Left edge
    t = y1 + (y2 - y1) * (bx1 - x1) / (x2 - x1);
    if (t > by1 && t <= by2) {
      return true;
    }
  }
  else if (x1 > bx2 && x2 <= bx2) { //  Right edge
    t = y1 + (y2 - y1) * (bx2 - x1) / (x2 - x1);
    if (t >= by1 && t <= by2) {
      return true;
    }
  }
  if (y1 < by1 && y2 >= by1) { //  Top edge
    t = x1 + (x2 - x1) * (by1 - y1) / (y2 - y1);
    if (t >= bx1 && t <= bx2) {
      return true;
    }
  } else if (y1 > by2 && y2 <= by2) {  //  Bottom edge
    t = x1 + (x2 - x1) * (by2 - y1) / (y2 - y1);
    if (t >= bx1 && t <= bx2) {
      return true;
    }
  }
  return false;
}
