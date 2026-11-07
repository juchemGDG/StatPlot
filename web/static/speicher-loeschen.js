// „Gespeicherte Daten löschen“ – entfernt die in diesem Browser (localStorage) abgelegten Daten dieser App.
// Präfixe stehen im Attribut data-praefixe des Script-Tags (mehrere mit Komma getrennt).
(function () {
  var skript = document.currentScript;
  var praefixe = ((skript && skript.getAttribute('data-praefixe')) || '').split(',').filter(Boolean);
  function loeschen() {
    if (!praefixe.length) return;
    if (!window.confirm('Alle in diesem Browser gespeicherten Daten dieser App löschen?\n(Dateien, die du heruntergeladen hast, bleiben erhalten.)')) return;
    try {
      Object.keys(localStorage).forEach(function (k) {
        if (praefixe.some(function (p) { return k.indexOf(p) === 0; })) localStorage.removeItem(k);
      });
    } catch (e) { /* Speicher gesperrt: nichts zu löschen */ }
    location.reload();
  }
  function start() {
    var knoepfe = document.querySelectorAll('.speicher-loeschen');
    for (var i = 0; i < knoepfe.length; i++) knoepfe[i].addEventListener('click', loeschen);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
