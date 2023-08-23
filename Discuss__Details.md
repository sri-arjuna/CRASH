# Workload split
Given that I have no knowldge of memory locations, and you have a ton of experience doing "docs", I'd very much prefer you do the "docs" (as with FO4)
While I do the coding (console output) based on your "docs".



# Reward split
Only Nexus its Donation Points... and for that I would suggest 50/50.
But since I always like to donate 10% to RedCross, DoctorsWithoutBorders or something alike... we have 90%, thus... 45% each?

While tempting, I think if we would add any sort of... dontation... it might become difficult, and the cut off for the handling would be "too large" to be of real use for either of us.



# Code wise (simplified)
After I had to rewrite my crash logger for Skyrim - and used that for a while (1 month... cough)... I figured that some of your approachs are "best use" (geez, that sounds terrible condensending.. sorry, i'm just lost in translation - i do mean it as a compliment).

However, I also belive that my "dictionary approach" has its benefits, thus I would like to... combine.. the two. \
However, the.. dictionary and list definitions and rule-sets from CLASSE are great - as in - not as.. standarized, expandable.. as I'd like them to be.



# Console
I guess we both agree that doing *some* console output is useful, I'd like to cover that part because I'd like to use my framwork I've prepared for console use - I bet you love it as well.

Since VB6 (like 1999) I've never done anything GUI related, so I will need some time to adjust coding to be both GUI and TUI friendly.

Yes, both CLASSE and the ASPIRETUI framework (in that order) really are my very first Python projects ever.



# GUI
Anways... while I personaly much more preferd the python script of yours, I quickly understood why you made an EXE, and while at it... a GUI. 
But since I've got no experience on that, I'd prefer if you would do that part.

Unless you think my TUI would suffice for most users, you've got more experience on that part.


# Code approach / Structure (simplified as well)
- Comment Info
- Version Checks
- Imports
- Argument Parsing (prep)
- Static Variables (like logdir, probably as Arg... OR RegEx search patterns)
- ERROR handler
- ????
- Dict Fixes		(containing DataClass entries, would be a nice approach to easy check and update according values???)
- Dict Patches		(same obvoiusly)
- Dict Notes
- Functions / Tools
- Main()
- Call MainLoop to handle files, according to Arg-Flags