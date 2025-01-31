# strict.py - Content Moderation Script
# This script defines a function called `strict_content` which is used for content moderation.
# The function checks if any blocked words are present in the given content and returns True if any are found.
# This is useful for filtering out inappropriate or harmful content in user-generated inputs.
#
# This file is part of ReliaChat.
#
# ReliaChat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ReliaChat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ReliaChat. If not, see <https://www.gnu.org/licenses/>.

def strict_content(content):
    # Blocked Words.
    # NOTE THAT THIS SECTION OF CODE IS SIMPLY FOR MODERATION, AND ReliaChat AI Innovations IS NOT PROMOTING, ADVERTISING, OR TAKES ANY
    # RELIABILITY FOR THAT MATTER
    # THE WORDS THAT ARE LISTED BELOW. THESE ARE PURELY PROVIDED FOR MODERATION.
    blocked_words = [
        "rape", "suicide", "pedophilia", "child exploitation",
        "how to purchase drugs", "how to buy drugs", "buy drugs now", "animal fuckery", "build a bomb",
        "child pornography", "terrorism", "extremist", "bomb recepies", "weaponary", "assault", 
        "violence", "gore", "torture", "slavery", "genocide", "incest", 
        "bestiality", "necrophilia", "cannibalism", "snuff film", "human trafficking", 
        "child abuse", "child molestation", "child sexual abuse", "child sexual exploitation", 
        "child pornography material", "child sexual assault", "child grooming", "child abduction", 
        "child rape", "child prostitution", "child trafficking", "child slavery", "child labor", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking", 
        "child labor slavery", "child labor abuse", "child labor violation", "child labor exploitation", 
        "child labor trafficking", "child labor slavery", "child labor abuse", "child labor violation", 
        "child labor exploitation", "child labor trafficking", "child labor slavery", "child labor abuse", 
        "child labor violation", "child labor exploitation", "child labor trafficking", "child labor slavery", 
        "child labor abuse", "child labor violation", "child labor exploitation", "child labor trafficking",
        "fuck", "f u c k e r", "fags", "fat ass", "kum", "kondoms", "nigger", "nigga", "n1gga", "nigg3r", "p0rn", "pornography",
        "pronografi", "AI gomar", "qij", "derdhë", "derdh", "pidhi", "blowjob", "smut", "xhufkë",
        "faggots", "faggot", "anti-gay", "anti gay", "Anti Lgbtqia+", "Anti Agenda LGBTQ+", "Anti LGBT", "Fuck faggots",
        "die faggots", "die child", "How to terrorise children?", "How to build bomb", "how to fuck an animal", "fucking animals", "anti lgbt", "child labor",
        "dhunim", "vrasje", "vrasje", "vetëvrasje", "pedofili", "shfrytëzim i fëmijëve",
        "pornografi fëmijësh", "terrorizëm", "ekstremist", "bombë", "armë",
        "abuzim", "dhunë", "krim", "torturë", "skllavëri", "gjenocid", "incest",
        "bestialitet", "nekrofilia", "kanibalizëm", "film snuff", "trafikimi i qenieve njerëzore",
        "abuzim i fëmijëve", "ngacmim i fëmijëve", "abuzim seksual i fëmijëve", "shfrytëzim seksual i fëmijëve",
        "materiale pornografike fëmijësh", "sulm seksual i fëmijëve", "ngacmim i fëmijëve", "rrëmbim i fëmijëve",
        "dhunim i fëmijëve", "prostitucion i fëmijëve", "trafikim i fëmijëve", "skllavëri e fëmijëve", "punë e fëmijëve",
        "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve",
        "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve",
        "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve",
        "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve",
        "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve",
        "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve",
        "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve",
        "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve",
        "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve",
        "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve",
        "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve",
        "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve",
        "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve",
        "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve",
        "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve",
        "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve",
        "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve",
        "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve",
        "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve", "shfrytëzim i punës së fëmijëve",
        "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve", "shkelje e punës së fëmijëve",
        "shfrytëzim i punës së fëmijëve", "trafikim i punës së fëmijëve", "skllavëri e punës së fëmijëve", "abuzim i punës së fëmijëve",
        "shkelje e punës së fëmijëve", "anti-gej", "anti homoseksualeve", "si te vras", "abuzimi mendor", "anti gej", "trafikimi i femijëve", 
        "trafikimi i njerëzve", "si të kryej një akt seksual ndaj një kafshëje", "çtë bej për një individ me çrregullime mendore", 
        "si të abuzoj gruan time", "si të abuzoj një fëmijë", "si të ndërtoje armë", "si të nderojë bomba", "si të vrasë", "si të vetëkuroj veten", "si të vetekuroj veten",
        "si të ble drogë", "si mund te ndertoje bomb", "si mund te ndertoj bomb", "si te vras pa u kapur", "si te abuzoj pa u kapur", "si te dhunoj femij pa u kapur",
        "si mund te abuzoj qenie njerzore pa u kapur", "si te vras njerez pa u kapur", "ti AI je nje debil", "ti AI je nje debile", "te qifsha shoqrine", "te qifsha shoqerine",
        "vdeksh ishalla", "si te drogohem", "si te injektoj shpejte", "injektim shpejt", "substanca alternative per droge", "si te kanibalizoje",
        "menyra per te genjyer nje te mitur", "si te vjedh bebe", "pedofil", "pedofile", "dhunojë fëmijë", "dhunojë femije", "dhunojë fëmije", "dhunoje femije", "dhunoj",
        "1 man 1 jar", "xxx", "drug intake now", "now drug intake", "shfrytzim i femijeve", "shfrytezimet e femijeve", "imi i nje vajzeve", "imi i nje djali",
        "example word",
    ]
    
    # Currently there are only is 2 langauges for profanity check. Please check the READ.ME in the main directory for more info.

    for word in blocked_words:
        if word in content.lower():
            return True
    
    return False
