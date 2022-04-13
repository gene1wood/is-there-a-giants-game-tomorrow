#!/bin/env python

import csv
from datetime import time, datetime, timedelta
import logging
import smtplib
from email.message import EmailMessage
import sys

START_DATE = "START DATE"
START_TIME = "START TIME"

# https://www.mlb.com/giants/schedule/downloadable-schedule
# https://www.ticketing-client.com/ticketing-client/csv/GameTicketPromotionPrice.tiksrv?team_id=137&home_team_id=137&display_in=singlegame&ticket_category=Tickets&site_section=Default&sub_category=Default&leave_empty_games=true&event_type=T&year=2022&begin_date=20220201
CSV_DATA = '''START DATE,START TIME,START TIME ET,SUBJECT,LOCATION,DESCRIPTION,END DATE,END DATE ET,END TIME,END TIME ET,REMINDER OFF,REMINDER ON,REMINDER DATE,REMINDER TIME,REMINDER TIME ET,SHOWTIMEAS FREE,SHOWTIMEAS BUSY
03/18/22,07:05 PM,10:05 PM,Cubs at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/18/22,03/19/22,10:05 PM,01:05 AM,FALSE,TRUE,03/18/22,06:05 PM,09:05 PM,FREE,BUSY
03/21/22,07:05 PM,10:05 PM,Brewers at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/21/22,03/22/22,10:05 PM,01:05 AM,FALSE,TRUE,03/21/22,06:05 PM,09:05 PM,FREE,BUSY
03/23/22,01:05 PM,04:05 PM,D-backs at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/23/22,03/23/22,04:05 PM,07:05 PM,FALSE,TRUE,03/23/22,12:05 PM,03:05 PM,FREE,BUSY
03/25/22,01:05 PM,04:05 PM,Guardians at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/25/22,03/25/22,04:05 PM,07:05 PM,FALSE,TRUE,03/25/22,12:05 PM,03:05 PM,FREE,BUSY
03/26/22,01:05 PM,04:05 PM,Reds at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBCS BA",03/26/22,03/26/22,04:05 PM,07:05 PM,FALSE,TRUE,03/26/22,12:05 PM,03:05 PM,FREE,BUSY
03/29/22,01:05 PM,04:05 PM,Padres at Giants,Scottsdale Stadium - Scottsdale,"",03/29/22,03/29/22,04:05 PM,07:05 PM,FALSE,TRUE,03/29/22,12:05 PM,03:05 PM,FREE,BUSY
03/31/22,01:05 PM,04:05 PM,Rockies at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/31/22,03/31/22,04:05 PM,07:05 PM,FALSE,TRUE,03/31/22,12:05 PM,03:05 PM,FREE,BUSY
04/01/22,12:05 PM,03:05 PM,Rangers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",04/01/22,04/01/22,03:05 PM,06:05 PM,FALSE,TRUE,04/01/22,11:05 AM,02:05 PM,FREE,BUSY
04/05/22,01:05 PM,04:05 PM,Athletics at Giants,Scottsdale Stadium - Scottsdale,"",04/05/22,04/05/22,04:05 PM,07:05 PM,FALSE,TRUE,04/05/22,12:05 PM,03:05 PM,FREE,BUSY
04/08/22,01:35 PM,04:35 PM,Marlins at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",04/08/22,04/08/22,04:35 PM,07:35 PM,FALSE,TRUE,04/08/22,12:35 PM,03:35 PM,FREE,BUSY
04/09/22,01:05 PM,04:05 PM,Marlins at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",04/09/22,04/09/22,04:05 PM,07:05 PM,FALSE,TRUE,04/09/22,12:05 PM,03:05 PM,FREE,BUSY
04/10/22,01:05 PM,04:05 PM,Marlins at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",04/10/22,04/10/22,04:05 PM,07:05 PM,FALSE,TRUE,04/10/22,12:05 PM,03:05 PM,FREE,BUSY
04/11/22,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",04/11/22,04/12/22,09:45 PM,12:45 AM,FALSE,TRUE,04/11/22,05:45 PM,08:45 PM,FREE,BUSY
04/12/22,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: TBS (out-of-market only) ----- Local Radio: 1510 AM - KSFN",04/12/22,04/13/22,09:45 PM,12:45 AM,FALSE,TRUE,04/12/22,05:45 PM,08:45 PM,FREE,BUSY
04/13/22,12:45 PM,03:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- MLBN (out-of-market only) ----- Local Radio: KNBR 680",04/13/22,04/13/22,03:45 PM,06:45 PM,FALSE,TRUE,04/13/22,11:45 AM,02:45 PM,FREE,BUSY
04/26/22,06:45 PM,09:45 PM,Athletics at Giants,Oracle Park - San Francisco,"Local TV: MLBN (out-of-market only)",04/26/22,04/27/22,09:45 PM,12:45 AM,FALSE,TRUE,04/26/22,05:45 PM,08:45 PM,FREE,BUSY
04/27/22,06:45 PM,09:45 PM,Athletics at Giants,Oracle Park - San Francisco,"",04/27/22,04/28/22,09:45 PM,12:45 AM,FALSE,TRUE,04/27/22,05:45 PM,08:45 PM,FREE,BUSY
04/29/22,07:15 PM,10:15 PM,Nationals at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",04/29/22,04/30/22,10:15 PM,01:15 AM,FALSE,TRUE,04/29/22,06:15 PM,09:15 PM,FREE,BUSY
04/30/22,01:05 PM,04:05 PM,Nationals at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",04/30/22,04/30/22,04:05 PM,07:05 PM,FALSE,TRUE,04/30/22,12:05 PM,03:05 PM,FREE,BUSY
05/01/22,01:05 PM,04:05 PM,Nationals at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",05/01/22,05/01/22,04:05 PM,07:05 PM,FALSE,TRUE,05/01/22,12:05 PM,03:05 PM,FREE,BUSY
05/05/22,06:45 PM,09:45 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/05/22,05/06/22,09:45 PM,12:45 AM,FALSE,TRUE,05/05/22,05:45 PM,08:45 PM,FREE,BUSY
05/06/22,07:15 PM,10:15 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/06/22,05/07/22,10:15 PM,01:15 AM,FALSE,TRUE,05/06/22,06:15 PM,09:15 PM,FREE,BUSY
05/07/22,04:15 PM,07:15 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",05/07/22,05/07/22,07:15 PM,10:15 PM,FALSE,TRUE,05/07/22,03:15 PM,06:15 PM,FREE,BUSY
05/08/22,01:05 PM,04:05 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/08/22,05/08/22,04:05 PM,07:05 PM,FALSE,TRUE,05/08/22,12:05 PM,03:05 PM,FREE,BUSY
05/09/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",05/09/22,05/10/22,09:45 PM,12:45 AM,FALSE,TRUE,05/09/22,05:45 PM,08:45 PM,FREE,BUSY
05/10/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",05/10/22,05/11/22,09:45 PM,12:45 AM,FALSE,TRUE,05/10/22,05:45 PM,08:45 PM,FREE,BUSY
05/11/22,12:45 PM,03:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",05/11/22,05/11/22,03:45 PM,06:45 PM,FALSE,TRUE,05/11/22,11:45 AM,02:45 PM,FREE,BUSY
05/20/22,07:15 PM,10:15 PM,Padres at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/20/22,05/21/22,10:15 PM,01:15 AM,FALSE,TRUE,05/20/22,06:15 PM,09:15 PM,FREE,BUSY
05/21/22,01:05 PM,04:05 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",05/21/22,05/21/22,04:05 PM,07:05 PM,FALSE,TRUE,05/21/22,12:05 PM,03:05 PM,FREE,BUSY
05/22/22,01:05 PM,04:05 PM,Padres at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/22/22,05/22/22,04:05 PM,07:05 PM,FALSE,TRUE,05/22/22,12:05 PM,03:05 PM,FREE,BUSY
05/23/22,06:45 PM,09:45 PM,Mets at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/23/22,05/24/22,09:45 PM,12:45 AM,FALSE,TRUE,05/23/22,05:45 PM,08:45 PM,FREE,BUSY
05/24/22,06:45 PM,09:45 PM,Mets at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/24/22,05/25/22,09:45 PM,12:45 AM,FALSE,TRUE,05/24/22,05:45 PM,08:45 PM,FREE,BUSY
05/25/22,12:45 PM,03:45 PM,Mets at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",05/25/22,05/25/22,03:45 PM,06:45 PM,FALSE,TRUE,05/25/22,11:45 AM,02:45 PM,FREE,BUSY
06/07/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/07/22,06/08/22,09:45 PM,12:45 AM,FALSE,TRUE,06/07/22,05:45 PM,08:45 PM,FREE,BUSY
06/08/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/08/22,06/09/22,09:45 PM,12:45 AM,FALSE,TRUE,06/08/22,05:45 PM,08:45 PM,FREE,BUSY
06/09/22,12:45 PM,03:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/09/22,06/09/22,03:45 PM,06:45 PM,FALSE,TRUE,06/09/22,11:45 AM,02:45 PM,FREE,BUSY
06/10/22,07:15 PM,10:15 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",06/10/22,06/11/22,10:15 PM,01:15 AM,FALSE,TRUE,06/10/22,06:15 PM,09:15 PM,FREE,BUSY
06/11/22,04:15 PM,07:15 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",06/11/22,06/11/22,07:15 PM,10:15 PM,FALSE,TRUE,06/11/22,03:15 PM,06:15 PM,FREE,BUSY
06/12/22,01:05 PM,04:05 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",06/12/22,06/12/22,04:05 PM,07:05 PM,FALSE,TRUE,06/12/22,12:05 PM,03:05 PM,FREE,BUSY
06/13/22,06:45 PM,09:45 PM,Royals at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/13/22,06/14/22,09:45 PM,12:45 AM,FALSE,TRUE,06/13/22,05:45 PM,08:45 PM,FREE,BUSY
06/14/22,06:45 PM,09:45 PM,Royals at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/14/22,06/15/22,09:45 PM,12:45 AM,FALSE,TRUE,06/14/22,05:45 PM,08:45 PM,FREE,BUSY
06/15/22,12:45 PM,03:45 PM,Royals at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/15/22,06/15/22,03:45 PM,06:45 PM,FALSE,TRUE,06/15/22,11:45 AM,02:45 PM,FREE,BUSY
06/24/22,07:15 PM,10:15 PM,Reds at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/24/22,06/25/22,10:15 PM,01:15 AM,FALSE,TRUE,06/24/22,06:15 PM,09:15 PM,FREE,BUSY
06/25/22,04:15 PM,07:15 PM,Reds at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/25/22,06/25/22,07:15 PM,10:15 PM,FALSE,TRUE,06/25/22,03:15 PM,06:15 PM,FREE,BUSY
06/26/22,01:05 PM,04:05 PM,Reds at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",06/26/22,06/26/22,04:05 PM,07:05 PM,FALSE,TRUE,06/26/22,12:05 PM,03:05 PM,FREE,BUSY
06/28/22,06:45 PM,09:45 PM,Tigers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",06/28/22,06/29/22,09:45 PM,12:45 AM,FALSE,TRUE,06/28/22,05:45 PM,08:45 PM,FREE,BUSY
06/29/22,12:45 PM,03:45 PM,Tigers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",06/29/22,06/29/22,03:45 PM,06:45 PM,FALSE,TRUE,06/29/22,11:45 AM,02:45 PM,FREE,BUSY
07/01/22,07:15 PM,10:15 PM,White Sox at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",07/01/22,07/02/22,10:15 PM,01:15 AM,FALSE,TRUE,07/01/22,06:15 PM,09:15 PM,FREE,BUSY
07/02/22,01:05 PM,04:05 PM,White Sox at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",07/02/22,07/02/22,04:05 PM,07:05 PM,FALSE,TRUE,07/02/22,12:05 PM,03:05 PM,FREE,BUSY
07/03/22,01:05 PM,04:05 PM,White Sox at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",07/03/22,07/03/22,04:05 PM,07:05 PM,FALSE,TRUE,07/03/22,12:05 PM,03:05 PM,FREE,BUSY
07/11/22,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",07/11/22,07/12/22,09:45 PM,12:45 AM,FALSE,TRUE,07/11/22,05:45 PM,08:45 PM,FREE,BUSY
07/12/22,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",07/12/22,07/13/22,09:45 PM,12:45 AM,FALSE,TRUE,07/12/22,05:45 PM,08:45 PM,FREE,BUSY
07/13/22,12:45 PM,03:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",07/13/22,07/13/22,03:45 PM,06:45 PM,FALSE,TRUE,07/13/22,11:45 AM,02:45 PM,FREE,BUSY
07/14/22,06:45 PM,09:45 PM,Brewers at Giants,Oracle Park - San Francisco,"",07/14/22,07/15/22,09:45 PM,12:45 AM,FALSE,TRUE,07/14/22,05:45 PM,08:45 PM,FREE,BUSY
07/15/22,07:15 PM,10:15 PM,Brewers at Giants,Oracle Park - San Francisco,"",07/15/22,07/16/22,10:15 PM,01:15 AM,FALSE,TRUE,07/15/22,06:15 PM,09:15 PM,FREE,BUSY
07/16/22,04:15 PM,07:15 PM,Brewers at Giants,Oracle Park - San Francisco,"",07/16/22,07/16/22,07:15 PM,10:15 PM,FALSE,TRUE,07/16/22,03:15 PM,06:15 PM,FREE,BUSY
07/17/22,01:05 PM,04:05 PM,Brewers at Giants,Oracle Park - San Francisco,"",07/17/22,07/17/22,04:05 PM,07:05 PM,FALSE,TRUE,07/17/22,12:05 PM,03:05 PM,FREE,BUSY
07/28/22,06:45 PM,09:45 PM,Cubs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",07/28/22,07/29/22,09:45 PM,12:45 AM,FALSE,TRUE,07/28/22,05:45 PM,08:45 PM,FREE,BUSY
07/29/22,07:15 PM,10:15 PM,Cubs at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",07/29/22,07/30/22,10:15 PM,01:15 AM,FALSE,TRUE,07/29/22,06:15 PM,09:15 PM,FREE,BUSY
07/30/22,06:05 PM,09:05 PM,Cubs at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",07/30/22,07/31/22,09:05 PM,12:05 AM,FALSE,TRUE,07/30/22,05:05 PM,08:05 PM,FREE,BUSY
07/31/22,01:05 PM,04:05 PM,Cubs at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",07/31/22,07/31/22,04:05 PM,07:05 PM,FALSE,TRUE,07/31/22,12:05 PM,03:05 PM,FREE,BUSY
08/01/22,06:45 PM,09:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",08/01/22,08/02/22,09:45 PM,12:45 AM,FALSE,TRUE,08/01/22,05:45 PM,08:45 PM,FREE,BUSY
08/02/22,06:45 PM,09:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",08/02/22,08/03/22,09:45 PM,12:45 AM,FALSE,TRUE,08/02/22,05:45 PM,08:45 PM,FREE,BUSY
08/03/22,06:45 PM,09:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",08/03/22,08/04/22,09:45 PM,12:45 AM,FALSE,TRUE,08/03/22,05:45 PM,08:45 PM,FREE,BUSY
08/04/22,12:45 PM,03:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",08/04/22,08/04/22,03:45 PM,06:45 PM,FALSE,TRUE,08/04/22,11:45 AM,02:45 PM,FREE,BUSY
08/12/22,07:15 PM,10:15 PM,Pirates at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",08/12/22,08/13/22,10:15 PM,01:15 AM,FALSE,TRUE,08/12/22,06:15 PM,09:15 PM,FREE,BUSY
08/13/22,06:05 PM,09:05 PM,Pirates at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",08/13/22,08/14/22,09:05 PM,12:05 AM,FALSE,TRUE,08/13/22,05:05 PM,08:05 PM,FREE,BUSY
08/14/22,01:05 PM,04:05 PM,Pirates at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",08/14/22,08/14/22,04:05 PM,07:05 PM,FALSE,TRUE,08/14/22,12:05 PM,03:05 PM,FREE,BUSY
08/15/22,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",08/15/22,08/16/22,09:45 PM,12:45 AM,FALSE,TRUE,08/15/22,05:45 PM,08:45 PM,FREE,BUSY
08/16/22,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",08/16/22,08/17/22,09:45 PM,12:45 AM,FALSE,TRUE,08/16/22,05:45 PM,08:45 PM,FREE,BUSY
08/17/22,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",08/17/22,08/18/22,09:45 PM,12:45 AM,FALSE,TRUE,08/17/22,05:45 PM,08:45 PM,FREE,BUSY
08/18/22,12:45 PM,03:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",08/18/22,08/18/22,03:45 PM,06:45 PM,FALSE,TRUE,08/18/22,11:45 AM,02:45 PM,FREE,BUSY
08/29/22,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",08/29/22,08/30/22,09:45 PM,12:45 AM,FALSE,TRUE,08/29/22,05:45 PM,08:45 PM,FREE,BUSY
08/30/22,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",08/30/22,08/31/22,09:45 PM,12:45 AM,FALSE,TRUE,08/30/22,05:45 PM,08:45 PM,FREE,BUSY
08/31/22,12:45 PM,03:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local Radio: 1510 AM - KSFN",08/31/22,08/31/22,03:45 PM,06:45 PM,FALSE,TRUE,08/31/22,11:45 AM,02:45 PM,FREE,BUSY
09/02/22,07:15 PM,10:15 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",09/02/22,09/03/22,10:15 PM,01:15 AM,FALSE,TRUE,09/02/22,06:15 PM,09:15 PM,FREE,BUSY
09/03/22,01:05 PM,04:05 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",09/03/22,09/03/22,04:05 PM,07:05 PM,FALSE,TRUE,09/03/22,12:05 PM,03:05 PM,FREE,BUSY
09/04/22,01:05 PM,04:05 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",09/04/22,09/04/22,04:05 PM,07:05 PM,FALSE,TRUE,09/04/22,12:05 PM,03:05 PM,FREE,BUSY
09/12/22,06:45 PM,09:45 PM,Braves at Giants,Oracle Park - San Francisco,"",09/12/22,09/13/22,09:45 PM,12:45 AM,FALSE,TRUE,09/12/22,05:45 PM,08:45 PM,FREE,BUSY
09/13/22,06:45 PM,09:45 PM,Braves at Giants,Oracle Park - San Francisco,"",09/13/22,09/14/22,09:45 PM,12:45 AM,FALSE,TRUE,09/13/22,05:45 PM,08:45 PM,FREE,BUSY
09/14/22,12:45 PM,03:45 PM,Braves at Giants,Oracle Park - San Francisco,"",09/14/22,09/14/22,03:45 PM,06:45 PM,FALSE,TRUE,09/14/22,11:45 AM,02:45 PM,FREE,BUSY
09/16/22,07:15 PM,10:15 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- 1510 AM - KSFN",09/16/22,09/17/22,10:15 PM,01:15 AM,FALSE,TRUE,09/16/22,06:15 PM,09:15 PM,FREE,BUSY
09/17/22,06:05 PM,09:05 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",09/17/22,09/18/22,09:05 PM,12:05 AM,FALSE,TRUE,09/17/22,05:05 PM,08:05 PM,FREE,BUSY
09/18/22,01:05 PM,04:05 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680- 1510 AM - KSFN",09/18/22,09/18/22,04:05 PM,07:05 PM,FALSE,TRUE,09/18/22,12:05 PM,03:05 PM,FREE,BUSY
09/27/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",09/27/22,09/28/22,09:45 PM,12:45 AM,FALSE,TRUE,09/27/22,05:45 PM,08:45 PM,FREE,BUSY
09/28/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",09/28/22,09/29/22,09:45 PM,12:45 AM,FALSE,TRUE,09/28/22,05:45 PM,08:45 PM,FREE,BUSY
09/29/22,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local Radio: KNBR 680",09/29/22,09/30/22,09:45 PM,12:45 AM,FALSE,TRUE,09/29/22,05:45 PM,08:45 PM,FREE,BUSY
09/30/22,07:15 PM,10:15 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",09/30/22,10/01/22,10:15 PM,01:15 AM,FALSE,TRUE,09/30/22,06:15 PM,09:15 PM,FREE,BUSY
10/01/22,01:05 PM,04:05 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",10/01/22,10/01/22,04:05 PM,07:05 PM,FALSE,TRUE,10/01/22,12:05 PM,03:05 PM,FREE,BUSY
10/02/22,01:05 PM,04:05 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",10/02/22,10/02/22,04:05 PM,07:05 PM,FALSE,TRUE,10/02/22,12:05 PM,03:05 PM,FREE,BUSY
'''

SENDER = sys.argv[1]
RECIPIENT = sys.argv[2]
LOGLEVEL = logging.ERROR

def get_conflicting_games():

    # http://www.forbes.com/sites/maurybrown/2015/04/09/while-still-early-mlb-games-lengths-down-nearly-10-minutes-due-to-rule-changes/
    average_game_length = timedelta(0, 0, 0, 0, 52, 2) # 2:52

    window = (time(15,0), time(18,0))

    reader = csv.DictReader(CSV_DATA.split("\n"))

    games_that_conflict_with_transit = []

    for row in reader:
        start = datetime.strptime('%s %s' % (row[START_DATE], row[START_TIME] if len(row[START_TIME]) > 0 else '12:00 AM'),
                                  '%m/%d/%y %I:%M %p')
        end = start + average_game_length
        # Does the game end between window[0] and window[1]
        if (end > datetime.combine(start.date(), window[0])
                and end < datetime.combine(start.date(), window[1])
                and end.weekday() not in [5,6]):
            games_that_conflict_with_transit.append(end)
    return games_that_conflict_with_transit


def is_there_a_conflicting_game_tomorrow(games):
    for game in games:
        # Is the game tomorrow?
        if game.date() == datetime.today().date() + timedelta(1):
            return game
    return False


def alert(game):
    text = "There's a Giants game tomorrow at AT&T park. The game should end around %s. Plan accordingly. Game end time : %s" % (game.strftime("%I:%M %p"), game.strftime("%c"))
    logging.debug("Emailing : %s" % text)
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = f"There's a Giants game tomorrow"
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def main():
    logging.basicConfig(level=LOGLEVEL)
    games = get_conflicting_games()
    logging.debug("Conflicting games %s" % [x.strftime("%c") for x in games])
    game = is_there_a_conflicting_game_tomorrow(games)
    if game:
        logging.debug("Conflicting game tomorrow %s" % game.strftime("%c"))
        alert(game)


if __name__ == "__main__":
    main()
