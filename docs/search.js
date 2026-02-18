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

    // Items index
    { title: "Items", url: "items/index.html", tags: "items weapons armour armor gear equipment" },

    // Weapons
    { title: "Starter Sword", url: "items/starter-sword.html", tags: "starter sword mainhand weapon melee free" },
    { title: "Rune dagger", url: "items/rune-dagger.html", tags: "rune dagger mainhand weapon melee" },
    { title: "Rune scimitar", url: "items/rune-scimitar.html", tags: "rune scimitar scimmy mainhand weapon melee" },
    { title: "Dragon dagger", url: "items/dragon-dagger.html", tags: "dragon dagger dds mainhand weapon melee" },
    { title: "Dragon scimitar", url: "items/dragon-scimitar.html", tags: "dragon scimitar dscim mainhand weapon melee" },
    { title: "Dragon 2h sword", url: "items/dragon-2h-sword.html", tags: "dragon 2h sword d2h two-handed weapon melee" },
    { title: "Abyssal Whip", url: "items/abyssal-whip.html", tags: "abyssal whip mainhand weapon melee" },
    { title: "Abyssal Scourge", url: "items/abyssal-scourge.html", tags: "abyssal scourge mainhand weapon melee" },
    { title: "Veilbreaker", url: "items/veilbreaker.html", tags: "veilbreaker mainhand weapon melee zarveth best" },
    { title: "Death Guard", url: "items/death-guard.html", tags: "death guard mainhand weapon necro necromancy" },
    { title: "Viggora's Chainmace", url: "items/viggoras-chainmace.html", tags: "viggora chainmace mainhand weapon melee ether npc bonus" },
    { title: "Abyssal Chainmace", url: "items/abyssal-chainmace.html", tags: "abyssal chainmace mainhand weapon melee ether npc bonus craft" },

    // Offhands
    { title: "Rune sq shield", url: "items/rune-sq-shield.html", tags: "rune sq shield offhand defence melee" },
    { title: "Skull Lantern", url: "items/skull-lantern.html", tags: "skull lantern offhand necro necromancy" },
    { title: "Bronze Defender", url: "items/bronze-defender.html", tags: "bronze defender offhand cyclops" },
    { title: "Iron Defender", url: "items/iron-defender.html", tags: "iron defender offhand cyclops" },
    { title: "Steel Defender", url: "items/steel-defender.html", tags: "steel defender offhand cyclops" },
    { title: "Black Defender", url: "items/black-defender.html", tags: "black defender offhand cyclops" },
    { title: "Mithril Defender", url: "items/mithril-defender.html", tags: "mithril defender offhand cyclops" },
    { title: "Adamant Defender", url: "items/adamant-defender.html", tags: "adamant addy defender offhand cyclops" },
    { title: "Rune Defender", url: "items/rune-defender.html", tags: "rune defender offhand cyclops" },
    { title: "Bone Defender", url: "items/bone-defender.html", tags: "bone defender offhand craft cursed" },

    // Armour
    { title: "Starter Platebody", url: "items/starter-platebody.html", tags: "starter platebody body armour free" },
    { title: "Rune platebody", url: "items/rune-platebody.html", tags: "rune platebody body armour plate" },
    { title: "Rune chainbody", url: "items/rune-chainbody.html", tags: "rune chainbody body armour chain" },
    { title: "Dragon platebody", url: "items/dragon-platebody.html", tags: "dragon platebody body armour plate" },
    { title: "Zarveth's Ascendant Platebody", url: "items/zarveths-ascendant-platebody.html", tags: "zarveth ascendant platebody body armour boss" },
    { title: "Rune platelegs", url: "items/rune-platelegs.html", tags: "rune platelegs legs armour" },
    { title: "Dragon platelegs", url: "items/dragon-platelegs.html", tags: "dragon platelegs legs armour" },
    { title: "Zarveth's Ascendant Platelegs", url: "items/zarveths-ascendant-platelegs.html", tags: "zarveth ascendant platelegs legs armour boss" },
    { title: "Rune full helm", url: "items/rune-full-helm.html", tags: "rune full helm head armour" },
    { title: "Rune med helm", url: "items/rune-med-helm.html", tags: "rune med helm head armour" },
    { title: "Zarveth's Ascendant Mask", url: "items/zarveths-ascendant-mask.html", tags: "zarveth ascendant mask helm head armour boss" },
    { title: "Dragon boots", url: "items/dragon-boots.html", tags: "dragon boots feet armour dboots" },
    { title: "Black Mask", url: "items/black-mask.html", tags: "black mask helm slayer masked figure" },
    { title: "Slayer Helmet", url: "items/slayer-helmet.html", tags: "slayer helmet helm craft damage bonus" },
    { title: "Shady Slayer Helm", url: "items/shady-slayer-helm.html", tags: "shady slayer helm helmet shadow veil upgrade" },

    // Accessories
    { title: "Amulet of Seeping", url: "items/amulet-of-seeping.html", tags: "amulet seeping necklace heal lifesteal blood rune valthyros" },
    { title: "Ring of Valthyros", url: "items/ring-of-valthyros.html", tags: "ring valthyros defence attack" },
    { title: "Shroud of the Undying", url: "items/shroud-of-the-undying.html", tags: "shroud undying cape nullify damage netharis" },
    { title: "Bracelet of ethereum", url: "items/bracelet-of-ethereum.html", tags: "bracelet ethereum gloves revenant damage reduction" },
    { title: "Wristwraps of the Damned", url: "items/wristwraps-of-the-damned.html", tags: "wristwraps damned gloves bleed overlord" },
    { title: "Bracelet of Slayer Aggression", url: "items/bracelet-of-slayer-aggression.html", tags: "bracelet slayer aggression gloves guarantee task chaos rune" },

    // Food
    { title: "Lobster", url: "items/lobster.html", tags: "lobster food heal 12" },
    { title: "Shark", url: "items/shark.html", tags: "shark food heal 20" },
    { title: "Manta Ray", url: "items/manta-ray.html", tags: "manta ray food heal 22" },
    { title: "Anglerfish", url: "items/anglerfish.html", tags: "anglerfish angler food heal 24" },
    { title: "Veilfruit", url: "items/veilfruit.html", tags: "veilfruit food heal 28" },

    // Potions
    { title: "Strength (4)", url: "items/strength-4.html", tags: "strength potion str pot attack boost" },
    { title: "Super Strength (4)", url: "items/super-strength-4.html", tags: "super strength potion sup str attack boost" },

    // Runes
    { title: "Nature rune", url: "items/nature-rune.html", tags: "nature rune nat alchemy runecraft" },
    { title: "Chaos rune", url: "items/chaos-rune.html", tags: "chaos rune runecraft slayer aggression" },
    { title: "Law rune", url: "items/law-rune.html", tags: "law rune runecraft" },
    { title: "Death rune", url: "items/death-rune.html", tags: "death rune runecraft" },
    { title: "Blood rune", url: "items/blood-rune.html", tags: "blood rune runecraft seeping" },
    { title: "Bone Rune", url: "items/bone-rune.html", tags: "bone rune drop" },
    { title: "Cosmic rune", url: "items/cosmic-rune.html", tags: "cosmic rune runecraft enchant" },

    // Materials & Pouches
    { title: "Pure essence", url: "items/pure-essence.html", tags: "pure essence ess runecraft material" },
    { title: "Small pouch", url: "items/small-pouch.html", tags: "small pouch essence runecraft" },
    { title: "Medium pouch", url: "items/medium-pouch.html", tags: "medium pouch essence runecraft" },
    { title: "Large pouch", url: "items/large-pouch.html", tags: "large pouch essence runecraft" },
    { title: "Giant pouch", url: "items/giant-pouch.html", tags: "giant pouch essence runecraft netharis" },
    { title: "Colossal pouch", url: "items/colossal-pouch.html", tags: "colossal pouch essence runecraft" },
    { title: "Revenant ether", url: "items/revenant-ether.html", tags: "revenant ether rev ether chainmace fuel material" },
    { title: "Cyclops Eye", url: "items/cyclops-eye.html", tags: "cyclops eye material craft" },
    { title: "Abyssal ash", url: "items/abyssal-ash.html", tags: "abyssal ash material craft chainmace" },
    { title: "Abyssal charm", url: "items/abyssal-charm.html", tags: "abyssal charm material craft slayer helmet" },
    { title: "Overlord core fragment", url: "items/overlord-core-fragment.html", tags: "overlord core fragment material craft chainmace" },
    { title: "Revenant Relic Shard", url: "items/revenant-relic-shard.html", tags: "revenant relic shard material craft defender" },
    { title: "Revenant Totem", url: "items/revenant-totem.html", tags: "revenant totem material craft defender" },
    { title: "Cursed Bone", url: "items/cursed-bone.html", tags: "cursed bone material craft defender archon" },
    { title: "Shadow Veil", url: "items/shadow-veil.html", tags: "shadow veil material craft shady slayer masked figure" },

    // Valuables & Keys
    { title: "Mysterious key", url: "items/mysterious-key.html", tags: "mysterious key chest open shop loot" },
    { title: "Bone key", url: "items/bone-key.html", tags: "bone key archon" },
    { title: "Ancient Effigy", url: "items/ancient-effigy.html", tags: "ancient effigy valuable alch" },
    { title: "Ancient Emblem", url: "items/ancient-emblem.html", tags: "ancient emblem valuable alch rare" },
    { title: "Uncut sapphire", url: "items/uncut-sapphire.html", tags: "uncut sapphire gem" },
    { title: "Uncut emerald", url: "items/uncut-emerald.html", tags: "uncut emerald gem" },
    { title: "Uncut diamond", url: "items/uncut-diamond.html", tags: "uncut diamond gem" },
    { title: "Uncut ruby", url: "items/uncut-ruby.html", tags: "uncut ruby gem cut" },
    { title: "Uncut dragonstone", url: "items/uncut-dragonstone.html", tags: "uncut dragonstone gem" },

    // Cut Gems & Crafting
    { title: "Gold Bar", url: "items/gold-bar.html", tags: "gold bar material craft amulet" },
    { title: "Sapphire", url: "items/sapphire.html", tags: "sapphire cut gem omnigem craft" },
    { title: "Emerald", url: "items/emerald.html", tags: "emerald cut gem omnigem craft" },
    { title: "Ruby", url: "items/ruby.html", tags: "ruby cut gem omnigem craft" },
    { title: "Diamond", url: "items/diamond.html", tags: "diamond cut gem omnigem craft" },
    { title: "Dragonstone", url: "items/dragonstone.html", tags: "dragonstone cut gem omnigem craft" },
    { title: "Omnigem", url: "items/omnigem.html", tags: "omnigem fused gem craft amulet" },
    { title: "Omnigem Amulet", url: "items/omnigem-amulet.html", tags: "omnigem amulet craft enchant eclipse" },
    { title: "Eclipse of the Five", url: "items/eclipse-of-the-five.html", tags: "eclipse five amulet enchant attack best necklace" },

    // Pets
    { title: "Tiny Revenant", url: "items/tiny-revenant.html", tags: "tiny revenant pet rev" },
    { title: "Baby Chaos Fanatic", url: "items/baby-chaos-fanatic.html", tags: "baby chaos fanatic pet" },
    { title: "Mini Overlord", url: "items/mini-overlord.html", tags: "mini overlord pet abyssal" },
    { title: "Lil' Undying", url: "items/lil-undying.html", tags: "lil undying pet netharis" },
    { title: "Zarvethy", url: "items/zarvethy.html", tags: "zarvethy pet zarveth veilbreaker" },
    { title: "Splat", url: "items/splat.html", tags: "splat pet valthyros" },

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
