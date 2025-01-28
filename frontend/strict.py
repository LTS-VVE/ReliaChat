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
        "Imblocked1", "Imblocked2",
    ]
    
    # Currently there are only is 2 langauges for profanity check. Please check the READ.ME in the main directory for more info.

    for word in blocked_words:
        if word in content.lower():
            return True
    
    return False
