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
    { title: "Revenant Imp", url: "npcs/revenant-imp.html", tags: "tier 1 wildy 1 revenant imp range" },
    { title: "Wandering Warlock", url: "npcs/wandering-warlock.html", tags: "tier 1 wildy 1 wandering warlock magic" },
    { title: "Cursed Spirit", url: "npcs/cursed-spirit.html", tags: "tier 1 wildy 1 cursed spirit necro" },
    { title: "Feral Scorpion", url: "npcs/feral-scorpion.html", tags: "tier 1 wildy 1 feral scorpion crush melee" },
    { title: "Revenant Pyromancer", url: "npcs/revenant-pyromancer.html", tags: "tier 2 wildy 10 revenant pyromancer magic fire" },
    { title: "Corrupted Ranger", url: "npcs/corrupted-ranger.html", tags: "tier 2 wildy 10 corrupted ranger range" },
    { title: "Shade", url: "npcs/shade.html", tags: "tier 2 wildy 10 shade necro" },
    { title: "Infernal Imp", url: "npcs/infernal-imp.html", tags: "tier 2 wildy 10 infernal imp crush melee" },
    { title: "Phantom Archer", url: "npcs/phantom-archer.html", tags: "tier 3 wildy 20 phantom archer range flickerwisp" },
    { title: "Risen Bonecaller", url: "npcs/risen-bonecaller.html", tags: "tier 3 wildy 25 risen bonecaller necro soulflame" },
    { title: "Windstrider", url: "npcs/windstrider.html", tags: "tier 3 wildy 22 windstrider range boss evasive dash" },
    { title: "Infernal Warlock", url: "npcs/infernal-warlock.html", tags: "tier 3 wildy 24 infernal warlock magic boss infernal blaze" },
    { title: "Hollow Warden", url: "npcs/hollow-warden.html", tags: "tier 4 wildy 32 hollow warden crush melee resources stone shell" },
    { title: "Duskwalker", url: "npcs/duskwalker.html", tags: "tier 5 wildy 47 duskwalker range boss shadow volley nightfall" },
    { title: "Emberlord Kael", url: "npcs/emberlord-kael.html", tags: "tier 5 wildy 48 emberlord kael magic boss flame burst soulfire" },
    { title: "Gravekeeper Azriel", url: "npcs/gravekeeper-azriel.html", tags: "tier 5 wildy 49 gravekeeper azriel necro boss soul siphon" },
    { title: "Fury Bunny", url: "npcs/fury-bunny.html", tags: "tier 3 wildy 23 fury bunny melee slash paws of fury" },

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
    { title: "Veilbreaker", url: "items/veilbreaker.html", tags: "veilbreaker mainhand weapon melee zarveth" },
    { title: "Death Guard", url: "items/death-guard.html", tags: "death guard mainhand weapon necro necromancy" },
    { title: "Viggora's Chainmace", url: "items/viggoras-chainmace.html", tags: "viggora chainmace mainhand weapon melee ether npc bonus" },
    { title: "Abyssal Chainmace", url: "items/abyssal-chainmace.html", tags: "abyssal chainmace mainhand weapon melee ether npc bonus craft" },
    { title: "Fury Paw", url: "items/fury-paw.html", tags: "fury paw fpaw mainhand weapon melee slash paws of fury bunny" },

    // Range Weapons
    { title: "Rotwood shortbow", url: "items/rotwood-shortbow.html", tags: "rotwood shortbow mainhand weapon range bow arrows" },
    { title: "Whisperwood bow", url: "items/whisperwood-bow.html", tags: "whisperwood bow mainhand weapon range arrows" },
    { title: "Ironwood bow", url: "items/ironwood-bow.html", tags: "ironwood bow mainhand weapon range arrows" },
    { title: "Hexwood bow", url: "items/hexwood-bow.html", tags: "hexwood bow mainhand weapon range arrows" },
    { title: "Bone crossbow", url: "items/bone-crossbow.html", tags: "bone crossbow mainhand weapon range bolts" },
    { title: "Nightfall bow", url: "items/nightfall-bow.html", tags: "nightfall bow two-handed weapon range dragon arrows duskwalker" },

    // Magic Weapons
    { title: "Galestaff", url: "items/galestaff.html", tags: "galestaff staff mainhand weapon magic air rune" },
    { title: "Tidestaff", url: "items/tidestaff.html", tags: "tidestaff staff mainhand weapon magic water rune" },
    { title: "Stonestaff", url: "items/stonestaff.html", tags: "stonestaff staff mainhand weapon magic earth rune" },
    { title: "Flamestaff", url: "items/flamestaff.html", tags: "flamestaff staff mainhand weapon magic fire rune" },
    { title: "Voidtouched wand", url: "items/voidtouched-wand.html", tags: "voidtouched wand mainhand weapon magic death rune" },
    { title: "Soulfire staff", url: "items/soulfire-staff.html", tags: "soulfire staff two-handed weapon magic blood rune emberlord" },

    // Necro Weapons
    { title: "Spectral scythe", url: "items/spectral-scythe.html", tags: "spectral scythe mainhand weapon necro necromancy" },
    { title: "Deathwarden staff", url: "items/deathwarden-staff.html", tags: "deathwarden staff two-handed weapon necro necromancy" },
    { title: "Netharis's Grasp", url: "items/nethariss-grasp.html", tags: "netharis grasp mainhand weapon necro necromancy boss" },

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
    { title: "Voidfire Quiver", url: "items/voidfire-quiver.html", tags: "voidfire quiver offhand range" },
    { title: "Cindertome", url: "items/cindertome.html", tags: "cindertome tome offhand magic" },
    { title: "Soulbound Grimoire", url: "items/soulbound-grimoire.html", tags: "soulbound grimoire offhand necro necromancy" },

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

    // Range Armour
    { title: "Scaleweave coif", url: "items/scaleweave-coif.html", tags: "scaleweave coif helm head range armour" },
    { title: "Scaleweave body", url: "items/scaleweave-body.html", tags: "scaleweave body range armour" },
    { title: "Scaleweave chaps", url: "items/scaleweave-chaps.html", tags: "scaleweave chaps legs range armour" },
    { title: "Scaleweave boots", url: "items/scaleweave-boots.html", tags: "scaleweave boots feet range armour" },
    { title: "Scaleweave vambraces", url: "items/scaleweave-vambraces.html", tags: "scaleweave vambraces gloves range armour" },
    { title: "Drakescale body", url: "items/drakescale-body.html", tags: "drakescale body range armour" },
    { title: "Drakescale chaps", url: "items/drakescale-chaps.html", tags: "drakescale chaps legs range armour" },
    { title: "Voidfire coif", url: "items/voidfire-coif.html", tags: "voidfire coif helm head range armour duskwalker" },
    { title: "Voidfire body", url: "items/voidfire-body.html", tags: "voidfire body range armour duskwalker" },
    { title: "Voidfire chaps", url: "items/voidfire-chaps.html", tags: "voidfire chaps legs range armour duskwalker" },
    { title: "Voidfire boots", url: "items/voidfire-boots.html", tags: "voidfire boots feet range armour duskwalker" },
    { title: "Voidfire vambraces", url: "items/voidfire-vambraces.html", tags: "voidfire vambraces gloves range armour duskwalker" },

    // Magic Armour
    { title: "Thornweave helm", url: "items/thornweave-helm.html", tags: "thornweave helm head magic armour" },
    { title: "Thornweave body", url: "items/thornweave-body.html", tags: "thornweave body magic armour" },
    { title: "Thornweave legs", url: "items/thornweave-legs.html", tags: "thornweave legs magic armour" },
    { title: "Thornweave boots", url: "items/thornweave-boots.html", tags: "thornweave boots feet magic armour" },
    { title: "Thornweave gloves", url: "items/thornweave-gloves.html", tags: "thornweave gloves magic armour" },
    { title: "Wraithcaller's robetop", url: "items/wraithcallers-robetop.html", tags: "wraithcaller robetop body magic armour" },
    { title: "Wraithcaller's robeskirt", url: "items/wraithcallers-robeskirt.html", tags: "wraithcaller robeskirt legs magic armour" },
    { title: "Soulfire hat", url: "items/soulfire-hat.html", tags: "soulfire hat helm head magic armour emberlord" },
    { title: "Soulfire robetop", url: "items/soulfire-robetop.html", tags: "soulfire robetop body magic armour emberlord" },
    { title: "Soulfire robeskirt", url: "items/soulfire-robeskirt.html", tags: "soulfire robeskirt legs magic armour emberlord" },
    { title: "Soulfire boots", url: "items/soulfire-boots.html", tags: "soulfire boots feet magic armour emberlord" },
    { title: "Soulfire gloves", url: "items/soulfire-gloves.html", tags: "soulfire gloves magic armour emberlord" },

    // Necro Armour
    { title: "Ghostweave hood", url: "items/ghostweave-hood.html", tags: "ghostweave hood helm head necro armour" },
    { title: "Ghostweave robetop", url: "items/ghostweave-robetop.html", tags: "ghostweave robetop body necro armour" },
    { title: "Ghostweave robeskirt", url: "items/ghostweave-robeskirt.html", tags: "ghostweave robeskirt legs necro armour" },
    { title: "Ghostweave boots", url: "items/ghostweave-boots.html", tags: "ghostweave boots feet necro armour" },
    { title: "Ghostweave gloves", url: "items/ghostweave-gloves.html", tags: "ghostweave gloves necro armour" },
    { title: "Deathwarden robetop", url: "items/deathwarden-robetop.html", tags: "deathwarden robetop body necro armour" },
    { title: "Deathwarden robeskirt", url: "items/deathwarden-robeskirt.html", tags: "deathwarden robeskirt legs necro armour" },
    { title: "Netharis's hood", url: "items/nethariss-hood.html", tags: "netharis hood helm head necro armour boss" },
    { title: "Netharis's robetop", url: "items/nethariss-robetop.html", tags: "netharis robetop body necro armour boss" },
    { title: "Netharis's robeskirt", url: "items/nethariss-robeskirt.html", tags: "netharis robeskirt legs necro armour boss" },
    { title: "Netharis's boots", url: "items/nethariss-boots.html", tags: "netharis boots feet necro armour boss" },
    { title: "Netharis's gloves", url: "items/nethariss-gloves.html", tags: "netharis gloves necro armour boss" },

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

    // Ammo
    { title: "Bronze arrows", url: "items/bronze-arrows.html", tags: "bronze arrows ammo range" },
    { title: "Iron arrows", url: "items/iron-arrows.html", tags: "iron arrows ammo range" },
    { title: "Steel arrows", url: "items/steel-arrows.html", tags: "steel arrows ammo range" },
    { title: "Mithril arrows", url: "items/mithril-arrows.html", tags: "mithril arrows ammo range" },
    { title: "Adamant arrows", url: "items/adamant-arrows.html", tags: "adamant addy arrows ammo range" },
    { title: "Rune arrows", url: "items/rune-arrows.html", tags: "rune arrows ammo range" },
    { title: "Dragon arrows", url: "items/dragon-arrows.html", tags: "dragon arrows ammo range" },
    { title: "Bone bolts", url: "items/bone-bolts.html", tags: "bone bolts ammo range crossbow" },

    // Runes
    { title: "Air rune", url: "items/air-rune.html", tags: "air rune elemental runecraft magic galestaff" },
    { title: "Water rune", url: "items/water-rune.html", tags: "water rune elemental runecraft magic tidestaff" },
    { title: "Earth rune", url: "items/earth-rune.html", tags: "earth rune elemental runecraft magic stonestaff" },
    { title: "Fire rune", url: "items/fire-rune.html", tags: "fire rune elemental runecraft magic flamestaff" },
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
    { title: "Ancient Effigy", url: "items/ancient-effigy.html", tags: "ancient effigy valuable alch consumable consume slayer xp lamp" },
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
    { title: "Eclipse of the Five", url: "items/eclipse-of-the-five.html", tags: "eclipse five amulet enchant attack necklace" },

    // Pets
    { title: "Tiny Revenant", url: "items/tiny-revenant.html", tags: "tiny revenant pet rev" },
    { title: "Baby Chaos Fanatic", url: "items/baby-chaos-fanatic.html", tags: "baby chaos fanatic pet" },
    { title: "Mini Overlord", url: "items/mini-overlord.html", tags: "mini overlord pet abyssal" },
    { title: "Lil' Undying", url: "items/lil-undying.html", tags: "lil undying pet netharis" },
    { title: "Zarvethy", url: "items/zarvethy.html", tags: "zarvethy pet zarveth veilbreaker" },
    { title: "Splat", url: "items/splat.html", tags: "splat pet valthyros" },
    { title: "Flickerwisp", url: "items/flickerwisp.html", tags: "flickerwisp pet phantom archer windstrider range" },
    { title: "Tiny Dark Archer", url: "items/tiny-dark-archer.html", tags: "tiny dark archer pet duskwalker range" },
    { title: "Soulflame", url: "items/soulflame.html", tags: "soulflame pet risen bonecaller emberlord gravekeeper necro magic" },
    { title: "Embersprite", url: "items/embersprite.html", tags: "embersprite pet infernal warlock magic" },

    // Grand Exchange
    { title: "Grand Exchange", url: "grand-exchange/index.html", tags: "grand exchange ge buy sell trade prices market offers" },

    // Commands index
    { title: "Commands", url: "commands/index.html", tags: "commands list all" },

    // Command pages
    { title: "Getting Started", url: "commands/getting-started.html", tags: "start reset profile create new beginner consume" },
    { title: "Combat", url: "commands/combat.html", tags: "fight venture attack tele teleport eat drink hp health combat pvp" },
    { title: "Inventory", url: "commands/inventory.html", tags: "inv inventory equip unequip gear drop inspect examine ground pickup blacklist lock" },
    { title: "Banking", url: "commands/banking.html", tags: "bank deposit depo withdraw banking noted" },
    { title: "Trading", url: "commands/trading.html", tags: "trade trading accept add remove cancel" },
    { title: "Shop", url: "commands/shop.html", tags: "shop buy sell list store" },
    { title: "Crafting", url: "commands/crafting.html", tags: "craft craftables breakdown runecraft rc rune cut gem enchant consume effigy" },
    { title: "Slayer", url: "commands/slayer.html", tags: "slayer task skip shop buy npcs block points xp" },
    { title: "Alchemy", url: "commands/alchemy.html", tags: "alch alchemy auto high alch nature rune coins" },
    { title: "Presets", url: "commands/presets.html", tags: "preset presets create load delete override check" },
    { title: "Miscellaneous", url: "commands/misc.html", tags: "stats profile kc killcount highscores pets pet chest open mysterious bone key misc" }
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
