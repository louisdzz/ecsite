(function () {
  'use strict';
  document.addEventListener('annuaire:results', function (event) {
    var section = document.getElementById('aviation-intro');
    if (section) section.hidden = event.detail.category !== 'jets';
  });
})();
