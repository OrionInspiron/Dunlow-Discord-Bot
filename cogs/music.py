import os
import asyncio
import random
import time
import urllib.parse
from typing import Optional, Dict, List, Set, Any

# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord.ext import commands, tasks

# All 224 non-lyrical / soothing instrumental tracks from lofi.radio (by Purrple Cat)
LOFI_RADIO_SONGS = [
    "3 A.M. Radio.mp3", "A Place to Hide.mp3", "Adrift.mp3", "Aether.mp3", "After Hours.mp3",
    "All Curled Up.mp3", "Alley Cat.mp3", "Artifact.mp3", "Astral Projection.mp3", "Aurora.mp3",
    "Awakenings.mp3", "Bayou Blues.mp3", "Beautiful Day.mp3", "Bird Bath.mp3", "Birdhouse.mp3",
    "Blood Moon.mp3", "Bloom.mp3", "Breathing Underwater.mp3", "Cable Car.mp3", "Calm Waters.mp3",
    "Can't Sleep.mp3", "Carousel.mp3", "Cave of Solace.mp3", "Celestial Sands.mp3", "Changes.mp3",
    "Chasing Snowflakes.mp3", "Chugging Along.mp3", "Come One, Come All.mp3", "Comfy.mp3",
    "Constellations.mp3", "Contact.mp3", "Convergence.mp3", "Cool Breeze.mp3", "Corner Store.mp3",
    "Cosmic Echoes.mp3", "Cosmic Web.mp3", "Creation.mp3", "Creatures of the Night.mp3",
    "Crescent Moon.mp3", "Crossroads.mp3", "Cruisin'.mp3", "Dance of the Cacti.mp3",
    "Dancing Dandelions.mp3", "Dancing Shadows.mp3", "Dark Corners.mp3", "Dark Forest.mp3",
    "Day's End.mp3", "Defunct.mp3", "Deja Vu.mp3", "Desert Rain.mp3", "Desolate.mp3",
    "Discovery.mp3", "Distant Ships.mp3", "Dont Look Back.mp3", "Downpour.mp3", "Downtown.mp3",
    "Dream Machine.mp3", "Dream State.mp3", "Drifting.mp3", "Dune Drifter.mp3", "Ebb and Flow.mp3",
    "Echoes of Yesterday.mp3", "Eerie Glow.mp3", "Egress.mp3", "Elevated.mp3", "Embrace.mp3",
    "Empty Sidewalks.mp3", "End of the Line.mp3", "Epiphany.mp3", "Equinox.mp3", "Ethereal.mp3",
    "Everchanging.mp3", "Exhale.mp3", "Exploration.mp3", "Eye of the Storm.mp3", "Eyes in the Dark.mp3",
    "Fading.mp3", "Fallen.mp3", "Familiar Faces.mp3", "Field Of Fireflies.mp3", "Flourish.mp3",
    "Fog Blanket.mp3", "Forget-Me-Not.mp3", "Fourth Dimension.mp3", "Fragments.mp3", "Frolic.mp3",
    "Frosted Evergreen.mp3", "Frozen Flowers.mp3", "Gentle Breeze.mp3", "Ghost Planet.mp3",
    "Ghost Town.mp3", "Ghosties.mp3", "Gingerbread House.mp3", "Glowing Tides.mp3",
    "Going With The Flow.mp3", "Goosebumps.mp3", "Green Tea.mp3", "Half Awake.mp3", "Happy Trails.mp3",
    "Heart of the Ocean.mp3", "Ice Palace.mp3", "Icicles.mp3", "In Between.mp3", "In the Moment.mp3",
    "In the Past.mp3", "In the Walls.mp3", "Infinite.mp3", "Insomnia.mp3", "Intertwined.mp3",
    "Labyrinth.mp3", "Lazy Afternoon.mp3", "Leviathan.mp3", "Lighthouse.mp3", "Lonely.mp3",
    "Long Day.mp3", "Looking Up.mp3", "Lost Paradise.mp3", "Lost Souls.mp3", "Lost and Found.mp3",
    "Lost at Sea.mp3", "Low Tide.mp3", "Lullaby.mp3", "Luminous.mp3", "Lurking in the Shadows.mp3",
    "Lush.mp3", "Maelstrom.mp3", "Magical Moments.mp3", "Mesa's Edge.mp3", "Message in a Bottle.mp3",
    "Meteorites.mp3", "Mirage.mp3", "Missing Pieces.mp3", "Morning Dew.mp3", "Moving Landscapes.mp3",
    "Mysterious Passenger.mp3", "Nevermore.mp3", "Nexus.mp3", "Night Light.mp3", "Night Owls.mp3",
    "Night Train.mp3", "Nightfall.mp3", "Not Alone.mp3", "Nowhere to Hide.mp3", "Oddity.mp3",
    "On the Brink.mp3", "Once in a Lifetime.mp3", "Otherworldly.mp3", "Out of Place.mp3",
    "Out of the Blue.mp3", "Palm Tree.mp3", "Paradox.mp3", "Passing Time.mp3",
    "Peppermint Mocha.mp3", "Phantom Waltz.mp3", "Pineapple Popsicle.mp3", "Pitter Patter.mp3",
    "Planetary Alignment.mp3", "Rainy Streets.mp3", "Refractions.mp3", "Rewind.mp3",
    "Rift in Time.mp3", "Rocky Shores.mp3", "Rooftop Rendezvous.mp3", "Running Late.mp3",
    "Sandstorm.mp3", "Satellite.mp3", "Sea Foam.mp3", "Sea of Stars.mp3", "Seashells.mp3",
    "Secret Of The Forest.mp3", "Serendipity.mp3", "Serenity Now.mp3", "Shelter.mp3",
    "Signs of Life.mp3", "Silent Wood.mp3", "Siren's Song.mp3", "Skeleton Dance.mp3",
    "Skyscrapers.mp3", "Snow Pillow.mp3", "Soft.mp3", "Solitude.mp3", "Sonder.mp3",
    "Spring Showers.mp3", "Star Bright.mp3", "Starlit Beach.mp3", "Starry Night.mp3",
    "Stars Collide.mp3", "Starseed.mp3", "Stasis.mp3", "Step Right Up.mp3", "Still of the Night.mp3",
    "Stranded.mp3", "Strange Fog.mp3", "Stray.mp3", "Streetlights.mp3", "Strike of Midnight.mp3",
    "Sunken Secrets.mp3", "Supernova.mp3", "Take Me With You.mp3", "The Bells.mp3",
    "The Dungeon.mp3", "The Midnight Diner.mp3", "The Murk.mp3", "The Portal.mp3",
    "The Toymaker.mp3", "Through the Trees.mp3", "Thunderous Waves.mp3", "Time Loop.mp3",
    "Time to Think.mp3", "Timeless.mp3", "Toasty.mp3", "Torn.mp3", "Tracks to Nowhere.mp3",
    "Transformation.mp3", "Tumbleweeds.mp3", "Tunnels.mp3", "Twilight Market.mp3", "UFO.mp3",
    "Under the Canopy.mp3", "Undertow.mp3", "Underwater Cavern.mp3", "Uninvited.mp3",
    "Unreality.mp3", "Upside Down.mp3", "Verdant.mp3", "Visions.mp3", "Waiting for the Sun.mp3",
    "Wanderlust.mp3", "Warm Horizon.mp3", "Weightless.mp3", "Weird Dream.mp3",
    "What Lies Beyond.mp3", "Wild Strawberry.mp3", "Window Seat.mp3", "Wish You Were Here.mp3",
    "Wishes.mp3", "Wishing Well.mp3", "Wonderland.mp3", "Wonderment.mp3", "Zero Gravity.mp3",
    "Zzz....mp3"
]

LOFI_TRACKS: List[Dict[str, str]] = [
    {
        "title": fn[:-4] if fn.endswith(".mp3") else fn,
        "artist": "Purrple Cat",
        "source": "lofi.radio",
        "url": f"https://lofi.radio/songs/{urllib.parse.quote(fn)}",
        "station": "lofi"
    }
    for fn in LOFI_RADIO_SONGS
]

# Iconic video game themes (Minecraft, Undertale, Zelda, Mario 64, Hollow Knight, Chrono Trigger, Halo, Pokémon)
GAMING_TRACKS: List[Dict[str, str]] = [
    # Minecraft (C418 / Lena Raine)
    {"title": "Sweden", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2018.%20Sweden.mp3", "station": "gaming"},
    {"title": "Wet Hands", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2013.%20Wet%20Hands.mp3", "station": "gaming"},
    {"title": "Subwoofer Lullaby", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2003.%20Subwoofer%20Lullaby.mp3", "station": "gaming"},
    {"title": "Mice on Venus", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2011.%20Mice%20on%20Venus.mp3", "station": "gaming"},
    {"title": "Haggstrom", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2007.%20Haggstrom.mp3", "station": "gaming"},
    {"title": "Minecraft", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2008.%20Minecraft.mp3", "station": "gaming"},
    {"title": "Aria Math", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2037.%20Aria%20Math.mp3", "station": "gaming"},
    {"title": "Cat", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2019.%20Cat.mp3", "station": "gaming"},
    {"title": "Danny", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2021.%20Danny.mp3", "station": "gaming"},
    {"title": "Moog City", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2006.%20Moog%20City.mp3", "station": "gaming"},
    {"title": "Dry Hands", "artist": "C418", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%20-%2012.%20Dry%20Hands.mp3", "station": "gaming"},
    {"title": "Pigstep", "artist": "Lena Raine", "source": "Minecraft", "url": "https://archive.org/download/minecraft-2011-ost/Minecraft%201.16%20-%2004.%20Pigstep.mp3", "station": "gaming"},

    # Undertale (Toby Fox)
    {"title": "Once Upon a Time", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20001%20Once%20Upon%20a%20Time.mp3", "station": "gaming"},
    {"title": "Fallen Down", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20004%20Fallen%20Down.mp3", "station": "gaming"},
    {"title": "Snowdin Town", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20022%20Snowdin%20Town.mp3", "station": "gaming"},
    {"title": "Memory", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20034%20Memory.mp3", "station": "gaming"},
    {"title": "Hotel", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20054%20Hotel.mp3", "station": "gaming"},
    {"title": "Undertale", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20071%20Undertale.mp3", "station": "gaming"},
    {"title": "His Theme", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20090%20His%20Theme.mp3", "station": "gaming"},
    {"title": "Reunited", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20092%20Reunited.mp3", "station": "gaming"},
    {"title": "MEGALOVANIA", "artist": "Toby Fox", "source": "Undertale", "url": "https://archive.org/download/undertaleoriginalsoundtrack/Undertale%20OST%20-%20100%20MEGALOVANIA.mp3", "station": "gaming"},

    # The Legend of Zelda: Ocarina of Time (Koji Kondo)
    {"title": "Title Theme", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/01.%20Title%20Theme.mp3", "station": "gaming"},
    {"title": "Hyrule Field Main Theme", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/19.%20Hyrule%20Field%20Main%20Theme.mp3", "station": "gaming"},
    {"title": "Zelda's Lullaby", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/26.%20Ocarina%20~Zelda%27s%20Lullaby~.mp3", "station": "gaming"},
    {"title": "Zora's Domain", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/40.%20Zora%27s%20Domain.mp3", "station": "gaming"},
    {"title": "Great Fairy's Fountain", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/41.%20Great%20Fairy%27s%20Fountain.mp3", "station": "gaming"},
    {"title": "Temple of Time", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/45.%20Temple%20of%20Time.mp3", "station": "gaming"},
    {"title": "Song of Storms", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/57.%20Ocarina%20~Song%20of%20Storms~.mp3", "station": "gaming"},
    {"title": "Gerudo Valley", "artist": "Koji Kondo", "source": "The Legend of Zelda: Ocarina of Time", "url": "https://archive.org/download/tloz-oot-original-soundtrack/69.%20Gerudo%20Valley.mp3", "station": "gaming"},

    # Super Mario 64 (Koji Kondo)
    {"title": "Title Theme", "artist": "Koji Kondo", "source": "Super Mario 64", "url": "https://archive.org/download/super-mario-64-soundtrack/Super%20Mario%2064%20%28Soundtrack%29/1-02%20Title%20Theme.mp3", "station": "gaming"},
    {"title": "Main Theme (Bob-omb Battlefield)", "artist": "Koji Kondo", "source": "Super Mario 64", "url": "https://archive.org/download/super-mario-64-soundtrack/Super%20Mario%2064%20%28Soundtrack%29/1-05%20Super%20Mario%2064%20Main%20Theme.mp3", "station": "gaming"},
    {"title": "Inside The Castle Walls", "artist": "Koji Kondo", "source": "Super Mario 64", "url": "https://archive.org/download/super-mario-64-soundtrack/Super%20Mario%2064%20%28Soundtrack%29/1-07%20Inside%20The%20Castle%20Walls.mp3", "station": "gaming"},
    {"title": "Dire, Dire Docks (Water Theme)", "artist": "Koji Kondo", "source": "Super Mario 64", "url": "https://archive.org/download/super-mario-64-soundtrack/Super%20Mario%2064%20%28Soundtrack%29/1-09%20Dire%2C%20Dire%20Docks.mp3", "station": "gaming"},
    {"title": "Piranha Plant's Lullaby", "artist": "Koji Kondo", "source": "Super Mario 64", "url": "https://archive.org/download/super-mario-64-soundtrack/Super%20Mario%2064%20%28Soundtrack%29/1-15%20Piranha%20Plant%27s%20Lullaby.mp3", "station": "gaming"},

    # Hollow Knight (Christopher Larkin)
    {"title": "Enter Hallownest", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/01%20-%20Enter%20Hallownest.mp3", "station": "gaming"},
    {"title": "Dirtmouth", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/02%20-%20Dirtmouth.mp3", "station": "gaming"},
    {"title": "Greenpath", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/05%20-%20Greenpath.mp3", "station": "gaming"},
    {"title": "Hornet", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/06%20-%20Hornet.mp3", "station": "gaming"},
    {"title": "Reflection", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/07%20-%20Reflection.mp3", "station": "gaming"},
    {"title": "Mantis Lords", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/08%20-%20Mantis%20Lords.mp3", "station": "gaming"},
    {"title": "City of Tears", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/09%20-%20City%20of%20Tears.mp3", "station": "gaming"},
    {"title": "Resting Grounds", "artist": "Christopher Larkin", "source": "Hollow Knight", "url": "https://archive.org/download/official-hollow-knight-original-soundtrack/Hollow%20Knight%20-%20Official%20Soundtrack/15%20-%20Resting%20Grounds.mp3", "station": "gaming"},

    # Chrono Trigger (Yasunori Mitsuda)
    {"title": "Crono's Theme", "artist": "Yasunori Mitsuda", "source": "Chrono Trigger", "url": "https://archive.org/download/chrono-trigger-1995-ost/Chrono%20Trigger%20-%2002.%20Chrono%20Trigger%20%28Crono%27s%20Theme%29.mp3", "station": "gaming"},
    {"title": "Wind Scene (Yearnings of the Wind)", "artist": "Yasunori Mitsuda", "source": "Chrono Trigger", "url": "https://archive.org/download/chrono-trigger-1995-ost/Chrono%20Trigger%20-%2009.%20Yearnings%20of%20the%20Wind.mp3", "station": "gaming"},
    {"title": "Frog's Theme", "artist": "Yasunori Mitsuda", "source": "Chrono Trigger", "url": "https://archive.org/download/chrono-trigger-1995-ost/Chrono%20Trigger%20-%2019.%20Frog%27s%20Theme.mp3", "station": "gaming"},
    {"title": "Corridor of Time", "artist": "Yasunori Mitsuda", "source": "Chrono Trigger", "url": "https://archive.org/download/chrono-trigger-1995-ost/Chrono%20Trigger%20-%2049.%20Corridor%20of%20Time.mp3", "station": "gaming"},
    {"title": "Schala's Theme", "artist": "Yasunori Mitsuda", "source": "Chrono Trigger", "url": "https://archive.org/download/chrono-trigger-1995-ost/Chrono%20Trigger%20-%2051.%20Schala%27s%20Theme.mp3", "station": "gaming"},

    # Halo: Combat Evolved (Martin O'Donnell)
    {"title": "Opening Suite", "artist": "Martin O'Donnell", "source": "Halo: Combat Evolved", "url": "https://archive.org/download/halo-combat-evolved-20010101-ost/Halo%20Combat%20Evolved%20-%2002.%20Opening%20Suite.mp3", "station": "gaming"},
    {"title": "Main Theme", "artist": "Martin O'Donnell", "source": "Halo: Combat Evolved", "url": "https://archive.org/download/halo-combat-evolved-20010101-ost/Halo%20Combat%20Evolved%20-%2027.%20Main%20Theme.mp3", "station": "gaming"},
    {"title": "A Walk in the Woods", "artist": "Martin O'Donnell", "source": "Halo: Combat Evolved", "url": "https://archive.org/download/halo-combat-evolved-20010101-ost/Halo%20Combat%20Evolved%20-%2007.%20A%20Walk%20in%20the%20Woods.mp3", "station": "gaming"},

    # Pokemon Omega Ruby & Alpha Sapphire (Junichi Masuda / Go Ichinose)
    {"title": "Title Screen", "artist": "Junichi Masuda", "source": "Pokemon Omega Ruby & Alpha Sapphire", "url": "https://archive.org/download/pkmn-oras-ost/Disc%201/03%20-%20Title%20Screen.mp3", "station": "gaming"},
    {"title": "Littleroot Town", "artist": "Go Ichinose", "source": "Pokemon Omega Ruby & Alpha Sapphire", "url": "https://archive.org/download/pkmn-oras-ost/Disc%201/05%20-%20Littleroot%20Town.mp3", "station": "gaming"},
    {"title": "Surf", "artist": "Go Ichinose", "source": "Pokemon Omega Ruby & Alpha Sapphire", "url": "https://archive.org/download/pkmn-oras-ost/Disc%202/11%20-%20Surf.mp3", "station": "gaming"},
    {"title": "Sootopolis City", "artist": "Go Ichinose", "source": "Pokemon Omega Ruby & Alpha Sapphire", "url": "https://archive.org/download/pkmn-oras-ost/Disc%203/12%20-%20Sootopolis%20City.mp3", "station": "gaming"}
]

# Iconic cinema & anime soundtracks (Studio Ghibli, Interstellar, Star Wars)
CINEMA_TRACKS: List[Dict[str, str]] = [
    # Studio Ghibli (Joe Hisaishi)
    {"title": "One Summer Day", "artist": "Joe Hisaishi", "source": "Spirited Away (Studio Ghibli)", "url": "https://archive.org/download/spirited-away-ost/01%20One%20Summer%20Day.mp3", "station": "cinema"},
    {"title": "The Dragon Boy", "artist": "Joe Hisaishi", "source": "Spirited Away (Studio Ghibli)", "url": "https://archive.org/download/spirited-away-ost/05%20The%20Dragon%20Boy.mp3", "station": "cinema"},
    {"title": "Day of the River", "artist": "Joe Hisaishi", "source": "Spirited Away (Studio Ghibli)", "url": "https://archive.org/download/spirited-away-ost/10%20Day%20of%20the%20River.mp3", "station": "cinema"},
    {"title": "Opening: Merry-Go-Round of Life", "artist": "Joe Hisaishi", "source": "Howl's Moving Castle (Studio Ghibli)", "url": "https://archive.org/download/howls-moving-castle-ost/01%20Opening%20%28Merry-Go-Round%20of%20Life%29.mp3", "station": "cinema"},
    {"title": "Sky Stroll", "artist": "Joe Hisaishi", "source": "Howl's Moving Castle (Studio Ghibli)", "url": "https://archive.org/download/howls-moving-castle-ost/03%20Sky%20Stroll.mp3", "station": "cinema"},
    {"title": "To the Lake of Stars", "artist": "Joe Hisaishi", "source": "Howl's Moving Castle (Studio Ghibli)", "url": "https://archive.org/download/howls-moving-castle-ost/10%20To%20the%20Lake%20of%20Stars.mp3", "station": "cinema"},
    {"title": "Hey, Let's Go (Opening Theme)", "artist": "Joe Hisaishi", "source": "My Neighbor Totoro (Studio Ghibli)", "url": "https://archive.org/download/my-neighbor-totoro-ost/01%20Hey%2C%20Let%27s%20Go%20%28Opening%20Theme%29.mp3", "station": "cinema"},
    {"title": "The Village in May", "artist": "Joe Hisaishi", "source": "My Neighbor Totoro (Studio Ghibli)", "url": "https://archive.org/download/my-neighbor-totoro-ost/02%20The%20Village%20in%20May.mp3", "station": "cinema"},
    {"title": "The Legend of Ashitaka", "artist": "Joe Hisaishi", "source": "Princess Mononoke (Studio Ghibli)", "url": "https://archive.org/download/princess-mononoke-ost/01%20The%20Legend%20of%20Ashitaka.mp3", "station": "cinema"},
    {"title": "The Kodamas", "artist": "Joe Hisaishi", "source": "Princess Mononoke (Studio Ghibli)", "url": "https://archive.org/download/princess-mononoke-ost/07%20The%20Kodamas.mp3", "station": "cinema"},
    {"title": "Forest of the Gods", "artist": "Joe Hisaishi", "source": "Princess Mononoke (Studio Ghibli)", "url": "https://archive.org/download/princess-mononoke-ost/08%20Forest%20of%20the%20Gods.mp3", "station": "cinema"},

    # Hans Zimmer & John Williams
    {"title": "Interstellar Main Theme", "artist": "Hans Zimmer", "source": "Interstellar", "url": "https://archive.org/download/InterstellarMainThemeExtraExtendedSoundtrackByHansZimmer/Interstellar%20Main%20Theme%20-%20Extra%20Extended%20-%20Soundtrack%20by%20Hans%20Zimmer.mp3", "station": "cinema"},
    {"title": "The Imperial March", "artist": "John Williams", "source": "Star Wars", "url": "https://archive.org/download/StarWarsImperialMarch2SoundtrackNewVersion/Star%20Wars%20-%20Imperial%20March%202%20Soundtrack%20New%20Version.mp3", "station": "cinema"}
]

STATIONS = {
    "lofi": {
        "name": "☕ Lofi Chill Beats",
        "description": "Chill, non-lyrical study & relaxation beats from lofi.radio",
        "genre": "100% Non-Lyrical Chill & Study Beats",
        "thumbnail": "https://lofi.radio/lofiradio.png",
        "color": discord.Color.from_rgb(0, 209, 178),
    },
    "gaming": {
        "name": "🎮 Iconic Gaming Themes",
        "description": "Legendary ambient & orchestral themes from iconic video games",
        "genre": "Iconic Video Game Soundtracks & Melodies",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Video_game_controller_icon_designed_by_Maico_Amorim.svg/512px-Video_game_controller_icon_designed_by_Maico_Amorim.svg.png",
        "color": discord.Color.from_rgb(114, 137, 218),
    },
    "cinema": {
        "name": "🎬 Cinema & Anime Themes",
        "description": "Studio Ghibli, Hans Zimmer, Star Wars & cinematic masterpieces",
        "genre": "Iconic Cinematic & Anime Orchestral Themes",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Filmroll.svg/512px-Filmroll.svg.png",
        "color": discord.Color.from_rgb(235, 69, 158),
    },
    "all": {
        "name": "🔀 All-in-One Shuffle",
        "description": "Seamless continuous shuffle across Lofi, Gaming, and Cinema themes",
        "genre": "Complete Multi-Station Shuffle Experience",
        "thumbnail": "https://lofi.radio/lofiradio.png",
        "color": discord.Color.gold(),
    }
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class StationSelect(discord.ui.Select):
    def __init__(self, current_station: str = "lofi"):
        options = [
            discord.SelectOption(
                label="Lofi Beats",
                value="lofi",
                description="224+ chill study & relaxation beats from lofi.radio",
                emoji="☕",
                default=(current_station == "lofi")
            ),
            discord.SelectOption(
                label="Gaming Themes",
                value="gaming",
                description="Minecraft, Zelda, Undertale, Mario, Hollow Knight...",
                emoji="🎮",
                default=(current_station == "gaming")
            ),
            discord.SelectOption(
                label="Cinema & Anime",
                value="cinema",
                description="Studio Ghibli, Interstellar, Star Wars themes",
                emoji="🎬",
                default=(current_station == "cinema")
            ),
            discord.SelectOption(
                label="All-in-One Shuffle",
                value="all",
                description="Shuffles all tracks across every station",
                emoji="🔀",
                default=(current_station == "all")
            )
        ]
        super().__init__(placeholder="📻 Switch Radio Station...", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        selected_station = self.values[0]
        guild_id = interaction.guild.id
        await interaction.response.defer()
        # pyrefly: ignore
        await self.view.music_cog.switch_station(guild_id, selected_station, interaction=interaction)


class RadioPlayerUI(discord.ui.View):
    def __init__(self, music_cog, current_station: str = "lofi"):
        super().__init__(timeout=None)
        self.music_cog = music_cog
        self.current_station = current_station
        self.add_item(StationSelect(current_station=current_station))

    @discord.ui.button(label="⏯️ Play/Pause", style=discord.ButtonStyle.primary, custom_id="lofi_play_pause", row=1)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("Radio is not playing right now.", ephemeral=True)

        guild_id = interaction.guild.id
        if vc.is_playing():
            vc.pause()
        elif vc.is_paused():
            vc.resume()
        else:
            return await interaction.response.send_message("Radio is currently loading next track.", ephemeral=True)

        current = self.music_cog.current_song.get(guild_id, {"title": "Melody"})
        embed = self.music_cog.create_player_embed(guild_id, current)
        station_key = self.music_cog.current_station.get(guild_id, "lofi")
        view = RadioPlayerUI(self.music_cog, current_station=station_key)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="⏭️ Next Melody", style=discord.ButtonStyle.secondary, custom_id="lofi_skip", row=1)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("Radio is not playing right now.", ephemeral=True)

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel: # pyrefly: ignore
            return await interaction.response.send_message("You must be in the same voice channel to skip.", ephemeral=True)

        guild_id = interaction.guild.id
        now = time.time()
        last_skip = self.music_cog.last_skip.get(guild_id, 0)
        if now - last_skip < 2.0:
            return await interaction.response.send_message("⏳ Buffering next melody, please wait a moment!", ephemeral=True)

        self.music_cog.last_skip[guild_id] = now
        await interaction.response.send_message("⏭️ Tuned to the next melody.", ephemeral=True)
        vc.stop() # Triggers play_next_song which edits the single session message!

    @discord.ui.button(label="🔀 Shuffle", style=discord.ButtonStyle.secondary, custom_id="lofi_shuffle", row=1)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("Radio is not active.", ephemeral=True)

        guild_id = interaction.guild.id
        queue = self.music_cog.queues.get(guild_id, [])
        random.shuffle(queue)
        await interaction.response.send_message(f"🔀 Shuffled {len(queue)} upcoming melodies!", ephemeral=True)
        current = self.music_cog.current_song.get(guild_id, {"title": "Melody"})
        embed = self.music_cog.create_player_embed(guild_id, current)
        try:
            if interaction.message:
                station_key = self.music_cog.current_station.get(guild_id, "lofi")
                view = RadioPlayerUI(self.music_cog, current_station=station_key)
                await interaction.message.edit(embed=embed, view=view)
        except Exception:
            pass

    @discord.ui.button(label="🔉 Vol -", style=discord.ButtonStyle.secondary, custom_id="lofi_vol_down", row=1)
    async def vol_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        current_vol = self.music_cog.volumes.get(guild_id, 0.35)
        new_vol = max(0.05, round(current_vol - 0.10, 2))
        self.music_cog.volumes[guild_id] = new_vol

        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = new_vol

        current = self.music_cog.current_song.get(guild_id, {"title": "Melody"})
        embed = self.music_cog.create_player_embed(guild_id, current)
        station_key = self.music_cog.current_station.get(guild_id, "lofi")
        view = RadioPlayerUI(self.music_cog, current_station=station_key)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🔊 Vol +", style=discord.ButtonStyle.secondary, custom_id="lofi_vol_up", row=1)
    async def vol_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        current_vol = self.music_cog.volumes.get(guild_id, 0.35)
        new_vol = min(1.0, round(current_vol + 0.10, 2))
        self.music_cog.volumes[guild_id] = new_vol

        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = new_vol

        current = self.music_cog.current_song.get(guild_id, {"title": "Melody"})
        embed = self.music_cog.create_player_embed(guild_id, current)
        station_key = self.music_cog.current_station.get(guild_id, "lofi")
        view = RadioPlayerUI(self.music_cog, current_station=station_key)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="⏹️ Stop & Leave", style=discord.ButtonStyle.danger, custom_id="lofi_stop", row=2)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc:
            return await interaction.response.send_message("Radio is not playing.", ephemeral=True)

        guild_id = interaction.guild.id
        self.music_cog.intentional_leaves.add(guild_id)
        self.music_cog.active_voice_channels.pop(guild_id, None)
        if guild_id:
            self.music_cog.queues[guild_id] = []
        vc.stop()
        await vc.disconnect()

        embed = discord.Embed(
            title="📻 24/7 Radio • Session Ended",
            description="The radio stream has ended. Thank you for listening!\nUse `f#radio` to start a new soothing session anytime.",
            color=discord.Color.dark_grey()
        )
        embed.set_footer(text="Femboys Bot • 24/7 Multi-Station Radio", icon_url=self.music_cog.bot.user.display_avatar.url if self.music_cog.bot.user else None)
        await interaction.response.edit_message(embed=embed, view=None)
        self.music_cog.player_messages.pop(guild_id, None)


class QueuePaginationView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


class Music(commands.Cog):
    """Direct 24/7 Multi-Station Radio Cog (Streaming 280+ Curated Melodies: Lofi, Gaming Themes & Cinema)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: Dict[int, List[Any]] = {}
        self.history: Dict[int, List[Any]] = {}
        self.current_song: Dict[int, Any] = {}
        self.current_station: Dict[int, str] = {}
        self.volumes: Dict[int, float] = {}
        self.text_channels: Dict[int, discord.abc.Messageable] = {}
        self.player_messages: Dict[int, discord.Message] = {}
        self.last_skip: Dict[int, float] = {}
        self.stay_connected: Dict[int, bool] = {}
        self.intentional_leaves: Set[int] = set()
        self.active_voice_channels: Dict[int, int] = {}
        self.reconnecting_guilds: Set[int] = set()

    async def cog_load(self):
        self.radio_watchdog.start()

    async def cog_unload(self):
        self.radio_watchdog.cancel()

    def create_embed(self, title: str, description: str = "", color: discord.Color = discord.Color.blurple()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Femboys Bot • 24/7 Radio", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
        return embed

    # ==================== TRACK METADATA HELPERS ====================

    def get_song_title(self, track: Any) -> str:
        """Returns clean song title."""
        if isinstance(track, dict):
            return track.get("title", "Melody")
        if isinstance(track, str):
            return track[:-4] if track.endswith(".mp3") else track
        return str(track)

    def get_song_url(self, track: Any) -> str:
        """Returns direct high-speed audio stream URL."""
        if isinstance(track, dict):
            return track.get("url", "")
        if isinstance(track, str):
            quoted = urllib.parse.quote(track)
            return f"https://lofi.radio/songs/{quoted}"
        return ""

    def get_song_artist(self, track: Any) -> str:
        """Returns track artist."""
        if isinstance(track, dict):
            return track.get("artist", "Purrple Cat")
        return "Purrple Cat"

    def get_song_source(self, track: Any) -> str:
        """Returns soundtrack / source name."""
        if isinstance(track, dict):
            return track.get("source", "lofi.radio")
        return "lofi.radio"

    def get_song_station(self, track: Any) -> str:
        """Returns track station category."""
        if isinstance(track, dict):
            return track.get("station", "lofi")
        return "lofi"

    def get_station_tracks(self, station_key: str) -> List[Dict[str, str]]:
        """Returns track list for a given station."""
        if station_key == "gaming":
            return list(GAMING_TRACKS)
        elif station_key == "cinema":
            return list(CINEMA_TRACKS)
        elif station_key == "all":
            return list(LOFI_TRACKS) + list(GAMING_TRACKS) + list(CINEMA_TRACKS)
        else: # default "lofi"
            return list(LOFI_TRACKS)

    def ensure_queue(self, guild_id: int):
        """Ensures the guild has a randomized upcoming queue for its active station."""
        q = self.queues.setdefault(guild_id, [])
        station = self.current_station.get(guild_id, "lofi")
        if len(q) < 5:
            fresh_batch = self.get_station_tracks(station)
            random.shuffle(fresh_batch)
            q.extend(fresh_batch)

    async def switch_station(self, guild_id: int, station_key: str, interaction: Optional[discord.Interaction] = None):
        """Switches the active station for a guild and immediately begins playing from it."""
        if station_key not in STATIONS:
            return

        self.current_station[guild_id] = station_key
        fresh_batch = self.get_station_tracks(station_key)
        random.shuffle(fresh_batch)
        self.queues[guild_id] = fresh_batch

        guild = self.bot.get_guild(guild_id)
        vc: Optional[discord.VoiceClient] = guild.voice_client if guild else None # pyrefly: ignore

        if vc and vc.is_connected():
            if vc.is_playing() or vc.is_paused():
                vc.stop() # Triggers play_next_song which plays new station track & edits embed!
            else:
                self.play_next_song(guild_id)
        else:
            current = self.current_song.get(guild_id)
            if current:
                await self.update_player_message(guild_id, current)

    # ==================== PLAYER UI EMBED ====================

    def create_player_embed(self, guild_id: int, track: Any) -> discord.Embed:
        title = self.get_song_title(track)
        song_url = self.get_song_url(track)
        artist = self.get_song_artist(track)
        source = self.get_song_source(track)
        station_key = self.current_station.get(guild_id, "lofi")
        station_info = STATIONS.get(station_key, STATIONS["lofi"])

        vol_pct = int(self.volumes.get(guild_id, 0.35) * 100)
        remaining = len(self.queues.get(guild_id, []))

        guild = self.bot.get_guild(guild_id)
        vc: Optional[discord.VoiceClient] = guild.voice_client if guild else None # pyrefly: ignore
        is_paused = vc.is_paused() if vc else False
        status_text = "⏸️ Stream Paused" if is_paused else "▶️ Streaming Live (24/7)"

        embed = discord.Embed(
            title=f"📻 {station_info['name']} • Now Playing",
            description=f"### 🎵 [{title}]({song_url})\n"
                        f"👤 **Artist:** {artist}\n"
                        f"🏷️ **Source / OST:** {source}\n"
                        f"✨ **Genre:** {station_info['genre']}\n\n"
                        f"━🔘━━━━━━━━━━ `{status_text}`",
            color=station_info["color"]
        )
        embed.set_thumbnail(url=station_info["thumbnail"])
        embed.add_field(
            name="📊 Radio Status",
            value=f"📻 **Station:** {station_info['name']}\n"
                  f"🔊 **Volume:** {vol_pct}%\n"
                  f"🔀 **Remaining in Queue:** {remaining} tracks\n"
                  f"🕒 **24/7 Mode:** {'Enabled ✅' if self.stay_connected.get(guild_id, True) else 'Disabled ❌'}",
            inline=True
        )
        embed.add_field(
            name="☕ Stations & Modes",
            value="Switch anytime using the dropdown below or `f#station <name>`:\n"
                  "• `☕ lofi` - Study & Chill\n"
                  "• `🎮 gaming` - Iconic Game Themes\n"
                  "• `🎬 cinema` - Ghibli & Movie Themes\n"
                  "• `🔀 all` - Shuffle Everything",
            inline=True
        )
        embed.set_footer(
            text="Single Session Stream • 24/7 Multi-Station Radio",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        return embed

    async def update_player_message(self, guild_id: int, track: Any):
        """Updates the persistent single session message for this guild."""
        channel = self.text_channels.get(guild_id)
        if not channel:
            guild = self.bot.get_guild(guild_id)
            if guild:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        self.text_channels[guild_id] = ch
                        break

        if not channel:
            return

        station_key = self.current_station.get(guild_id, "lofi")
        embed = self.create_player_embed(guild_id, track)
        view = RadioPlayerUI(self, current_station=station_key)

        existing_msg = self.player_messages.get(guild_id)
        if existing_msg:
            try:
                await existing_msg.edit(embed=embed, view=view)
                return
            except discord.NotFound:
                self.player_messages.pop(guild_id, None)
            except discord.HTTPException as e:
                print(f"[RADIO] Failed to edit existing player message: {e}")
                self.player_messages.pop(guild_id, None)

        try:
            msg = await channel.send(embed=embed, view=view)
            self.player_messages[guild_id] = msg
        except Exception as e:
            print(f"[RADIO] Failed to send Player UI: {e}")

    async def cleanup_session(self, guild_id: int):
        """Edits the single session message to ended state when the bot leaves or stops."""
        msg = self.player_messages.pop(guild_id, None)
        if msg:
            try:
                embed = discord.Embed(
                    title="📻 24/7 Radio • Session Ended",
                    description="The radio stream has ended. Thank you for listening!\nUse `f#radio` to start a new session anytime.",
                    color=discord.Color.dark_grey()
                )
                embed.set_footer(text="Femboys Bot • 24/7 Multi-Station Radio", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
                await msg.edit(embed=embed, view=None)
            except Exception:
                pass

    def play_next_song(self, guild_id: int):
        """Plays the next melody from the active station queue and updates the single session message."""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        vc: Optional[discord.VoiceClient] = guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            # If 24/7 mode is on and not intentionally left, retry in 3 seconds to recover from momentary reconnects
            if self.stay_connected.get(guild_id, True) and guild_id not in self.intentional_leaves:
                self.bot.loop.call_later(3.0, self.play_next_song, guild_id)
            return

        if vc.is_playing() or vc.is_paused():
            return

        self.ensure_queue(guild_id)
        next_track = self.queues[guild_id].pop(0)
        self.current_song[guild_id] = next_track

        hist = self.history.setdefault(guild_id, [])
        hist.append(next_track)
        if len(hist) > 30:
            hist.pop(0)

        url = self.get_song_url(next_track)
        vol = self.volumes.get(guild_id, 0.35)

        try:
            audio_source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            vol_source = discord.PCMVolumeTransformer(audio_source, volume=vol)

            def after_play(error):
                if error:
                    print(f"[RADIO] Playback error for {self.get_song_title(next_track)}: {error}")
                # Slight 0.5s delay avoids busy looping on immediate stream or decode failures
                self.bot.loop.call_later(0.5, self.play_next_song, guild_id)

            vc.play(vol_source, after=after_play)
            print(f"\033[32m[RADIO] 🎵 Now Playing:\033[0m {self.get_song_title(next_track)} ({self.get_song_source(next_track)}) in {guild.name}")

            # Update the single session message
            self.bot.loop.create_task(self.update_player_message(guild_id, next_track))
        except discord.ClientException as e:
            if "Already playing" in str(e):
                return
            print(f"[RADIO] ClientException while playing {self.get_song_title(next_track)}: {e}")
            self.bot.loop.call_later(1.0, self.play_next_song, guild_id)
        except Exception as e:
            print(f"[RADIO] Failed to play {self.get_song_title(next_track)}: {e}")
            self.bot.loop.call_later(1.0, self.play_next_song, guild_id)

    # ==================== VOICE STATE LISTENER & WATCHDOG ====================

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        guild = member.guild
        guild_id = guild.id

        # Keep track of active voice channel whenever connected
        if after.channel is not None:
            self.active_voice_channels[guild_id] = after.channel.id

        # Intentional leave handling (e.g. via f#stop or UI Stop button)
        if guild_id in self.intentional_leaves:
            if after.channel is None:
                self.intentional_leaves.discard(guild_id)
                self.active_voice_channels.pop(guild_id, None)
                await self.cleanup_session(guild_id)
            return

        # If bot was moved between voice channels
        if before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            vc: Optional[discord.VoiceClient] = guild.voice_client # pyrefly: ignore
            if vc and vc.is_connected() and not vc.is_playing() and not vc.is_paused():
                self.play_next_song(guild_id)
            return

        # If disconnected unexpectedly, handle 24/7 recovery
        if before.channel is not None and after.channel is None:
            if not self.stay_connected.get(guild_id, True):
                self.active_voice_channels.pop(guild_id, None)
                await self.cleanup_session(guild_id)
                return

            # Debounce: prevent multiple concurrent rejoin routines for the same guild
            if guild_id in self.reconnecting_guilds:
                return

            self.reconnecting_guilds.add(guild_id)
            target_channel = before.channel

            try:
                print(f"[RADIO] Disconnected from {target_channel.name}. Checking auto-rejoin in 2 seconds (24/7 mode)...")
                await asyncio.sleep(2)

                # Check if discord.py already reconnected automatically in background
                vc: Optional[discord.VoiceClient] = guild.voice_client # pyrefly: ignore
                if vc and vc.is_connected():
                    print(f"[RADIO] Already connected to {vc.channel.name}. Resuming radio...")
                    if not vc.is_playing() and not vc.is_paused():
                        self.play_next_song(guild_id)
                    return

                # If a stale or broken voice_client exists, cleanly detach it before connecting
                if vc:
                    try:
                        await vc.disconnect(force=True)
                    except Exception:
                        pass

                # Connect cleanly
                try:
                    new_vc = await target_channel.connect(timeout=20.0, reconnect=True)
                    self.active_voice_channels[guild_id] = target_channel.id
                    if not new_vc.is_playing() and not new_vc.is_paused():
                        self.play_next_song(guild_id)
                except discord.ClientException:
                    # 'Already connected' — verify existing client and start playback
                    current_vc: Optional[discord.VoiceClient] = guild.voice_client # pyrefly: ignore
                    if current_vc and current_vc.is_connected():
                        if not current_vc.is_playing() and not current_vc.is_paused():
                            self.play_next_song(guild_id)
                except Exception as e:
                    print(f"[RADIO] Auto-rejoin failed: {e}")
            finally:
                self.reconnecting_guilds.discard(guild_id)

    @tasks.loop(seconds=10)
    async def radio_watchdog(self):
        """Monitors all 24/7 radio sessions and self-heals any stalled audio or dropped connections."""
        for guild_id, is_247 in list(self.stay_connected.items()):
            if not is_247 or guild_id in self.intentional_leaves:
                continue

            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            vc: Optional[discord.VoiceClient] = guild.voice_client # pyrefly: ignore

            # 1. Bot is in VC and connected, but audio stalled (neither playing nor paused)
            if vc and vc.is_connected():
                if not vc.is_playing() and not vc.is_paused():
                    print(f"[RADIO-WATCHDOG] Detected idle radio in {guild.name}. Resuming stream...")
                    self.play_next_song(guild_id)

            # 2. Bot was supposed to stay 24/7, but disconnected from voice channel
            elif not vc or not vc.is_connected():
                channel_id = self.active_voice_channels.get(guild_id)
                if channel_id and guild_id not in self.reconnecting_guilds:
                    channel = guild.get_channel(channel_id)
                    if isinstance(channel, discord.VoiceChannel):
                        print(f"[RADIO-WATCHDOG] Reconnecting 24/7 stream to {channel.name} in {guild.name}...")
                        self.reconnecting_guilds.add(guild_id)
                        try:
                            if vc:
                                try:
                                    await vc.disconnect(force=True)
                                except Exception:
                                    pass
                            new_vc = await channel.connect(timeout=20.0, reconnect=True)
                            self.play_next_song(guild_id)
                        except Exception as e:
                            print(f"[RADIO-WATCHDOG] Reconnect failed: {e}")
                        finally:
                            self.reconnecting_guilds.discard(guild_id)

    @radio_watchdog.before_loop
    async def before_watchdog(self):
        await self.bot.wait_until_ready()

    # ==================== BOT COMMANDS ====================

    @commands.command(name="radio", help="Starts the 24/7 multi-station radio stream.", aliases=["join", "start", "play", "p"])
    async def radio_command(self, ctx, *, station: Optional[str] = None):
        """Summons the bot and begins streaming non-stop melodies (Lofi, Gaming, or Cinema)."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(embed=self.create_embed("❌ Voice Channel Required", "Please join a voice channel first to start the radio!", discord.Color.red()), delete_after=10)

        guild_id = ctx.guild.id

        # If a station name was provided in the command, match and activate it
        if station:
            st = station.strip().lower()
            if st in ("lofi", "chill", "study", "beats"):
                self.current_station[guild_id] = "lofi"
            elif st in ("gaming", "games", "game", "ost", "minecraft", "zelda", "undertale"):
                self.current_station[guild_id] = "gaming"
            elif st in ("cinema", "movie", "movies", "anime", "ghibli", "film"):
                self.current_station[guild_id] = "cinema"
            elif st in ("all", "shuffle", "mix", "everything"):
                self.current_station[guild_id] = "all"
        else:
            self.current_station.setdefault(guild_id, "lofi")

        vc_target = ctx.author.voice.channel
        self.text_channels[guild_id] = ctx.channel
        self.stay_connected[guild_id] = True # Default 24/7
        self.active_voice_channels[guild_id] = vc_target.id
        self.intentional_leaves.discard(guild_id)

        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore

        if not vc or not vc.is_connected():
            station_info = STATIONS.get(self.current_station[guild_id], STATIONS["lofi"])
            msg = await ctx.send(embed=self.create_embed("📻 Connecting...", f"Connecting to {vc_target.mention} and tuning into **{station_info['name']}**...", discord.Color.blue()))
            try:
                vc = await vc_target.connect(timeout=20.0, reconnect=True)
                self.player_messages[guild_id] = msg
            except Exception as e:
                return await msg.edit(embed=self.create_embed("❌ Connection Failed", f"Could not connect to {vc_target.mention}: {e}", discord.Color.red()))
        elif vc.channel.id != vc_target.id:
            await vc.move_to(vc_target)

        # If not playing, start radio immediately
        if not vc.is_playing() and not vc.is_paused():
            self.ensure_queue(guild_id)
            self.play_next_song(guild_id)
        else:
            current = self.current_song.get(guild_id, {"title": "Melody"})
            await self.update_player_message(guild_id, current)

        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="station", help="Switches radio station or lists available stations.", aliases=["stations", "mode"])
    async def station_command(self, ctx, *, station_name: Optional[str] = None):
        """Displays available stations or switches to a chosen station (lofi, gaming, cinema, all)."""
        guild_id = ctx.guild.id
        if not station_name:
            current = self.current_station.get(guild_id, "lofi")
            embed = discord.Embed(
                title="📻 Available Radio Stations",
                description="Choose a station to stream continuous music 24/7!\nSwitch using `f#station <name>` or via the dropdown on the player card.",
                color=discord.Color.from_rgb(0, 209, 178)
            )
            for key, info in STATIONS.items():
                track_count = len(self.get_station_tracks(key))
                is_active = " 🌟 **[Active]**" if key == current else ""
                embed.add_field(
                    name=f"{info['name']}{is_active}",
                    value=f"• **Command:** `f#station {key}`\n"
                          f"• **Description:** {info['description']}\n"
                          f"• **Tracks:** {track_count} curated tracks",
                    inline=False
                )
            embed.set_footer(text="Femboys Bot • Multi-Station 24/7 Radio", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
            return await ctx.send(embed=embed, delete_after=30)

        st = station_name.strip().lower()
        matched = None
        if st in ("lofi", "chill", "study", "beats"):
            matched = "lofi"
        elif st in ("gaming", "games", "game", "ost", "minecraft", "zelda", "undertale"):
            matched = "gaming"
        elif st in ("cinema", "movie", "movies", "anime", "ghibli", "film"):
            matched = "cinema"
        elif st in ("all", "shuffle", "mix", "everything"):
            matched = "all"

        if not matched:
            return await ctx.send(embed=self.create_embed("❌ Unknown Station", f"Could not find station `{station_name}`.\nAvailable stations: `lofi`, `gaming`, `cinema`, `all`.", discord.Color.red()), delete_after=8)

        await self.switch_station(guild_id, matched)
        info = STATIONS[matched]
        await ctx.send(embed=self.create_embed("📻 Station Switched", f"Tuned into **{info['name']}**!\n{info['description']}", info['color']), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="next", help="Skips to the next melody.", aliases=["skip", "s"])
    async def next_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not playing.", discord.Color.red()), delete_after=5)

        vc.stop() # Triggers play_next_song which edits the single session message
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="previous", help="Replays the previous melody from history.", aliases=["prev"])
    async def prev_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not playing.", discord.Color.red()), delete_after=5)

        guild_id = ctx.guild.id
        hist = self.history.get(guild_id, [])
        if len(hist) < 2:
            return await ctx.send(embed=self.create_embed("❌ Error", "No previous melody in history.", discord.Color.red()), delete_after=5)

        # Put current song back to front of queue
        current = self.current_song.get(guild_id)
        if current:
            self.queues.setdefault(guild_id, []).insert(0, current)

        hist.pop()
        prev_song = hist.pop()
        self.queues[guild_id].insert(0, prev_song)
        vc.stop()
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="shuffle", help="Shuffles upcoming melodies in the active station.")
    async def shuffle_command(self, ctx):
        guild_id = ctx.guild.id
        self.ensure_queue(guild_id)
        random.shuffle(self.queues[guild_id])
        current = self.current_song.get(guild_id, {"title": "Melody"})
        await self.update_player_message(guild_id, current)
        await ctx.send(embed=self.create_embed("🔀 Shuffled", f"Randomized {len(self.queues[guild_id])} upcoming melodies!", discord.Color.green()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="pause", help="Pauses the radio stream.")
    async def pause_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not active.", discord.Color.red()), delete_after=5)

        if vc.is_playing():
            vc.pause()
            current = self.current_song.get(ctx.guild.id, {"title": "Melody"})
            await self.update_player_message(ctx.guild.id, current)
            await ctx.send(embed=self.create_embed("⏸️ Paused", "Paused the radio stream.", discord.Color.gold()), delete_after=5)
        else:
            await ctx.send(embed=self.create_embed("ℹ️ Already Paused", "Radio is already paused.", discord.Color.gold()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="resume", help="Resumes the paused radio stream.")
    async def resume_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not active.", discord.Color.red()), delete_after=5)

        if vc.is_paused():
            vc.resume()
            current = self.current_song.get(ctx.guild.id, {"title": "Melody"})
            await self.update_player_message(ctx.guild.id, current)
            await ctx.send(embed=self.create_embed("▶️ Resumed", "Resumed the radio stream.", discord.Color.green()), delete_after=5)
        else:
            await ctx.send(embed=self.create_embed("ℹ️ Already Playing", "Radio is already playing.", discord.Color.green()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="volume", help="Adjusts radio volume (1-100%).", aliases=["vol", "v"])
    async def volume_command(self, ctx, volume: int):
        volume = max(1, min(100, volume))
        guild_id = ctx.guild.id
        vol_float = volume / 100.0
        self.volumes[guild_id] = vol_float

        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = vol_float

        current = self.current_song.get(guild_id, {"title": "Melody"})
        await self.update_player_message(guild_id, current)
        await ctx.send(embed=self.create_embed("🔊 Volume", f"Radio volume set to **{volume}%**.", discord.Color.blue()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="nowplaying", help="Focuses or refreshes the single session player message.", aliases=["np"])
    async def nowplaying_command(self, ctx):
        guild_id = ctx.guild.id
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected() or guild_id not in self.current_song:
            return await ctx.send(embed=self.create_embed("ℹ️ Radio Offline", "The radio is not currently playing. Use `f#radio` to tune in!", discord.Color.gold()), delete_after=8)

        self.text_channels[guild_id] = ctx.channel
        await self.update_player_message(guild_id, self.current_song[guild_id])
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="queue", help="Shows upcoming melodies in the active station.", aliases=["q"])
    async def queue_command(self, ctx):
        guild_id = ctx.guild.id
        self.ensure_queue(guild_id)
        tracks = self.queues[guild_id]
        station_key = self.current_station.get(guild_id, "lofi")
        station_info = STATIONS.get(station_key, STATIONS["lofi"])

        per_page = 8
        chunks = [tracks[i:i + per_page] for i in range(0, min(len(tracks), 40), per_page)]

        embeds = []
        for page_idx, chunk in enumerate(chunks):
            lines = [f"**Station:** {station_info['name']} • **Upcoming Rotation:**\n"]
            for idx, track in enumerate(chunk):
                item_num = page_idx * per_page + idx + 1
                title = self.get_song_title(track)
                url = self.get_song_url(track)
                artist = self.get_song_artist(track)
                source = self.get_song_source(track)
                lines.append(f"`{item_num}.` **[{title}]({url})** — *{artist} ({source})*")

            embed = discord.Embed(
                title=f"📻 Upcoming Melodies (Page {page_idx + 1}/{len(chunks)})",
                description="\n".join(lines),
                color=station_info["color"]
            )
            embed.set_footer(text=f"Station: {station_info['name']} • Total in station: {len(self.get_station_tracks(station_key))} tracks")
            embeds.append(embed)

        if not embeds:
            return await ctx.send(embed=self.create_embed("ℹ️ Queue Empty", "No upcoming melodies in queue.", discord.Color.gold()), delete_after=5)

        if len(embeds) == 1:
            await ctx.send(embed=embeds[0], delete_after=60)
        else:
            view = QueuePaginationView(embeds)
            await ctx.send(embed=embeds[0], view=view, delete_after=60)

    @commands.command(name="247", help="Toggles 24/7 continuous stream mode.")
    async def toggle_247(self, ctx):
        current = self.stay_connected.get(ctx.guild.id, True)
        self.stay_connected[ctx.guild.id] = not current
        status = "Enabled ✅" if self.stay_connected[ctx.guild.id] else "Disabled ❌"
        current_song = self.current_song.get(ctx.guild.id, {"title": "Melody"})
        await self.update_player_message(ctx.guild.id, current_song)
        await ctx.send(embed=self.create_embed("🕒 24/7 Radio Mode", f"24/7 continuous stream is now **{status}**.", discord.Color.gold()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="stop", help="Stops radio and leaves the voice channel.", aliases=["leave", "dc", "disconnect"])
    async def stop_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc:
            return await ctx.send(embed=self.create_embed("ℹ️ Not Connected", "The bot is not in a voice channel.", discord.Color.gold()), delete_after=5)

        guild_id = ctx.guild.id
        self.intentional_leaves.add(guild_id)
        self.active_voice_channels.pop(guild_id, None)
        if guild_id:
            self.queues[guild_id] = []
        vc.stop()
        await vc.disconnect()
        await self.cleanup_session(guild_id)
        try:
            await ctx.message.delete()
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
