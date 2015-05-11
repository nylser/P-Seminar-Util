# P-Seminar-Util
Some utils for my project seminar @ Feodor-Lynen-Gymnasium
Mostly for FINView
Table2DBF will take the Table with collected information our group has and writes it into the DBF format.
This makes digitalization extremely easy as you just have to enter the street/digitalization in FINView, run this tool, and all attributes are filled in.
It also updates the DBF Table with the newest values.
The newest version now features a better GUI using PyQt5.

Used libraries:
* dbf for python (https://pypi.python.org/pypi/dbf/)
* google-gdata api (inofficial py3.4 port) (https://github.com/hfalcic/google-gdata)
* PyQt5 (http://www.riverbankcomputing.co.uk/software/pyqt/intro)


## Usage

Quite easy: Just execute the table2dbf_gui python file if you've got all the required libraries.

<strong>One important thing to note: Close FINView before accessing one of the open DBF files.</strong>

