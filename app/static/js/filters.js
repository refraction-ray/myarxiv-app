Vue.filter('datef', function (d) {
  return $.strftime(d);
});