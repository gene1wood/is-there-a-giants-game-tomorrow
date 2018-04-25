#!/bin/env python

import csv
from datetime import time, datetime, timedelta
import logging
import json
import pyzmail
import sys

START_DATE = "START DATE"
START_TIME = "START TIME"

# http://mlb.mlb.com/soa/ical/schedule.csv?home_team_id=137&season=2015
# http://mlb.mlb.com/ticketing-client/csv/EventTicketPromotionPrice.tiksrv?team_id=137&home_team_id=137&display_in=singlegame&ticket_category=Tickets&site_section=Default&sub_category=Default&leave_empty_games=true&event_type=T&event_type=Y
# http://www.ticketing-client.com/ticketing-client/csv/EventTicketPromotionPrice.tiksrv?team_id=137&home_team_id=137&display_in=singlegame&ticket_category=Tickets&site_section=Default&sub_category=Default&leave_empty_games=true&event_type=T
CSV_DATA = '''START DATE,START TIME,START TIME ET,SUBJECT,LOCATION,DESCRIPTION,END DATE,END DATE ET,END TIME,END TIME ET,REMINDER OFF,REMINDER ON,REMINDER DATE,REMINDER TIME,REMINDER TIME ET,SHOWTIMEAS FREE,SHOWTIMEAS BUSY
03/26/18,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/26/18,03/27/18,10:15 PM,01:15 AM,FALSE,TRUE,03/26/18,06:15 PM,09:15 PM,FREE,BUSY
03/27/18,06:05 PM,09:05 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA- NBCS BA+ ----- Local Radio: KNBR 680",03/27/18,03/28/18,09:05 PM,12:05 AM,FALSE,TRUE,03/27/18,05:05 PM,08:05 PM,FREE,BUSY
04/03/18,01:35 PM,04:35 PM,Mariners at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA- MLBN (out-of-market only) ----- Local Radio: KNBR 680- KXZM 93.7",04/03/18,04/03/18,04:35 PM,07:35 PM,FALSE,TRUE,04/03/18,12:35 PM,03:35 PM,FREE,BUSY
04/04/18,04:15 PM,07:15 PM,Mariners at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/04/18,04/04/18,07:15 PM,10:15 PM,FALSE,TRUE,04/04/18,03:15 PM,06:15 PM,FREE,BUSY
04/07/18,03:05 PM,06:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/07/18,04/07/18,06:05 PM,09:05 PM,FALSE,TRUE,04/07/18,02:05 PM,05:05 PM,FREE,BUSY
04/08/18,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/08/18,04/08/18,04:05 PM,07:05 PM,FALSE,TRUE,04/08/18,12:05 PM,03:05 PM,FREE,BUSY
04/09/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/09/18,04/10/18,10:15 PM,01:15 AM,FALSE,TRUE,04/09/18,06:15 PM,09:15 PM,FREE,BUSY
04/10/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA+ ----- Local Radio: KNBR 680- KXZM 93.7",04/10/18,04/11/18,10:15 PM,01:15 AM,FALSE,TRUE,04/10/18,06:15 PM,09:15 PM,FREE,BUSY
04/11/18,12:45 PM,03:45 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/11/18,04/11/18,03:45 PM,06:45 PM,FALSE,TRUE,04/11/18,11:45 AM,02:45 PM,FREE,BUSY
04/23/18,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA- MLBN (out-of-market only) ----- Local Radio: KNBR 680- KXZM 93.7",04/23/18,04/24/18,10:15 PM,01:15 AM,FALSE,TRUE,04/23/18,06:15 PM,09:15 PM,FREE,BUSY
04/24/18,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/24/18,04/25/18,10:15 PM,01:15 AM,FALSE,TRUE,04/24/18,06:15 PM,09:15 PM,FREE,BUSY
04/25/18,12:45 PM,03:45 PM,Nationals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/25/18,04/25/18,03:45 PM,06:45 PM,FALSE,TRUE,04/25/18,11:45 AM,02:45 PM,FREE,BUSY
04/27/18,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",04/27/18,04/28/18,10:15 PM,01:15 AM,FALSE,TRUE,04/27/18,06:15 PM,09:15 PM,FREE,BUSY
04/28/18,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",04/28/18,04/28/18,04:05 PM,07:05 PM,FALSE,TRUE,04/28/18,12:05 PM,03:05 PM,FREE,BUSY
04/28/18,07:05 PM,10:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/28/18,04/29/18,10:05 PM,01:05 AM,FALSE,TRUE,04/28/18,06:05 PM,09:05 PM,FREE,BUSY
04/29/18,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",04/29/18,04/29/18,04:05 PM,07:05 PM,FALSE,TRUE,04/29/18,12:05 PM,03:05 PM,FREE,BUSY
04/30/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA- MLBN (out-of-market only) ----- Local Radio: KNBR 680- KXZM 93.7",04/30/18,05/01/18,10:15 PM,01:15 AM,FALSE,TRUE,04/30/18,06:15 PM,09:15 PM,FREE,BUSY
05/01/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/01/18,05/02/18,10:15 PM,01:15 AM,FALSE,TRUE,05/01/18,06:15 PM,09:15 PM,FREE,BUSY
05/02/18,12:45 PM,03:45 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/02/18,05/02/18,03:45 PM,06:45 PM,FALSE,TRUE,05/02/18,11:45 AM,02:45 PM,FREE,BUSY
05/14/18,07:15 PM,10:15 PM,Reds at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/14/18,05/15/18,10:15 PM,01:15 AM,FALSE,TRUE,05/14/18,06:15 PM,09:15 PM,FREE,BUSY
05/15/18,07:15 PM,10:15 PM,Reds at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/15/18,05/16/18,10:15 PM,01:15 AM,FALSE,TRUE,05/15/18,06:15 PM,09:15 PM,FREE,BUSY
05/16/18,12:45 PM,03:45 PM,Reds at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/16/18,05/16/18,03:45 PM,06:45 PM,FALSE,TRUE,05/16/18,11:45 AM,02:45 PM,FREE,BUSY
05/17/18,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/17/18,05/18/18,10:15 PM,01:15 AM,FALSE,TRUE,05/17/18,06:15 PM,09:15 PM,FREE,BUSY
05/18/18,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",05/18/18,05/19/18,10:15 PM,01:15 AM,FALSE,TRUE,05/18/18,06:15 PM,09:15 PM,FREE,BUSY
05/19/18,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/19/18,05/19/18,04:05 PM,07:05 PM,FALSE,TRUE,05/19/18,12:05 PM,03:05 PM,FREE,BUSY
05/20/18,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",05/20/18,05/20/18,04:05 PM,07:05 PM,FALSE,TRUE,05/20/18,12:05 PM,03:05 PM,FREE,BUSY
06/01/18,07:15 PM,10:15 PM,Phillies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/01/18,06/02/18,10:15 PM,01:15 AM,FALSE,TRUE,06/01/18,06:15 PM,09:15 PM,FREE,BUSY
06/02/18,07:05 PM,10:05 PM,Phillies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/02/18,06/03/18,10:05 PM,01:05 AM,FALSE,TRUE,06/02/18,06:05 PM,09:05 PM,FREE,BUSY
06/03/18,01:05 PM,04:05 PM,Phillies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/03/18,06/03/18,04:05 PM,07:05 PM,FALSE,TRUE,06/03/18,12:05 PM,03:05 PM,FREE,BUSY
06/04/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/04/18,06/05/18,10:15 PM,01:15 AM,FALSE,TRUE,06/04/18,06:15 PM,09:15 PM,FREE,BUSY
06/05/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/05/18,06/06/18,10:15 PM,01:15 AM,FALSE,TRUE,06/05/18,06:15 PM,09:15 PM,FREE,BUSY
06/06/18,12:45 PM,03:45 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/06/18,06/06/18,03:45 PM,06:45 PM,FALSE,TRUE,06/06/18,11:45 AM,02:45 PM,FREE,BUSY
06/18/18,07:15 PM,10:15 PM,Marlins at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/18/18,06/19/18,10:15 PM,01:15 AM,FALSE,TRUE,06/18/18,06:15 PM,09:15 PM,FREE,BUSY
06/19/18,07:15 PM,10:15 PM,Marlins at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/19/18,06/20/18,10:15 PM,01:15 AM,FALSE,TRUE,06/19/18,06:15 PM,09:15 PM,FREE,BUSY
06/20/18,12:45 PM,03:45 PM,Marlins at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/20/18,06/20/18,03:45 PM,06:45 PM,FALSE,TRUE,06/20/18,11:45 AM,02:45 PM,FREE,BUSY
06/21/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/21/18,06/22/18,10:15 PM,01:15 AM,FALSE,TRUE,06/21/18,06:15 PM,09:15 PM,FREE,BUSY
06/22/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",06/22/18,06/23/18,10:15 PM,01:15 AM,FALSE,TRUE,06/22/18,06:15 PM,09:15 PM,FREE,BUSY
06/23/18,01:05 PM,04:05 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/23/18,06/23/18,04:05 PM,07:05 PM,FALSE,TRUE,06/23/18,12:05 PM,03:05 PM,FREE,BUSY
06/24/18,01:05 PM,04:05 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/24/18,06/24/18,04:05 PM,07:05 PM,FALSE,TRUE,06/24/18,12:05 PM,03:05 PM,FREE,BUSY
06/26/18,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/26/18,06/27/18,10:15 PM,01:15 AM,FALSE,TRUE,06/26/18,06:15 PM,09:15 PM,FREE,BUSY
06/27/18,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/27/18,06/28/18,10:15 PM,01:15 AM,FALSE,TRUE,06/27/18,06:15 PM,09:15 PM,FREE,BUSY
06/28/18,12:45 PM,03:45 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",06/28/18,06/28/18,03:45 PM,06:45 PM,FALSE,TRUE,06/28/18,11:45 AM,02:45 PM,FREE,BUSY
07/05/18,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/05/18,07/06/18,10:15 PM,01:15 AM,FALSE,TRUE,07/05/18,06:15 PM,09:15 PM,FREE,BUSY
07/06/18,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/06/18,07/07/18,10:15 PM,01:15 AM,FALSE,TRUE,07/06/18,06:15 PM,09:15 PM,FREE,BUSY
07/07/18,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/07/18,07/07/18,04:05 PM,07:05 PM,FALSE,TRUE,07/07/18,12:05 PM,03:05 PM,FREE,BUSY
07/08/18,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/08/18,07/08/18,04:05 PM,07:05 PM,FALSE,TRUE,07/08/18,12:05 PM,03:05 PM,FREE,BUSY
07/09/18,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/09/18,07/10/18,10:15 PM,01:15 AM,FALSE,TRUE,07/09/18,06:15 PM,09:15 PM,FREE,BUSY
07/10/18,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/10/18,07/11/18,10:15 PM,01:15 AM,FALSE,TRUE,07/10/18,06:15 PM,09:15 PM,FREE,BUSY
07/11/18,12:45 PM,03:45 PM,Cubs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/11/18,07/11/18,03:45 PM,06:45 PM,FALSE,TRUE,07/11/18,11:45 AM,02:45 PM,FREE,BUSY
07/13/18,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/13/18,07/14/18,10:15 PM,01:15 AM,FALSE,TRUE,07/13/18,06:15 PM,09:15 PM,FREE,BUSY
07/14/18,07:05 PM,10:05 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/14/18,07/15/18,10:05 PM,01:05 AM,FALSE,TRUE,07/14/18,06:05 PM,09:05 PM,FREE,BUSY
07/15/18,01:05 PM,04:05 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/15/18,07/15/18,04:05 PM,07:05 PM,FALSE,TRUE,07/15/18,12:05 PM,03:05 PM,FREE,BUSY
07/26/18,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/26/18,07/27/18,10:15 PM,01:15 AM,FALSE,TRUE,07/26/18,06:15 PM,09:15 PM,FREE,BUSY
07/27/18,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",07/27/18,07/28/18,10:15 PM,01:15 AM,FALSE,TRUE,07/27/18,06:15 PM,09:15 PM,FREE,BUSY
07/28/18,06:05 PM,09:05 PM,Brewers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/28/18,07/29/18,09:05 PM,12:05 AM,FALSE,TRUE,07/28/18,05:05 PM,08:05 PM,FREE,BUSY
07/29/18,01:05 PM,04:05 PM,Brewers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",07/29/18,07/29/18,04:05 PM,07:05 PM,FALSE,TRUE,07/29/18,12:05 PM,03:05 PM,FREE,BUSY
08/06/18,07:15 PM,10:15 PM,Astros at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/06/18,08/07/18,10:15 PM,01:15 AM,FALSE,TRUE,08/06/18,06:15 PM,09:15 PM,FREE,BUSY
08/07/18,12:45 PM,03:45 PM,Astros at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/07/18,08/07/18,03:45 PM,06:45 PM,FALSE,TRUE,08/07/18,11:45 AM,02:45 PM,FREE,BUSY
08/09/18,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/09/18,08/10/18,10:15 PM,01:15 AM,FALSE,TRUE,08/09/18,06:15 PM,09:15 PM,FREE,BUSY
08/10/18,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/10/18,08/11/18,10:15 PM,01:15 AM,FALSE,TRUE,08/10/18,06:15 PM,09:15 PM,FREE,BUSY
08/11/18,06:05 PM,09:05 PM,Pirates at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/11/18,08/12/18,09:05 PM,12:05 AM,FALSE,TRUE,08/11/18,05:05 PM,08:05 PM,FREE,BUSY
08/12/18,01:05 PM,04:05 PM,Pirates at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/12/18,08/12/18,04:05 PM,07:05 PM,FALSE,TRUE,08/12/18,12:05 PM,03:05 PM,FREE,BUSY
08/24/18,07:15 PM,10:15 PM,Rangers at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",08/24/18,08/25/18,10:15 PM,01:15 AM,FALSE,TRUE,08/24/18,06:15 PM,09:15 PM,FREE,BUSY
08/25/18,01:05 PM,04:05 PM,Rangers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/25/18,08/25/18,04:05 PM,07:05 PM,FALSE,TRUE,08/25/18,12:05 PM,03:05 PM,FREE,BUSY
08/26/18,01:05 PM,04:05 PM,Rangers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/26/18,08/26/18,04:05 PM,07:05 PM,FALSE,TRUE,08/26/18,12:05 PM,03:05 PM,FREE,BUSY
08/27/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/27/18,08/28/18,10:15 PM,01:15 AM,FALSE,TRUE,08/27/18,06:15 PM,09:15 PM,FREE,BUSY
08/28/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/28/18,08/29/18,10:15 PM,01:15 AM,FALSE,TRUE,08/28/18,06:15 PM,09:15 PM,FREE,BUSY
08/29/18,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/29/18,08/30/18,10:15 PM,01:15 AM,FALSE,TRUE,08/29/18,06:15 PM,09:15 PM,FREE,BUSY
08/31/18,07:15 PM,10:15 PM,Mets at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",08/31/18,09/01/18,10:15 PM,01:15 AM,FALSE,TRUE,08/31/18,06:15 PM,09:15 PM,FREE,BUSY
09/01/18,01:05 PM,04:05 PM,Mets at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/01/18,09/01/18,04:05 PM,07:05 PM,FALSE,TRUE,09/01/18,12:05 PM,03:05 PM,FREE,BUSY
09/02/18,01:05 PM,04:05 PM,Mets at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/02/18,09/02/18,04:05 PM,07:05 PM,FALSE,TRUE,09/02/18,12:05 PM,03:05 PM,FREE,BUSY
09/10/18,07:15 PM,10:15 PM,Braves at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/10/18,09/11/18,10:15 PM,01:15 AM,FALSE,TRUE,09/10/18,06:15 PM,09:15 PM,FREE,BUSY
09/11/18,07:15 PM,10:15 PM,Braves at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/11/18,09/12/18,10:15 PM,01:15 AM,FALSE,TRUE,09/11/18,06:15 PM,09:15 PM,FREE,BUSY
09/12/18,12:45 PM,03:45 PM,Braves at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/12/18,09/12/18,03:45 PM,06:45 PM,FALSE,TRUE,09/12/18,11:45 AM,02:45 PM,FREE,BUSY
09/14/18,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",09/14/18,09/15/18,10:15 PM,01:15 AM,FALSE,TRUE,09/14/18,06:15 PM,09:15 PM,FREE,BUSY
09/15/18,06:05 PM,09:05 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/15/18,09/16/18,09:05 PM,12:05 AM,FALSE,TRUE,09/15/18,05:05 PM,08:05 PM,FREE,BUSY
09/16/18,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/16/18,09/16/18,04:05 PM,07:05 PM,FALSE,TRUE,09/16/18,12:05 PM,03:05 PM,FREE,BUSY
09/24/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/24/18,09/25/18,10:15 PM,01:15 AM,FALSE,TRUE,09/24/18,06:15 PM,09:15 PM,FREE,BUSY
09/25/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/25/18,09/26/18,10:15 PM,01:15 AM,FALSE,TRUE,09/25/18,06:15 PM,09:15 PM,FREE,BUSY
09/26/18,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/26/18,09/27/18,10:15 PM,01:15 AM,FALSE,TRUE,09/26/18,06:15 PM,09:15 PM,FREE,BUSY
09/28/18,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7",09/28/18,09/29/18,10:15 PM,01:15 AM,FALSE,TRUE,09/28/18,06:15 PM,09:15 PM,FREE,BUSY
09/29/18,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/29/18,09/29/18,04:05 PM,07:05 PM,FALSE,TRUE,09/29/18,12:05 PM,03:05 PM,FREE,BUSY
09/30/18,12:05 PM,03:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680- KXZM 93.7",09/30/18,09/30/18,03:05 PM,06:05 PM,FALSE,TRUE,09/30/18,11:05 AM,02:05 PM,FREE,BUSY'''

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
    compose_args = {'sender': ("Is there a Giants game tomorrow", SENDER),
                    'recipients': [RECIPIENT],
                    'subject': "There's a Giants game tomorrow",
                    'default_charset': 'iso-8859-1',
                    'text': (text, 'us-ascii')}
    payload, mail_from, rcpt_to, msg_id=pyzmail.compose_mail(**compose_args)
    return pyzmail.send_mail(payload, 
                             mail_from, 
                             rcpt_to, 
                             'localhost')

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
