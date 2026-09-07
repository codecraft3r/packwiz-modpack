from __future__ import annotations

import json

"""Reviewed quest edits accepted on dev and kept separate from generation logic.

The live SNBT edits in commits 92a9020, 4ed3207, and 777a1e0 were accepted
before the generator caught up. This explicit overlay lets the source emit
the reviewed result without silently reading its own generated output.
"""

REVIEWED_SOURCE_COMMITS = ("92a9020", "4ed3207", "777a1e0")
REVIEWED_QUEST_OVERRIDES = json.loads(r'''{
  "7A11C0DF00100006": {
    "description": [
      "A public road, workshop, or refuge needs a named entrance and a responsible keeper. Claims remain inviolable; public access exists only where the owner clearly grants it. Ask a member to witness your understanding."
    ],
    "tasks": [
      {
        "id": "7A11C1DF00100006",
        "title": "I understand how public access is granted - witnessed by a member",
        "type": "checkmark"
      }
    ]
  },
  "7A11C0DF00100003": {
    "tasks": [
      {
        "id": "7A11C1DF00100003",
        "title": "I agree to stop on request - witnessed by a member",
        "type": "checkmark"
      }
    ]
  },
  "7A11C0DF00100007": {
    "tasks": [
      {
        "id": "7A11C1DF00100007",
        "title": "I will keep rivalry claim-safe and reversible - witnessed by a member",
        "type": "checkmark"
      }
    ]
  },
  "7A11C0DF00100005": {
    "description": [
      "You have read the rules that keep a persistent world playable: name public access, obtain consent, and keep rivalry reversible. Event guests may sign with a sponsor member present and backfill the third promise later. The calling board is now open."
    ],
    "min_required_dependencies": 2,
    "subtitle": "Required · Any two promises, third vouched"
  },
  "7A11C0DF00200002": {
    "description": [
      "Become a Vampire through Vampirism and keep the fang that marks the transformation. The House campaign begins with shelter and blood logistics, then opens ritual, magic, transport, and hospitality specialties. Taking a second calling renounces the first: pass its mark on before you claim another."
    ],
    "tasks": [
      {
        "consume_items": true,
        "id": "7A11C1DF00200002",
        "item": {
          "count": 1,
          "id": "vampirism:vampire_fang"
        },
        "title": "Offer a vampire fang",
        "type": "item"
      },
      {
        "advancement": "vampirism:vampire/become_vampire",
        "criterion": "",
        "id": "7A11C1DF00200003",
        "type": "advancement"
      }
    ]
  },
  "7A11C0DF00200003": {
    "description": [
      "Choose Neutral when you want ordinary survival, trade, infrastructure, and public services without faction obligations. This attestation is the entire civic route; it grants trade stock and record supplies instead of faction arms, and creates no hidden third faction. Claiming a faction calling later ends Neutral protection."
    ],
    "icon": {
      "id": "minecraft:emerald"
    },
    "rewards": [
      {
        "id": "7A11C2DF00200003",
        "item": {
          "count": 1,
          "id": "numismatics:sprocket"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00200005",
        "item": {
          "count": 16,
          "id": "minecraft:cooked_beef"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00200006",
        "item": {
          "count": 1,
          "id": "minecraft:spyglass"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00200007",
        "item": {
          "count": 8,
          "id": "minecraft:emerald"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0020000A",
        "item": {
          "count": 16,
          "id": "minecraft:paper"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0020000D",
        "item": {
          "count": 1,
          "id": "minecraft:shield"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0020000E",
        "item": {
          "count": 1,
          "id": "minecraft:white_bed"
        },
        "team_reward": false,
        "type": "item"
      }
    ]
  },
  "7A11C0DF00200004": {
    "description": [
      "Become a Hunter through Vampirism and keep the garlic injection used to enter the profession. The Order campaign begins with field equipment, then opens medicine, wards, reconnaissance, construction, and holy support. Taking a second calling renounces the first: pass its mark on before you claim another."
    ],
    "tasks": [
      {
        "consume_items": true,
        "id": "7A11C1DF00200007",
        "item": {
          "count": 1,
          "id": "vampirism:injection_garlic"
        },
        "title": "Offer a garlic injection",
        "type": "item"
      },
      {
        "advancement": "vampirism:hunter/become_hunter",
        "criterion": "",
        "id": "7A11C1DF00200008",
        "type": "advancement"
      }
    ]
  },
  "7A11C0DF00200007": {
    "description": [
      "Your first calling determines which faction campaign, if any, you maintain. Market services remain open to House, Order, and Neutral teams, and later curiosity does not rewrite the protected opt-out. One calling per member - a second calling renounces the first. Complete it as a party - every member checks in."
    ],
    "tasks": [
      {
        "id": "7A11C1DF00200009",
        "title": "We confirm this calling as a party - each member checks in",
        "type": "checkmark"
      }
    ]
  },
  "7A11C0DF00300002": {
    "description": [
      "Gather an essential construction stock of stone bricks, logs, iron bars, and lanterns. Completing this foundation rewards a manageable starter building kit with two stacks of stone, a stack each of oak and spruce logs, iron, copper, and one Sprocket to spend at the Market."
    ],
    "rewards": [
      {
        "id": "7A11C2DF00300006",
        "item": {
          "count": 1,
          "id": "numismatics:sprocket"
        },
        "team_reward": false,
        "title": "1 Sprocket",
        "type": "item"
      },
      {
        "id": "7A11C2DF00300064",
        "item": {
          "count": 64,
          "id": "minecraft:stone"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00300065",
        "item": {
          "count": 64,
          "id": "minecraft:stone"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00300082",
        "item": {
          "count": 64,
          "id": "minecraft:oak_log"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00300096",
        "item": {
          "count": 64,
          "id": "minecraft:spruce_log"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0030000A",
        "item": {
          "count": 16,
          "id": "minecraft:iron_ingot"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00300046",
        "item": {
          "count": 16,
          "id": "minecraft:copper_ingot"
        },
        "team_reward": false,
        "type": "item"
      }
    ]
  },
  "7A11C0DF00400001": {
    "rewards": [
      {
        "id": "7A11C2DF00400001",
        "item": {
          "count": 1,
          "id": "numismatics:bevel"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00400002",
        "item": {
          "count": 1,
          "id": "vampirism:vampire_cloak_red_black"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00400003",
        "item": {
          "count": 4,
          "id": "vampirism:blood_bottle"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00400004",
        "item": {
          "count": 8,
          "id": "minecraft:glass_bottle"
        },
        "team_reward": false,
        "type": "item"
      }
    ]
  },
  "7A11C0DF00400002": {
    "description": [
      "Raise an Altar of Infusion: four Altar Pillars crowned with four Altar Tips over a stone foundation. The upgraded altar unlocks stronger rites and steadier blood work."
    ]
  },
  "7A11C0DF00400003": {
    "description": [
      "Muster the Household: raise a House Notice Board, draft the Household Roll, and convene the four commissions that raise the Spire, Foundry, Hall, and Vault. Ring the muster bell and set the House to work."
    ],
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF0040005E",
        "item": {
          "count": 1,
          "id": "supplementaries:notice_board"
        },
        "title": "Raise a House Notice Board",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF0040005F",
        "item": {
          "count": 1,
          "id": "minecraft:writable_book"
        },
        "title": "Draft the Household Roll",
        "type": "item"
      },
      {
        "id": "7A11C1DF00400060",
        "title": "I convened the four commissions - witnessed by a member",
        "type": "checkmark"
      }
    ],
    "title": "Household Muster"
  },
  "7A11C0DF0040000E": {
    "description": [
      "Commission the Dark Spire as the House night-watch: raise lightning rods, post a lookout spyglass, and hang signal lamps that call the House home after dark."
    ],
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF00400061",
        "item": {
          "count": 1,
          "id": "minecraft:lightning_rod"
        },
        "count": 8,
        "title": "Raise eight Lightning Rods",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400062",
        "item": {
          "count": 1,
          "id": "minecraft:spyglass"
        },
        "title": "Post a lookout Spyglass",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400063",
        "item": {
          "count": 1,
          "id": "minecraft:redstone_lamp"
        },
        "count": 4,
        "title": "Hang four Spire Signal Lamps",
        "type": "item"
      }
    ]
  },
  "7A11C0DF0040000F": {
    "description": [
      "Commission the Blood Foundry as the House rendering rig: set seething cauldrons, rig hoist chains, and bank furnace fuel to render blood and tallow for the House works."
    ]
  },
  "7A11C0DF00400010": {
    "description": [
      "Commission the Thrall Hall as the House rest-house: fill provision barrels, keep low hearth fires, and set red coffins where bound thralls sleep through the day. The hall feeds the night shift and keeps blood close at hand."
    ],
    "icon": {
      "id": "vampirism:coffin_red"
    },
    "rewards": [
      {
        "id": "7A11C2DF00400065",
        "item": {
          "count": 1,
          "id": "numismatics:sprocket"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00400066",
        "item": {
          "count": 4,
          "id": "vampirism:blood_bottle"
        },
        "team_reward": false,
        "type": "item"
      }
    ],
    "subtitle": "Commission · Thralls and rest",
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF00400067",
        "item": {
          "count": 1,
          "id": "minecraft:barrel"
        },
        "count": 4,
        "title": "Fill four Thrall Provision Barrels",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400068",
        "item": {
          "count": 1,
          "id": "minecraft:campfire"
        },
        "count": 2,
        "title": "Keep two Low Hearth Fires",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400069",
        "item": {
          "count": 1,
          "id": "vampirism:coffin_red"
        },
        "count": 2,
        "title": "Set two Thrall Coffins",
        "type": "item"
      }
    ],
    "title": "Thrall Hall"
  },
  "7A11C0DF00400011": {
    "description": [
      "Commission the Blood Vault as the House archive: shelve records bookshelves, stand a catalogue lectern, and glaze tinted panes for the sealed blood reserve."
    ]
  },
  "7A11C0DF00400009": {
    "description": [
      "Pay the Night's Shroud: veil the Spire route with tinted panes, set soul-flames where the dark pools deepest, then walk the shadowed perimeter to prove safe passage."
    ],
    "rewards": [
      {
        "id": "7A11C2DF00400069",
        "item": {
          "count": 4,
          "id": "numismatics:sprocket"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0040006A",
        "item": {
          "count": 16,
          "id": "minecraft:tinted_glass"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0040006B",
        "item": {
          "count": 4,
          "id": "minecraft:redstone_lamp"
        },
        "team_reward": false,
        "type": "item"
      }
    ],
    "subtitle": "Specialty · Shadow veiling",
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF0040006D",
        "item": {
          "count": 1,
          "id": "minecraft:tinted_glass"
        },
        "count": 16,
        "title": "Veil sixteen Shadow Panes",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF0040006E",
        "item": {
          "count": 1,
          "id": "minecraft:soul_lantern"
        },
        "count": 8,
        "title": "Set eight Omen Soul-Flames",
        "type": "item"
      },
      {
        "id": "7A11C1DF0040006F",
        "title": "I walked the shadowed perimeter - witnessed by a member",
        "type": "checkmark"
      }
    ],
    "title": "Night's Shroud"
  },
  "7A11C0DF00400008": {
    "description": [
      "Post the night omens from the Dark Spire: ring the muster bell, light soul-flames for the far farms, and pin written notices so no House member misses the call."
    ],
    "icon": {
      "id": "minecraft:bell"
    },
    "rewards": [
      {
        "id": "7A11C2DF00400035",
        "item": {
          "count": 2,
          "id": "numismatics:sprocket"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00400036",
        "item": {
          "count": 16,
          "id": "minecraft:paper"
        },
        "team_reward": false,
        "type": "item"
      }
    ],
    "subtitle": "Specialty · Omen signs",
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF00400013",
        "item": {
          "count": 1,
          "id": "minecraft:bell"
        },
        "title": "Ring the Omen Bell",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400014",
        "item": {
          "count": 1,
          "id": "minecraft:soul_lantern"
        },
        "count": 4,
        "title": "Light four Omen Soul-Flames",
        "type": "item"
      }
    ],
    "title": "Night Omens"
  },
  "7A11C0DF0040000D": {
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF0040002B",
        "item": {
          "count": 1,
          "id": "vampirism:sunscreen_beacon"
        },
        "title": "Raise a Sunscreen Beacon",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF0040002C",
        "item": {
          "count": 1,
          "id": "vampirism:umbrella"
        },
        "title": "Carry a Sunshade Umbrella",
        "type": "item"
      },
      {
        "id": "7A11C1DF0040002D",
        "title": "I crossed the route at noon - witnessed by a member",
        "type": "checkmark"
      }
    ]
  },
  "7A11C0DF0040000C": {
    "description": [
      "Keep the tithe table: a low hearth fire, a sealed blood vessel for the House tithe, and candles that burn through the night watch. The table turns feeding into a rite the whole House can share."
    ],
    "icon": {
      "id": "vampirism:blood_bottle"
    },
    "rewards": [
      {
        "id": "7A11C2DF00400029",
        "item": {
          "count": 1,
          "id": "numismatics:sprocket"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0040002A",
        "item": {
          "count": 4,
          "id": "vampirism:blood_bottle"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0040002B",
        "item": {
          "count": 8,
          "id": "minecraft:candle"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0040002C",
        "item": {
          "count": 16,
          "id": "minecraft:torch"
        },
        "team_reward": false,
        "type": "item"
      }
    ],
    "subtitle": "Specialty · Tithe service",
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF00400028",
        "item": {
          "count": 1,
          "id": "minecraft:campfire"
        },
        "title": "Keep a Low Tithe Fire",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400029",
        "item": {
          "count": 1,
          "id": "vampirism:blood_container"
        },
        "title": "Seal a Blood Tithe Vessel",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF0040002A",
        "item": {
          "count": 1,
          "id": "minecraft:candle"
        },
        "count": 8,
        "title": "Set eight Tithe Candles",
        "type": "item"
      }
    ],
    "title": "Blood Tithe"
  },
  "7A11C0DF00400006": {
    "description": [
      "Bind the Thrall Hall on paper: stand a registry lectern, open the oath book, and take a first thrall-oath for the night shift. Names in the book keep feeding and watch duties honest."
    ],
    "subtitle": "Specialty · Oaths and records",
    "tasks": [
      {
        "consume_items": false,
        "id": "7A11C1DF0040000F",
        "item": {
          "count": 1,
          "id": "minecraft:lectern"
        },
        "title": "Stand an Oath Lectern",
        "type": "item"
      },
      {
        "consume_items": false,
        "id": "7A11C1DF00400010",
        "item": {
          "count": 1,
          "id": "minecraft:writable_book"
        },
        "title": "Open the Oath Book",
        "type": "item"
      },
      {
        "id": "7A11C1DF00400011",
        "title": "I bound a first thrall-oath - witnessed by a member",
        "type": "checkmark"
      }
    ],
    "title": "Thrall Registry"
  },
  "7A11C0DF00500005": {
    "description": [
      "Consume two Sprockets for a personal early-Create starter of alloy, shafts, cogwheels, belts, water wheels, a millstone and basin, a wrench, and copper for first machines. Restocks after five minutes. A beginning, not precision mechanisms, brass-age parts, or an automated factory."
    ],
    "rewards": [
      {
        "id": "7A11C2DF0050000C",
        "item": {
          "count": 16,
          "id": "create:andesite_alloy"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050000D",
        "item": {
          "count": 8,
          "id": "create:shaft"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050000E",
        "item": {
          "count": 8,
          "id": "create:cogwheel"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050000F",
        "item": {
          "count": 4,
          "id": "create:large_cogwheel"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500065",
        "item": {
          "count": 4,
          "id": "create:belt_connector"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500066",
        "item": {
          "count": 1,
          "id": "create:wrench"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500067",
        "item": {
          "count": 16,
          "id": "minecraft:copper_ingot"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050006F",
        "item": {
          "count": 2,
          "id": "create:water_wheel"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050007A",
        "item": {
          "count": 1,
          "id": "create:millstone"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050007B",
        "item": {
          "count": 1,
          "id": "create:basin"
        },
        "team_reward": false,
        "type": "item"
      }
    ]
  },
  "7A11C0DF00500009": {
    "rewards": [
      {
        "id": "7A11C2DF00500014",
        "item": {
          "count": 2,
          "id": "minecraft:white_bed"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500015",
        "item": {
          "count": 2,
          "id": "minecraft:shield"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500016",
        "item": {
          "count": 16,
          "id": "minecraft:honey_bottle"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500017",
        "item": {
          "count": 1,
          "id": "minecraft:golden_apple"
        },
        "team_reward": false,
        "type": "item"
      }
    ]
  },
  "7A11C0DF0050000A": {
    "rewards": [
      {
        "id": "7A11C2DF00500018",
        "item": {
          "count": 2,
          "id": "minecraft:saddle"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF00500019",
        "item": {
          "count": 16,
          "id": "minecraft:lead"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050001A",
        "item": {
          "count": 32,
          "id": "minecraft:firework_rocket"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050001B",
        "item": {
          "count": 4,
          "id": "minecraft:oak_boat"
        },
        "team_reward": false,
        "type": "item"
      },
      {
        "id": "7A11C2DF0050001C",
        "item": {
          "count": 4,
          "id": "minecraft:compass"
        },
        "team_reward": false,
        "type": "item"
      }
    ]
  },
  "7A11C0DF00500007": {
    "description": [
      "Consume four Sprockets for a personal civic-works package behind one shared project: bulk Stone and Oak, scaffolding, Glass, Chains, and Lanterns at a scale no single lower kit matches. Restocks after five minutes. Shared building stock, not diamonds, alloy, or combat gear."
    ],
    "subtitle": "4 Sprockets · 5 min",
    "tasks": [
      {
        "consume_items": true,
        "id": "7A11C1DF00500006",
        "item": {
          "count": 4,
          "id": "numismatics:sprocket"
        },
        "title": "Submit 4 Sprockets",
        "type": "item"
      }
    ]
  },
  "7A11C0DF00500015": {
    "x": -5.2
  }
}
''')

# The complete mapping above is retained as reconciliation history.  Ch4/5
# were subsequently redesigned in the authoritative generator; replaying
# their old overlay would silently undo that work and can introduce duplicate
# stable IDs.  Only accepted Ch1-3 edits and the protected First Thirst
# baseline are active during generation.
ACTIVE_REVIEWED_QUEST_OVERRIDES = {
    quest_id: fields
    for quest_id, fields in REVIEWED_QUEST_OVERRIDES.items()
    if quest_id.startswith((
        "7A11C0DF001", "7A11C0DF002", "7A11C0DF003", "7A11C0DF00400001",
    ))
}
