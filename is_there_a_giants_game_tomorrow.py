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
CSV_DATA = '''START DATE,START TIME,START TIME ET,SUBJECT,LOCATION,DESCRIPTION,END DATE,END DATE ET,END TIME,END TIME ET,REMINDER OFF,REMINDER ON,REMINDER DATE,REMINDER TIME,REMINDER TIME ET,SHOWTIMEAS FREE,SHOWTIMEAS BUSY
03/30/17,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,03/30/17,03/31/17,10:15 PM,01:15 AM,FALSE,TRUE,03/30/17,06:15 PM,09:15 PM,FREE,BUSY
03/31/17,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,03/31/17,04/01/17,10:15 PM,01:15 AM,FALSE,TRUE,03/31/17,06:15 PM,09:15 PM,FREE,BUSY
04/10/17,01:35 PM,04:35 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA- MLBN ----- Local Radio: KNBR 680- KXZM 93.7,04/10/17,04/10/17,04:35 PM,07:35 PM,FALSE,TRUE,04/10/17,12:35 PM,03:35 PM,FREE,BUSY
04/11/17,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA- MLBN ----- Local Radio: KNBR 680- KXZM 93.7,04/11/17,04/12/17,10:15 PM,01:15 AM,FALSE,TRUE,04/11/17,06:15 PM,09:15 PM,FREE,BUSY
04/12/17,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/12/17,04/13/17,10:15 PM,01:15 AM,FALSE,TRUE,04/12/17,06:15 PM,09:15 PM,FREE,BUSY
04/13/17,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/13/17,04/14/17,10:15 PM,01:15 AM,FALSE,TRUE,04/13/17,06:15 PM,09:15 PM,FREE,BUSY
04/14/17,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,04/14/17,04/15/17,10:15 PM,01:15 AM,FALSE,TRUE,04/14/17,06:15 PM,09:15 PM,FREE,BUSY
04/15/17,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/15/17,04/15/17,04:05 PM,07:05 PM,FALSE,TRUE,04/15/17,12:05 PM,03:05 PM,FREE,BUSY
04/16/17,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/16/17,04/16/17,04:05 PM,07:05 PM,FALSE,TRUE,04/16/17,12:05 PM,03:05 PM,FREE,BUSY
04/24/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA- MLBN ----- Local Radio: KNBR 680- KXZM 93.7,04/24/17,04/25/17,10:15 PM,01:15 AM,FALSE,TRUE,04/24/17,06:15 PM,09:15 PM,FREE,BUSY
04/25/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/25/17,04/26/17,10:15 PM,01:15 AM,FALSE,TRUE,04/25/17,06:15 PM,09:15 PM,FREE,BUSY
04/26/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area- MLBN ----- Local Radio: KNBR 680- KXZM 93.7,04/26/17,04/27/17,10:15 PM,01:15 AM,FALSE,TRUE,04/26/17,06:15 PM,09:15 PM,FREE,BUSY
04/27/17,12:45 PM,03:45 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/27/17,04/27/17,03:45 PM,06:45 PM,FALSE,TRUE,04/27/17,11:45 AM,02:45 PM,FREE,BUSY
04/28/17,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/28/17,04/29/17,10:15 PM,01:15 AM,FALSE,TRUE,04/28/17,06:15 PM,09:15 PM,FREE,BUSY
04/29/17,06:05 PM,09:05 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA- MLBN ----- Local Radio: KNBR 680- KXZM 93.7,04/29/17,04/30/17,09:05 PM,12:05 AM,FALSE,TRUE,04/29/17,05:05 PM,08:05 PM,FREE,BUSY
04/30/17,01:05 PM,04:05 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,04/30/17,04/30/17,04:05 PM,07:05 PM,FALSE,TRUE,04/30/17,12:05 PM,03:05 PM,FREE,BUSY
05/11/17,07:15 PM,10:15 PM,Reds at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/11/17,05/12/17,10:15 PM,01:15 AM,FALSE,TRUE,05/11/17,06:15 PM,09:15 PM,FREE,BUSY
05/12/17,07:15 PM,10:15 PM,Reds at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/12/17,05/13/17,10:15 PM,01:15 AM,FALSE,TRUE,05/12/17,06:15 PM,09:15 PM,FREE,BUSY
05/13/17,01:05 PM,04:05 PM,Reds at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/13/17,05/13/17,04:05 PM,07:05 PM,FALSE,TRUE,05/13/17,12:05 PM,03:05 PM,FREE,BUSY
05/14/17,01:05 PM,04:05 PM,Reds at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/14/17,05/14/17,04:05 PM,07:05 PM,FALSE,TRUE,05/14/17,12:05 PM,03:05 PM,FREE,BUSY
05/15/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/15/17,05/16/17,10:15 PM,01:15 AM,FALSE,TRUE,05/15/17,06:15 PM,09:15 PM,FREE,BUSY
05/16/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/16/17,05/17/17,10:15 PM,01:15 AM,FALSE,TRUE,05/16/17,06:15 PM,09:15 PM,FREE,BUSY
05/17/17,12:45 PM,03:45 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/17/17,05/17/17,03:45 PM,06:45 PM,FALSE,TRUE,05/17/17,11:45 AM,02:45 PM,FREE,BUSY
05/26/17,07:15 PM,10:15 PM,Braves at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/26/17,05/27/17,10:15 PM,01:15 AM,FALSE,TRUE,05/26/17,06:15 PM,09:15 PM,FREE,BUSY
05/27/17,07:05 PM,10:05 PM,Braves at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,05/27/17,05/28/17,10:05 PM,01:05 AM,FALSE,TRUE,05/27/17,06:05 PM,09:05 PM,FREE,BUSY
05/28/17,01:05 PM,04:05 PM,Braves at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/28/17,05/28/17,04:05 PM,07:05 PM,FALSE,TRUE,05/28/17,12:05 PM,03:05 PM,FREE,BUSY
05/29/17,01:05 PM,04:05 PM,Nationals at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/29/17,05/29/17,04:05 PM,07:05 PM,FALSE,TRUE,05/29/17,12:05 PM,03:05 PM,FREE,BUSY
05/30/17,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,05/30/17,05/31/17,10:15 PM,01:15 AM,FALSE,TRUE,05/30/17,06:15 PM,09:15 PM,FREE,BUSY
05/31/17,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,05/31/17,06/01/17,10:15 PM,01:15 AM,FALSE,TRUE,05/31/17,06:15 PM,09:15 PM,FREE,BUSY
06/09/17,07:15 PM,10:15 PM,Twins at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,06/09/17,06/10/17,10:15 PM,01:15 AM,FALSE,TRUE,06/09/17,06:15 PM,09:15 PM,FREE,BUSY
06/10/17,01:05 PM,04:05 PM,Twins at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/10/17,06/10/17,04:05 PM,07:05 PM,FALSE,TRUE,06/10/17,12:05 PM,03:05 PM,FREE,BUSY
06/11/17,01:05 PM,04:05 PM,Twins at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/11/17,06/11/17,04:05 PM,07:05 PM,FALSE,TRUE,06/11/17,12:05 PM,03:05 PM,FREE,BUSY
06/13/17,07:15 PM,10:15 PM,Royals at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/13/17,06/14/17,10:15 PM,01:15 AM,FALSE,TRUE,06/13/17,06:15 PM,09:15 PM,FREE,BUSY
06/14/17,12:45 PM,03:45 PM,Royals at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/14/17,06/14/17,03:45 PM,06:45 PM,FALSE,TRUE,06/14/17,11:45 AM,02:45 PM,FREE,BUSY
06/23/17,07:15 PM,10:15 PM,Mets at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,06/23/17,06/24/17,10:15 PM,01:15 AM,FALSE,TRUE,06/23/17,06:15 PM,09:15 PM,FREE,BUSY
06/24/17,04:15 PM,07:15 PM,Mets at Giants,AT&T Park - San Francisco,Local TV: FOX ----- Local Radio: KNBR 680- KXZM 93.7,06/24/17,06/24/17,07:15 PM,10:15 PM,FALSE,TRUE,06/24/17,03:15 PM,06:15 PM,FREE,BUSY
06/25/17,01:05 PM,04:05 PM,Mets at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/25/17,06/25/17,04:05 PM,07:05 PM,FALSE,TRUE,06/25/17,12:05 PM,03:05 PM,FREE,BUSY
06/26/17,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/26/17,06/27/17,10:15 PM,01:15 AM,FALSE,TRUE,06/26/17,06:15 PM,09:15 PM,FREE,BUSY
06/27/17,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/27/17,06/28/17,10:15 PM,01:15 AM,FALSE,TRUE,06/27/17,06:15 PM,09:15 PM,FREE,BUSY
06/28/17,12:45 PM,03:45 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,06/28/17,06/28/17,03:45 PM,06:45 PM,FALSE,TRUE,06/28/17,11:45 AM,02:45 PM,FREE,BUSY
07/07/17,07:15 PM,10:15 PM,Marlins at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/07/17,07/08/17,10:15 PM,01:15 AM,FALSE,TRUE,07/07/17,06:15 PM,09:15 PM,FREE,BUSY
07/08/17,07:05 PM,10:05 PM,Marlins at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/08/17,07/09/17,10:05 PM,01:05 AM,FALSE,TRUE,07/08/17,06:05 PM,09:05 PM,FREE,BUSY
07/09/17,01:05 PM,04:05 PM,Marlins at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/09/17,07/09/17,04:05 PM,07:05 PM,FALSE,TRUE,07/09/17,12:05 PM,03:05 PM,FREE,BUSY
07/17/17,07:15 PM,10:15 PM,Indians at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/17/17,07/18/17,10:15 PM,01:15 AM,FALSE,TRUE,07/17/17,06:15 PM,09:15 PM,FREE,BUSY
07/18/17,07:15 PM,10:15 PM,Indians at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/18/17,07/19/17,10:15 PM,01:15 AM,FALSE,TRUE,07/18/17,06:15 PM,09:15 PM,FREE,BUSY
07/19/17,12:45 PM,03:45 PM,Indians at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/19/17,07/19/17,03:45 PM,06:45 PM,FALSE,TRUE,07/19/17,11:45 AM,02:45 PM,FREE,BUSY
07/20/17,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,07/20/17,07/21/17,10:15 PM,01:15 AM,FALSE,TRUE,07/20/17,06:15 PM,09:15 PM,FREE,BUSY
07/21/17,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/21/17,07/22/17,10:15 PM,01:15 AM,FALSE,TRUE,07/21/17,06:15 PM,09:15 PM,FREE,BUSY
07/22/17,01:05 PM,04:05 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/22/17,07/22/17,04:05 PM,07:05 PM,FALSE,TRUE,07/22/17,12:05 PM,03:05 PM,FREE,BUSY
07/23/17,01:05 PM,04:05 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/23/17,07/23/17,04:05 PM,07:05 PM,FALSE,TRUE,07/23/17,12:05 PM,03:05 PM,FREE,BUSY
07/24/17,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/24/17,07/25/17,10:15 PM,01:15 AM,FALSE,TRUE,07/24/17,06:15 PM,09:15 PM,FREE,BUSY
07/25/17,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/25/17,07/26/17,10:15 PM,01:15 AM,FALSE,TRUE,07/25/17,06:15 PM,09:15 PM,FREE,BUSY
07/26/17,12:45 PM,03:45 PM,Pirates at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,07/26/17,07/26/17,03:45 PM,06:45 PM,FALSE,TRUE,07/26/17,11:45 AM,02:45 PM,FREE,BUSY
08/02/17,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/02/17,08/03/17,10:15 PM,01:15 AM,FALSE,TRUE,08/02/17,06:15 PM,09:15 PM,FREE,BUSY
08/03/17,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/03/17,08/04/17,10:15 PM,01:15 AM,FALSE,TRUE,08/03/17,06:15 PM,09:15 PM,FREE,BUSY
08/04/17,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/04/17,08/05/17,10:15 PM,01:15 AM,FALSE,TRUE,08/04/17,06:15 PM,09:15 PM,FREE,BUSY
08/05/17,06:05 PM,09:05 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/05/17,08/06/17,09:05 PM,12:05 AM,FALSE,TRUE,08/05/17,05:05 PM,08:05 PM,FREE,BUSY
08/06/17,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/06/17,08/06/17,04:05 PM,07:05 PM,FALSE,TRUE,08/06/17,12:05 PM,03:05 PM,FREE,BUSY
08/07/17,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,08/07/17,08/08/17,10:15 PM,01:15 AM,FALSE,TRUE,08/07/17,06:15 PM,09:15 PM,FREE,BUSY
08/08/17,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/08/17,08/09/17,10:15 PM,01:15 AM,FALSE,TRUE,08/08/17,06:15 PM,09:15 PM,FREE,BUSY
08/09/17,12:45 PM,03:45 PM,Cubs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/09/17,08/09/17,03:45 PM,06:45 PM,FALSE,TRUE,08/09/17,11:45 AM,02:45 PM,FREE,BUSY
08/17/17,07:15 PM,10:15 PM,Phillies at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,08/17/17,08/18/17,10:15 PM,01:15 AM,FALSE,TRUE,08/17/17,06:15 PM,09:15 PM,FREE,BUSY
08/18/17,07:15 PM,10:15 PM,Phillies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/18/17,08/19/17,10:15 PM,01:15 AM,FALSE,TRUE,08/18/17,06:15 PM,09:15 PM,FREE,BUSY
08/19/17,06:05 PM,09:05 PM,Phillies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/19/17,08/20/17,09:05 PM,12:05 AM,FALSE,TRUE,08/19/17,05:05 PM,08:05 PM,FREE,BUSY
08/20/17,01:05 PM,04:05 PM,Phillies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/20/17,08/20/17,04:05 PM,07:05 PM,FALSE,TRUE,08/20/17,12:05 PM,03:05 PM,FREE,BUSY
08/21/17,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/21/17,08/22/17,10:15 PM,01:15 AM,FALSE,TRUE,08/21/17,06:15 PM,09:15 PM,FREE,BUSY
08/22/17,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/22/17,08/23/17,10:15 PM,01:15 AM,FALSE,TRUE,08/22/17,06:15 PM,09:15 PM,FREE,BUSY
08/23/17,12:45 PM,03:45 PM,Brewers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,08/23/17,08/23/17,03:45 PM,06:45 PM,FALSE,TRUE,08/23/17,11:45 AM,02:45 PM,FREE,BUSY
08/31/17,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,08/31/17,09/01/17,10:15 PM,01:15 AM,FALSE,TRUE,08/31/17,06:15 PM,09:15 PM,FREE,BUSY
09/01/17,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/01/17,09/02/17,10:15 PM,01:15 AM,FALSE,TRUE,09/01/17,06:15 PM,09:15 PM,FREE,BUSY
09/02/17,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park - San Francisco,Local TV: CSBA- FS1 ----- Local Radio: KNBR 680- KXZM 93.7,09/02/17,09/02/17,04:05 PM,07:05 PM,FALSE,TRUE,09/02/17,12:05 PM,03:05 PM,FREE,BUSY
09/03/17,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/03/17,09/03/17,04:05 PM,07:05 PM,FALSE,TRUE,09/03/17,12:05 PM,03:05 PM,FREE,BUSY
09/11/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/11/17,09/12/17,10:15 PM,01:15 AM,FALSE,TRUE,09/11/17,06:15 PM,09:15 PM,FREE,BUSY
09/12/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/12/17,09/13/17,10:15 PM,01:15 AM,FALSE,TRUE,09/12/17,06:15 PM,09:15 PM,FREE,BUSY
09/13/17,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/13/17,09/14/17,10:15 PM,01:15 AM,FALSE,TRUE,09/13/17,06:15 PM,09:15 PM,FREE,BUSY
09/15/17,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/15/17,09/16/17,10:15 PM,01:15 AM,FALSE,TRUE,09/15/17,06:15 PM,09:15 PM,FREE,BUSY
09/16/17,06:05 PM,09:05 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: NBC Bay Area ----- Local Radio: KNBR 680- KXZM 93.7,09/16/17,09/17/17,09:05 PM,12:05 AM,FALSE,TRUE,09/16/17,05:05 PM,08:05 PM,FREE,BUSY
09/17/17,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/17/17,09/17/17,04:05 PM,07:05 PM,FALSE,TRUE,09/17/17,12:05 PM,03:05 PM,FREE,BUSY
09/19/17,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/19/17,09/20/17,10:15 PM,01:15 AM,FALSE,TRUE,09/19/17,06:15 PM,09:15 PM,FREE,BUSY
09/20/17,12:45 PM,03:45 PM,Rockies at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/20/17,09/20/17,03:45 PM,06:45 PM,FALSE,TRUE,09/20/17,11:45 AM,02:45 PM,FREE,BUSY
09/29/17,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/29/17,09/30/17,10:15 PM,01:15 AM,FALSE,TRUE,09/29/17,06:15 PM,09:15 PM,FREE,BUSY
09/30/17,01:05 PM,04:05 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,09/30/17,09/30/17,04:05 PM,07:05 PM,FALSE,TRUE,09/30/17,12:05 PM,03:05 PM,FREE,BUSY
10/01/17,12:05 PM,03:05 PM,Padres at Giants,AT&T Park - San Francisco,Local TV: CSBA ----- Local Radio: KNBR 680- KXZM 93.7,10/01/17,10/01/17,03:05 PM,06:05 PM,FALSE,TRUE,10/01/17,11:05 AM,02:05 PM,FREE,BUSY'''

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
