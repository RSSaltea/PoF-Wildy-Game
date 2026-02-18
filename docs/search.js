/* Wilderness Wiki — Search */
(function () {
  var PAGES = [
    // Home
    { title: "Home", url: "index.html", tags: "home wiki getting started" },

    // NPCs index
    { title: "NPCs & Bosses", url: "npcs/index.html", tags: "npcs bosses monsters creatures" },
    { title: "Revenants", url: "npcs/revenants.html", tags: "revenant family spectral spirits ether chainmace" },

    // Individual NPCs
    { title: "Revenant Goblin", url: "npcs/revenant-goblin.html", tags: "tier 1 wildy 1 revenant goblin starter beginner" },
    { title: "Revenant Knight", url: "npcs/revenant-knight.html", tags: "tier 2 wildy 10 revenant knight" },
    { title: "Chaos Fanatic", url: "npcs/chaos-fanatic.html", tags: "tier 3 wildy 20 chaos fanatic" },
    { title: "Revenant Necromancer", url: "npcs/revenant-necromancer.html", tags: "tier 4 wildy 20 revenant necromancer" },
    { title: "Revenant Abyssal Demon", url: "npcs/revenant-abyssal-demon.html", tags: "tier 4 wildy 35 revenant abyssal demon" },
    { title: "Blighted Cyclops", url: "npcs/blighted-cyclops.html", tags: "tier 4 wildy 35 blighted cyclops" },
    { title: "Abyssal Overlord", url: "npcs/abyssal-overlord.html", tags: "tier 4 wildy 35 abyssal overlord scourge boss" },
    { title: "Lord Valthyros", url: "npcs/lord-valthyros.html", tags: "tier 4 wildy 35 lord valthyros boss" },
    { title: "Revenant Archon", url: "npcs/revenant-archon.html", tags: "tier 4 wildy 40 revenant archon" },
    { title: "Zarveth the Veilbreaker", url: "npcs/zarveth-the-veilbreaker.html", tags: "tier 5 wildy 45 zarveth veilbreaker boss veil shatter" },
    { title: "Masked Figure", url: "npcs/masked-figure.html", tags: "tier 5 wildy 47 masked figure black mask shadow veil" },
    { title: "Netharis the Undying", url: "npcs/netharis-the-undying.html", tags: "tier 5 wildy 50 netharis undying boss curse" },

    // Commands index
    { title: "Commands", url: "commands/index.html", tags: "commands list all" },

    // Command pages
    { title: "Getting Started", url: "commands/getting-started.html", tags: "start reset profile create new beginner" },
    { title: "Combat", url: "commands/combat.html", tags: "fight venture attack tele teleport eat drink hp health combat pvp" },
    { title: "Inventory", url: "commands/inventory.html", tags: "inv inventory equip unequip gear drop inspect examine ground pickup blacklist lock" },
    { title: "Banking", url: "commands/banking.html", tags: "bank deposit withdraw banking" },
    { title: "Trading", url: "commands/trading.html", tags: "trade trading accept add remove cancel" },
    { title: "Shop", url: "commands/shop.html", tags: "shop buy sell list store" },
    { title: "Crafting", url: "commands/crafting.html", tags: "craft craftables breakdown runecraft rc rune" },
    { title: "Slayer", url: "commands/slayer.html", tags: "slayer task skip shop buy npcs block points xp" },
    { title: "Alchemy", url: "commands/alchemy.html", tags: "alch alchemy auto high alch nature rune coins" },
    { title: "Presets", url: "commands/presets.html", tags: "preset presets create load delete override check" },
    { title: "Miscellaneous", url: "commands/misc.html", tags: "stats profile kc killcount highscores pets pet chest open misc" }
  ];

  /* Resolve URLs relative to the wiki root.
     We detect the base from the stylesheet href which is already correct
     on every page: "style.css" at root, "../style.css" in subdirs. */
  var baseUrl = (function () {
    var link = document.querySelector('link[href*="style.css"]');
    if (link) {
      return link.getAttribute("href").replace("style.css", "");
    }
    return "";
  })();

  function resolveUrl(rel) {
    return baseUrl + rel;
  }

  function search(query) {
    if (!query) return [];
    var q = query.toLowerCase().trim();
    var words = q.split(/\s+/);
    var scored = [];

    for (var i = 0; i < PAGES.length; i++) {
      var p = PAGES[i];
      var title = p.title.toLowerCase();
      var tags = p.tags.toLowerCase();
      var haystack = title + " " + tags;
      var score = 0;

      /* exact title match */
      if (title === q) score += 100;
      /* title starts with query */
      else if (title.indexOf(q) === 0) score += 60;
      /* title contains query */
      else if (title.indexOf(q) >= 0) score += 40;

      /* word matching */
      for (var w = 0; w < words.length; w++) {
        if (words[w].length < 1) continue;
        if (title.indexOf(words[w]) >= 0) score += 20;
        else if (tags.indexOf(words[w]) >= 0) score += 10;
      }

      if (score > 0) scored.push({ page: p, score: score });
    }

    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 8);
  }

  function init() {
    var wrapper = document.querySelector(".search-wrapper");
    if (!wrapper) return;

    var input = wrapper.querySelector(".search-input");
    var dropdown = wrapper.querySelector(".search-dropdown");

    function render(results) {
      if (results.length === 0) {
        dropdown.style.display = "none";
        dropdown.innerHTML = "";
        return;
      }
      var html = "";
      for (var i = 0; i < results.length; i++) {
        var r = results[i].page;
        html += '<a class="search-item" href="' + resolveUrl(r.url) + '">' +
                '<span class="search-item-title">' + r.title + '</span>' +
                '</a>';
      }
      dropdown.innerHTML = html;
      dropdown.style.display = "block";
    }

    input.addEventListener("input", function () {
      render(search(this.value));
    });

    input.addEventListener("focus", function () {
      if (this.value) render(search(this.value));
    });

    /* keyboard navigation */
    input.addEventListener("keydown", function (e) {
      var items = dropdown.querySelectorAll(".search-item");
      var active = dropdown.querySelector(".search-item.active");
      var idx = -1;
      for (var i = 0; i < items.length; i++) {
        if (items[i] === active) { idx = i; break; }
      }

      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (active) active.classList.remove("active");
        idx = (idx + 1) % items.length;
        items[idx].classList.add("active");
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (active) active.classList.remove("active");
        idx = idx <= 0 ? items.length - 1 : idx - 1;
        items[idx].classList.add("active");
      } else if (e.key === "Enter") {
        if (active) {
          e.preventDefault();
          window.location.href = active.href;
        }
      } else if (e.key === "Escape") {
        dropdown.style.display = "none";
        input.blur();
      }
    });

    /* close dropdown when clicking outside */
    document.addEventListener("click", function (e) {
      if (!wrapper.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
