class Ticket():
    TEMPLATE_FILE="data/ticket_template.png"
    OUTPUT_DIR="TicketImage/"
    OUTPUT_FORMAT="png"

    NAME_POS=(20,320)
    NAME_MAX_LENGTH=265
    BARCODE_POS=(5,380)

    FONT="data/OCRAitalic.otf"
    FONT_SIZE=10
    TICKET_NAME_POS=(20, 345)
    PRICE_POS=(20, 365)

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
    <img src="%(ticket)s" alt="%(code)s" style="border: 2px solid #000;" />
    </td>
    <td>
    <div id="container">
    <div id="message">
    <p>
    Hello %(name)s,
    </p>
    <p>
    the Exceptionally Hard &amp; Soft Meeting in approaching fast. So we are happy to send you your ticket.
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


    <div id="container">
    <div id="intro">

    <h2>EHSM venue</h2>
    <p>
    TU Berlin, H&ouml;rsaalgeb&auml;ude Elektrotechnik<br />
    Lecture room HE101<br />
    Stra&szlig;e des 17. Juni 136<br />
    10623 Berlin, Germany<br />
    U Bahn: Ernst-Reuter-Platz
    </p>
    </div>

    </div>

    <div id="footer">
    <div id="footerinside">
    <p>This is the life on Mars. <a href="http://www.twitter.com/ehsmeeting">Follow us on twitter</a></p>
    </div>
    </div>

    </body>
    </html>
	"""
