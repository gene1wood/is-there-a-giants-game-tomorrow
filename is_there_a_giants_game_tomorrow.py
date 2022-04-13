#!/bin/env python

import csv
from datetime import time, datetime, timedelta
import logging
import smtplib
from email.message import EmailMessage
import sys

START_DATE = "START DATE"
START_TIME = "START TIME"

# http://mlb.mlb.com/soa/ical/schedule.csv?home_team_id=137&season=2015
# http://mlb.mlb.com/ticketing-client/csv/EventTicketPromotionPrice.tiksrv?team_id=137&home_team_id=137&display_in=singlegame&ticket_category=Tickets&site_section=Default&sub_category=Default&leave_empty_games=true&event_type=T&event_type=Y
# http://www.ticketing-client.com/ticketing-client/csv/EventTicketPromotionPrice.tiksrv?team_id=137&home_team_id=137&display_in=singlegame&ticket_category=Tickets&site_section=Default&sub_category=Default&leave_empty_games=true&event_type=T
CSV_DATA = '''START DATE,START TIME,START TIME ET,SUBJECT,LOCATION,DESCRIPTION,END DATE,END DATE ET,END TIME,END TIME ET,REMINDER OFF,REMINDER ON,REMINDER DATE,REMINDER TIME,REMINDER TIME ET,SHOWTIMEAS FREE,SHOWTIMEAS BUSY
02/24/19,12:05 PM,03:05 PM,Cubs at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",02/24/19,02/24/19,03:05 PM,06:05 PM,FALSE,TRUE,02/24/19,11:05 AM,02:05 PM,FREE,BUSY
02/25/19,12:05 PM,03:05 PM,White Sox at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",02/25/19,02/25/19,03:05 PM,06:05 PM,FALSE,TRUE,02/25/19,11:05 AM,02:05 PM,FREE,BUSY
02/27/19,12:05 PM,03:05 PM,Royals at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",02/27/19,02/27/19,03:05 PM,06:05 PM,FALSE,TRUE,02/27/19,11:05 AM,02:05 PM,FREE,BUSY
03/01/19,06:05 PM,09:05 PM,Reds at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBC Bay Area- MLBN (out-of-market only) ----- Local Radio: MLB.com",03/01/19,03/02/19,09:05 PM,12:05 AM,FALSE,TRUE,03/01/19,05:05 PM,08:05 PM,FREE,BUSY
03/02/19,12:05 PM,03:05 PM,Rangers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/02/19,03/02/19,03:05 PM,06:05 PM,FALSE,TRUE,03/02/19,11:05 AM,02:05 PM,FREE,BUSY
03/04/19,12:05 PM,03:05 PM,Dodgers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/04/19,03/04/19,03:05 PM,06:05 PM,FALSE,TRUE,03/04/19,11:05 AM,02:05 PM,FREE,BUSY
03/07/19,06:05 PM,09:05 PM,Athletics at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBCS BA- MLBN (out-of-market only) ----- Local Radio: KNBR 680",03/07/19,03/08/19,09:05 PM,12:05 AM,FALSE,TRUE,03/07/19,05:05 PM,08:05 PM,FREE,BUSY
03/09/19,12:05 PM,03:05 PM,Cubs at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/09/19,03/09/19,03:05 PM,06:05 PM,FALSE,TRUE,03/09/19,11:05 AM,02:05 PM,FREE,BUSY
03/10/19,01:05 PM,04:05 PM,Rangers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/10/19,03/10/19,04:05 PM,07:05 PM,FALSE,TRUE,03/10/19,12:05 PM,03:05 PM,FREE,BUSY
03/12/19,07:05 PM,10:05 PM,Brewers at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBCS BA ----- Local Radio: MLB.com",03/12/19,03/13/19,10:05 PM,01:05 AM,FALSE,TRUE,03/12/19,06:05 PM,09:05 PM,FREE,BUSY
03/15/19,01:05 PM,04:05 PM,Angels at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/15/19,03/15/19,04:05 PM,07:05 PM,FALSE,TRUE,03/15/19,12:05 PM,03:05 PM,FREE,BUSY
03/16/19,01:05 PM,04:05 PM,Padres at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/16/19,03/16/19,04:05 PM,07:05 PM,FALSE,TRUE,03/16/19,12:05 PM,03:05 PM,FREE,BUSY
03/17/19,01:05 PM,04:05 PM,Royals at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/17/19,03/17/19,04:05 PM,07:05 PM,FALSE,TRUE,03/17/19,12:05 PM,03:05 PM,FREE,BUSY
03/20/19,07:05 PM,10:05 PM,Indians at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/20/19,03/21/19,10:05 PM,01:05 AM,FALSE,TRUE,03/20/19,06:05 PM,09:05 PM,FREE,BUSY
03/22/19,07:05 PM,10:05 PM,Rockies at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680",03/22/19,03/23/19,10:05 PM,01:05 AM,FALSE,TRUE,03/22/19,06:05 PM,09:05 PM,FREE,BUSY
03/23/19,01:05 PM,04:05 PM,D-backs at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/23/19,03/23/19,04:05 PM,07:05 PM,FALSE,TRUE,03/23/19,12:05 PM,03:05 PM,FREE,BUSY
03/25/19,06:45 PM,09:45 PM,Athletics at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/25/19,03/26/19,09:45 PM,12:45 AM,FALSE,TRUE,03/25/19,05:45 PM,08:45 PM,FREE,BUSY
03/26/19,06:45 PM,09:45 PM,Athletics at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/26/19,03/27/19,09:45 PM,12:45 AM,FALSE,TRUE,03/26/19,05:45 PM,08:45 PM,FREE,BUSY
04/05/19,01:35 PM,04:35 PM,Rays at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/05/19,04/05/19,04:35 PM,07:35 PM,FALSE,TRUE,04/05/19,12:35 PM,03:35 PM,FREE,BUSY
04/06/19,01:05 PM,04:05 PM,Rays at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/06/19,04/06/19,04:05 PM,07:05 PM,FALSE,TRUE,04/06/19,12:05 PM,03:05 PM,FREE,BUSY
04/07/19,01:05 PM,04:05 PM,Rays at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/07/19,04/07/19,04:05 PM,07:05 PM,FALSE,TRUE,04/07/19,12:05 PM,03:05 PM,FREE,BUSY
04/08/19,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/08/19,04/09/19,09:45 PM,12:45 AM,FALSE,TRUE,04/08/19,05:45 PM,08:45 PM,FREE,BUSY
04/09/19,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA+ ----- Local Radio: KNBR 680- KXZM 93.7",04/09/19,04/10/19,09:45 PM,12:45 AM,FALSE,TRUE,04/09/19,05:45 PM,08:45 PM,FREE,BUSY
04/10/19,12:45 PM,03:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/10/19,04/10/19,03:45 PM,06:45 PM,FALSE,TRUE,04/10/19,11:45 AM,02:45 PM,FREE,BUSY
04/11/19,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/11/19,04/12/19,09:45 PM,12:45 AM,FALSE,TRUE,04/11/19,05:45 PM,08:45 PM,FREE,BUSY
04/12/19,07:15 PM,10:15 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/12/19,04/13/19,10:15 PM,01:15 AM,FALSE,TRUE,04/12/19,06:15 PM,09:15 PM,FREE,BUSY
04/13/19,01:05 PM,04:05 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- FS1 ----- Local Radio: KNBR 680- KXZM 93.7",04/13/19,04/13/19,04:05 PM,07:05 PM,FALSE,TRUE,04/13/19,12:05 PM,03:05 PM,FREE,BUSY
04/14/19,01:05 PM,04:05 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/14/19,04/14/19,04:05 PM,07:05 PM,FALSE,TRUE,04/14/19,12:05 PM,03:05 PM,FREE,BUSY
04/26/19,07:15 PM,10:15 PM,Yankees at Giants,Oracle Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",04/26/19,04/27/19,10:15 PM,01:15 AM,FALSE,TRUE,04/26/19,06:15 PM,09:15 PM,FREE,BUSY
04/27/19,01:05 PM,04:05 PM,Yankees at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/27/19,04/27/19,04:05 PM,07:05 PM,FALSE,TRUE,04/27/19,12:05 PM,03:05 PM,FREE,BUSY
04/28/19,01:05 PM,04:05 PM,Yankees at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/28/19,04/28/19,04:05 PM,07:05 PM,FALSE,TRUE,04/28/19,12:05 PM,03:05 PM,FREE,BUSY
04/29/19,06:45 PM,09:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/29/19,04/30/19,09:45 PM,12:45 AM,FALSE,TRUE,04/29/19,05:45 PM,08:45 PM,FREE,BUSY
04/30/19,06:45 PM,09:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/30/19,05/01/19,09:45 PM,12:45 AM,FALSE,TRUE,04/30/19,05:45 PM,08:45 PM,FREE,BUSY
05/01/19,06:45 PM,09:45 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/01/19,05/02/19,09:45 PM,12:45 AM,FALSE,TRUE,05/01/19,05:45 PM,08:45 PM,FREE,BUSY
05/10/19,07:15 PM,10:15 PM,Reds at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/10/19,05/11/19,10:15 PM,01:15 AM,FALSE,TRUE,05/10/19,06:15 PM,09:15 PM,FREE,BUSY
05/11/19,06:05 PM,09:05 PM,Reds at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/11/19,05/12/19,09:05 PM,12:05 AM,FALSE,TRUE,05/11/19,05:05 PM,08:05 PM,FREE,BUSY
05/12/19,01:05 PM,04:05 PM,Reds at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/12/19,05/12/19,04:05 PM,07:05 PM,FALSE,TRUE,05/12/19,12:05 PM,03:05 PM,FREE,BUSY
05/14/19,06:45 PM,09:45 PM,Blue Jays at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/14/19,05/15/19,09:45 PM,12:45 AM,FALSE,TRUE,05/14/19,05:45 PM,08:45 PM,FREE,BUSY
05/15/19,12:45 PM,03:45 PM,Blue Jays at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/15/19,05/15/19,03:45 PM,06:45 PM,FALSE,TRUE,05/15/19,11:45 AM,02:45 PM,FREE,BUSY
05/20/19,06:45 PM,09:45 PM,Braves at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/20/19,05/21/19,09:45 PM,12:45 AM,FALSE,TRUE,05/20/19,05:45 PM,08:45 PM,FREE,BUSY
05/21/19,06:45 PM,09:45 PM,Braves at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- ESPN ----- Local Radio: KNBR 680- KXZM 93.7",05/21/19,05/22/19,09:45 PM,12:45 AM,FALSE,TRUE,05/21/19,05:45 PM,08:45 PM,FREE,BUSY
05/22/19,06:45 PM,09:45 PM,Braves at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/22/19,05/23/19,09:45 PM,12:45 AM,FALSE,TRUE,05/22/19,05:45 PM,08:45 PM,FREE,BUSY
05/23/19,12:45 PM,03:45 PM,Braves at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/23/19,05/23/19,03:45 PM,06:45 PM,FALSE,TRUE,05/23/19,11:45 AM,02:45 PM,FREE,BUSY
05/24/19,07:15 PM,10:15 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",05/24/19,05/25/19,10:15 PM,01:15 AM,FALSE,TRUE,05/24/19,06:15 PM,09:15 PM,FREE,BUSY
05/25/19,01:05 PM,04:05 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- FS1 ----- Local Radio: KNBR 680- KXZM 93.7",05/25/19,05/25/19,04:05 PM,07:05 PM,FALSE,TRUE,05/25/19,12:05 PM,03:05 PM,FREE,BUSY
05/26/19,01:05 PM,04:05 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/26/19,05/26/19,04:05 PM,07:05 PM,FALSE,TRUE,05/26/19,12:05 PM,03:05 PM,FREE,BUSY
06/07/19,07:15 PM,10:15 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",06/07/19,06/08/19,10:15 PM,01:15 AM,FALSE,TRUE,06/07/19,06:15 PM,09:15 PM,FREE,BUSY
06/08/19,04:15 PM,07:15 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: FOX ----- Local Radio: KNBR 680- KXZM 93.7",06/08/19,06/08/19,07:15 PM,10:15 PM,FALSE,TRUE,06/08/19,03:15 PM,06:15 PM,FREE,BUSY
06/09/19,01:05 PM,04:05 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/09/19,06/09/19,04:05 PM,07:05 PM,FALSE,TRUE,06/09/19,12:05 PM,03:05 PM,FREE,BUSY
06/11/19,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/11/19,06/12/19,09:45 PM,12:45 AM,FALSE,TRUE,06/11/19,05:45 PM,08:45 PM,FREE,BUSY
06/12/19,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/12/19,06/13/19,09:45 PM,12:45 AM,FALSE,TRUE,06/12/19,05:45 PM,08:45 PM,FREE,BUSY
06/14/19,07:15 PM,10:15 PM,Brewers at Giants,Oracle Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",06/14/19,06/15/19,10:15 PM,01:15 AM,FALSE,TRUE,06/14/19,06:15 PM,09:15 PM,FREE,BUSY
06/15/19,01:05 PM,04:05 PM,Brewers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/15/19,06/15/19,04:05 PM,07:05 PM,FALSE,TRUE,06/15/19,12:05 PM,03:05 PM,FREE,BUSY
06/16/19,01:05 PM,04:05 PM,Brewers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/16/19,06/16/19,04:05 PM,07:05 PM,FALSE,TRUE,06/16/19,12:05 PM,03:05 PM,FREE,BUSY
06/24/19,07:05 PM,10:05 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/24/19,06/25/19,10:05 PM,01:05 AM,FALSE,TRUE,06/24/19,06:05 PM,09:05 PM,FREE,BUSY
06/25/19,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- ESPN ----- Local Radio: KNBR 680- KXZM 93.7",06/25/19,06/26/19,09:45 PM,12:45 AM,FALSE,TRUE,06/25/19,05:45 PM,08:45 PM,FREE,BUSY
06/26/19,12:45 PM,03:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/26/19,06/26/19,03:45 PM,06:45 PM,FALSE,TRUE,06/26/19,11:45 AM,02:45 PM,FREE,BUSY
06/27/19,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/27/19,06/28/19,09:45 PM,12:45 AM,FALSE,TRUE,06/27/19,05:45 PM,08:45 PM,FREE,BUSY
06/28/19,07:15 PM,10:15 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",06/28/19,06/29/19,10:15 PM,01:15 AM,FALSE,TRUE,06/28/19,06:15 PM,09:15 PM,FREE,BUSY
06/29/19,07:05 PM,10:05 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/29/19,06/30/19,10:05 PM,01:05 AM,FALSE,TRUE,06/29/19,06:05 PM,09:05 PM,FREE,BUSY
06/30/19,01:05 PM,04:05 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/30/19,06/30/19,04:05 PM,07:05 PM,FALSE,TRUE,06/30/19,12:05 PM,03:05 PM,FREE,BUSY
07/05/19,07:15 PM,10:15 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/05/19,07/06/19,10:15 PM,01:15 AM,FALSE,TRUE,07/05/19,06:15 PM,09:15 PM,FREE,BUSY
07/06/19,07:05 PM,10:05 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/06/19,07/07/19,10:05 PM,01:05 AM,FALSE,TRUE,07/06/19,06:05 PM,09:05 PM,FREE,BUSY
07/07/19,01:05 PM,04:05 PM,Cardinals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/07/19,07/07/19,04:05 PM,07:05 PM,FALSE,TRUE,07/07/19,12:05 PM,03:05 PM,FREE,BUSY
07/09/19,,,NL All-Stars at AL All-Stars - Time TBD,Progressive Field - Cleveland,"",07/09/19,07/09/19,,,FALSE,TRUE,07/09/19,,,FREE,BUSY
07/18/19,06:45 PM,09:45 PM,Mets at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/18/19,07/19/19,09:45 PM,12:45 AM,FALSE,TRUE,07/18/19,05:45 PM,08:45 PM,FREE,BUSY
07/19/19,07:15 PM,10:15 PM,Mets at Giants,Oracle Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",07/19/19,07/20/19,10:15 PM,01:15 AM,FALSE,TRUE,07/19/19,06:15 PM,09:15 PM,FREE,BUSY
07/20/19,01:05 PM,04:05 PM,Mets at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- FS1 ----- Local Radio: KNBR 680- KXZM 93.7",07/20/19,07/20/19,04:05 PM,07:05 PM,FALSE,TRUE,07/20/19,12:05 PM,03:05 PM,FREE,BUSY
07/21/19,01:05 PM,04:05 PM,Mets at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/21/19,07/21/19,04:05 PM,07:05 PM,FALSE,TRUE,07/21/19,12:05 PM,03:05 PM,FREE,BUSY
07/22/19,06:45 PM,09:45 PM,Cubs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/22/19,07/23/19,09:45 PM,12:45 AM,FALSE,TRUE,07/22/19,05:45 PM,08:45 PM,FREE,BUSY
07/23/19,06:45 PM,09:45 PM,Cubs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/23/19,07/24/19,09:45 PM,12:45 AM,FALSE,TRUE,07/23/19,05:45 PM,08:45 PM,FREE,BUSY
07/24/19,12:45 PM,03:45 PM,Cubs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/24/19,07/24/19,03:45 PM,06:45 PM,FALSE,TRUE,07/24/19,11:45 AM,02:45 PM,FREE,BUSY
08/05/19,06:45 PM,09:45 PM,Nationals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/05/19,08/06/19,09:45 PM,12:45 AM,FALSE,TRUE,08/05/19,05:45 PM,08:45 PM,FREE,BUSY
08/06/19,06:45 PM,09:45 PM,Nationals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/06/19,08/07/19,09:45 PM,12:45 AM,FALSE,TRUE,08/06/19,05:45 PM,08:45 PM,FREE,BUSY
08/07/19,12:45 PM,03:45 PM,Nationals at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/07/19,08/07/19,03:45 PM,06:45 PM,FALSE,TRUE,08/07/19,11:45 AM,02:45 PM,FREE,BUSY
08/08/19,06:45 PM,09:45 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/08/19,08/09/19,09:45 PM,12:45 AM,FALSE,TRUE,08/08/19,05:45 PM,08:45 PM,FREE,BUSY
08/09/19,07:15 PM,10:15 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/09/19,08/10/19,10:15 PM,01:15 AM,FALSE,TRUE,08/09/19,06:15 PM,09:15 PM,FREE,BUSY
08/10/19,01:05 PM,04:05 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA- FS1 ----- Local Radio: KNBR 680- KXZM 93.7",08/10/19,08/10/19,04:05 PM,07:05 PM,FALSE,TRUE,08/10/19,12:05 PM,03:05 PM,FREE,BUSY
08/11/19,01:05 PM,04:05 PM,Phillies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/11/19,08/11/19,04:05 PM,07:05 PM,FALSE,TRUE,08/11/19,12:05 PM,03:05 PM,FREE,BUSY
08/13/19,06:45 PM,09:45 PM,Athletics at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/13/19,08/14/19,09:45 PM,12:45 AM,FALSE,TRUE,08/13/19,05:45 PM,08:45 PM,FREE,BUSY
08/14/19,12:45 PM,03:45 PM,Athletics at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/14/19,08/14/19,03:45 PM,06:45 PM,FALSE,TRUE,08/14/19,11:45 AM,02:45 PM,FREE,BUSY
08/26/19,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/26/19,08/27/19,09:45 PM,12:45 AM,FALSE,TRUE,08/26/19,05:45 PM,08:45 PM,FREE,BUSY
08/27/19,06:45 PM,09:45 PM,D-backs at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/27/19,08/28/19,09:45 PM,12:45 AM,FALSE,TRUE,08/27/19,05:45 PM,08:45 PM,FREE,BUSY
08/29/19,06:45 PM,09:45 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/29/19,08/30/19,09:45 PM,12:45 AM,FALSE,TRUE,08/29/19,05:45 PM,08:45 PM,FREE,BUSY
08/30/19,07:15 PM,10:15 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/30/19,08/31/19,10:15 PM,01:15 AM,FALSE,TRUE,08/30/19,06:15 PM,09:15 PM,FREE,BUSY
08/31/19,06:05 PM,09:05 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/31/19,09/01/19,09:05 PM,12:05 AM,FALSE,TRUE,08/31/19,05:05 PM,08:05 PM,FREE,BUSY
09/01/19,01:05 PM,04:05 PM,Padres at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/01/19,09/01/19,04:05 PM,07:05 PM,FALSE,TRUE,09/01/19,12:05 PM,03:05 PM,FREE,BUSY
09/09/19,06:45 PM,09:45 PM,Pirates at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/09/19,09/10/19,09:45 PM,12:45 AM,FALSE,TRUE,09/09/19,05:45 PM,08:45 PM,FREE,BUSY
09/10/19,06:45 PM,09:45 PM,Pirates at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/10/19,09/11/19,09:45 PM,12:45 AM,FALSE,TRUE,09/10/19,05:45 PM,08:45 PM,FREE,BUSY
09/11/19,06:45 PM,09:45 PM,Pirates at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/11/19,09/12/19,09:45 PM,12:45 AM,FALSE,TRUE,09/11/19,05:45 PM,08:45 PM,FREE,BUSY
09/12/19,12:45 PM,03:45 PM,Pirates at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/12/19,09/12/19,03:45 PM,06:45 PM,FALSE,TRUE,09/12/19,11:45 AM,02:45 PM,FREE,BUSY
09/13/19,07:15 PM,10:15 PM,Marlins at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/13/19,09/14/19,10:15 PM,01:15 AM,FALSE,TRUE,09/13/19,06:15 PM,09:15 PM,FREE,BUSY
09/14/19,06:05 PM,09:05 PM,Marlins at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/14/19,09/15/19,09:05 PM,12:05 AM,FALSE,TRUE,09/14/19,05:05 PM,08:05 PM,FREE,BUSY
09/15/19,01:05 PM,04:05 PM,Marlins at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/15/19,09/15/19,04:05 PM,07:05 PM,FALSE,TRUE,09/15/19,12:05 PM,03:05 PM,FREE,BUSY
09/24/19,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/24/19,09/25/19,09:45 PM,12:45 AM,FALSE,TRUE,09/24/19,05:45 PM,08:45 PM,FREE,BUSY
09/25/19,06:45 PM,09:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/25/19,09/26/19,09:45 PM,12:45 AM,FALSE,TRUE,09/25/19,05:45 PM,08:45 PM,FREE,BUSY
09/26/19,12:45 PM,03:45 PM,Rockies at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/26/19,09/26/19,03:45 PM,06:45 PM,FALSE,TRUE,09/26/19,11:45 AM,02:45 PM,FREE,BUSY
09/27/19,07:15 PM,10:15 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/27/19,09/28/19,10:15 PM,01:15 AM,FALSE,TRUE,09/27/19,06:15 PM,09:15 PM,FREE,BUSY
09/28/19,01:05 PM,04:05 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/28/19,09/28/19,04:05 PM,07:05 PM,FALSE,TRUE,09/28/19,12:05 PM,03:05 PM,FREE,BUSY
09/29/19,12:05 PM,03:05 PM,Dodgers at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/29/19,09/29/19,03:05 PM,06:05 PM,FALSE,TRUE,09/29/19,11:05 AM,02:05 PM,FREE,BUSY
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
