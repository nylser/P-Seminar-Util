# P-Seminar-Util
Some utils for my project seminar @ Feodor-Lynen-Gymnasium
Mostly for FINView
Table2DBF will take the Table with collected information our group has and writes it into the DBF format.
This makes digitalization extremely easy as you just have to enter the street and it's in FINView, run this tool, and all attributes are filled in.
It also updates the DBF Table with the newest values.
In this project I use easygui, dbf for python and a ported version (for python3.4) of the google-gdata api interface.

## Usage

Quite easy: Just execute the table2dbf python file if you've got all the required libraries.

<strong>One important thing to note: Close FINView before accessing one of the open DBF files.</strong>

