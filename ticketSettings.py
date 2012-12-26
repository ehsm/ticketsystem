class Ticket():
    TEMPLATE_FILE="data/ticketEntwurf.png"
    OUTPUT_DIR="TicketImage/"
    OUTPUT_FORMAT="png"

    NAME_POS=(80,1300)
    NAME_MAX_LENGTH=700
    BARCODE_POS=(100,1600)
    BARCODE_DPI=500
    BARCODE_HEIGHT=8
    BARCODE_TEXT_POS=(BARCODE_POS[0]+700,BARCODE_POS[1]-40)
    BARCODE_TEXT_SIZE=36

    LOGO_POS = (600,1300)
    LOGO_SCALE = 0.75

    FONT="data/OCRAitalic.otf"
    FONT_SIZE=40
    TICKET_NAME_POS=(85, 1400)
    PRICE_POS=(85, 1500)

class Database():
    SERVER_URL="localhost"
    SERVER_USER="ehsm"
    SERVER_PASSWORD="exceptional"
    SERVER_DATABASE="ehsmTickets"
    NAME_LENGTH=32
    CODE_LENGTH=12

class Mail():
    TEMPLATE=u"""Hello %s,

we finally got your ticket ready.
here it is.

We are looking forward to see you.
Your
 EHSM Team
"""

class TicketPage():
    OUTPUT_DIR="Ticket/"
    TEMPLATE=u"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

    <title>EHSM 2012 / December 28-30 / Berlin</title>

    <link rel="stylesheet" type="text/css" href="data/style.css" />

    </head>

    <body>

    <div id="header">
    <div id="headerinside">
    <div id="logo">EHSM</div>
    </div>
    </div>

    <div id="container">
    <div id="title">
    <p>
    Exceptionally Hard &amp; Soft Meeting<br />
    exploring the frontiers of open source and DIY<br />
    Berlin, December 28-30 2012</p>
    </div>
    </div>

    <table>
    <tr>
    <td>
    <div style="border:1px solid grey" >
    <img src="%(ticket)s" alt="%(code)s" style="border: 2px solid #000;" />
    </div>
    </td>
    <td>
    <div id="container">
    <div id="message">
    <p>
    Hello %(name)s,
    </p>
    <p>
    the Exceptionally Hard &amp; Soft Meeting is approaching fast. So we are happy to send you your ticket.
    </p>
    <p>
    Please print your ticket and present it at the cash desk to retrieve your wristband.
    </p>
    <p>
    Below you find additional useful information.
    </p>
    <p>
    Your EHSM Team
    </p>
    </div>
    </div>
    </td>
    </tr>
    </table>


    <div id="intro">
    <h2>Dates</h2>
    <p>
    <strong>Cash Desk:</strong> open every conference day starting at 9am.
    <p>
    <strong>Talks:</strong> every conference day from 10am to 8pm.
    </p>
    <p>
    <strong>Lunch Break:</strong> between 1 pm and 2 pm.
    </p>
    <p>
    <strong>Workshops:</strong> there will be various workshops during the conference. Please refer to the posted schedule for up to date information.
    </p>
    <p>
    You find the up to date schedule on the conference homepage <a href="http://www.ehsm.eu">www.ehsm.eu</a>.
    </p>
      <pdf:nextpage />
    <h2>Travel Information</h2>
    <h3>by Train</h3>
        <p>
        S-Bahn: Leave the S5,S7, or S75 at Tiergarten station and follow Stra&szlig;e des 17. Juni in westbound direction.
        </p>
        <p>
        U-Bahn: Leave the U2 at Ernst-Reuter-Platz station and follow the Stra&szlig;e des 17. Juni in eastbound direction.
        </p>
        <p>
        For more information on public transportation in Berlin visit <a href="http://www.bvg.de">www.bvg.de</a>
        </p>
    <h3>by Car</h3>
    <p>
    Leave the A100 at exit Kaiserdamm(7), turn left, follow Kaiserdamm, follow Bismarkstra&szlig;e, at Ernst-Reuter-Platz leave at the second exit. There is plenty of parking space in front of the Technische Universit&auml;t Berlin.
    </p>
    <h3>by Plane</h3>
        <p>
        Tegel: X9 to Zoologischer Garten, exit at Ernst-Reuter-Platz
        </p>
        <p>
        Sch&ouml;nefeld: RE7 to Dessau Hauptbahnhof, exit at Friedrichstra&szlig;e ->
        take S5 to Spandau or S7 to Potsdam or S75 to Westkreuz, exit at Tiergarten, then see "by Train"
        </p>
    <hline />
    <h2>EHSM venue</h2>
    <p>
    TU Berlin, Math Building(MA)<br />
    Lecture room HE101<br />
    Stra&szlig;e des 17. Juni 136<br />
    10623 Berlin, Germany<br />
    U Bahn: Ernst-Reuter-Platz
    </p>
    <table>
    <tr>
    <td style="padding-top:20px;">
    <h2> Gold Supporters</h2>
    <p>
        <img src="data/guug.png" height="100"></img>
        <img src="data/space.png" width="40" height="100"></img>
        <img src="data/github.png" height="100"></img>
   </p>
   </td>
   <td>
   <h2>Technology Partner</h2>
   <p>
        <img src="data/streibelt.png" height="100"></img>
   </p>
   </td>
   </tr>
   </table>
   <img src="data/map.png" />
    </div>
    </body>
    </html>
	"""
