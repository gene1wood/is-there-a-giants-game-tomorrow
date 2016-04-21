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
03/02/16,12:05 PM,03:05 PM,Angels at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/02/16,03/02/16,03:05 PM,06:05 PM,FALSE,TRUE,03/02/16,11:05 AM,02:05 PM,FREE,BUSY
03/03/16,12:05 PM,03:05 PM,Brewers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/03/16,03/03/16,03:05 PM,06:05 PM,FALSE,TRUE,03/03/16,11:05 AM,02:05 PM,FREE,BUSY
03/05/16,12:05 PM,03:05 PM,Rangers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/05/16,03/05/16,03:05 PM,06:05 PM,FALSE,TRUE,03/05/16,11:05 AM,02:05 PM,FREE,BUSY
03/06/16,12:05 PM,03:05 PM,Dodgers at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/06/16,03/06/16,03:05 PM,06:05 PM,FALSE,TRUE,03/06/16,11:05 AM,02:05 PM,FREE,BUSY
03/08/16,06:05 PM,09:05 PM,Reds at Giants,Scottsdale Stadium - Scottsdale,"Local TV: MLBN- CSN-BA ----- Local Radio: MLB.com",03/08/16,03/09/16,09:05 PM,12:05 AM,FALSE,TRUE,03/08/16,05:05 PM,08:05 PM,FREE,BUSY
03/09/16,12:05 PM,03:05 PM,Rockies at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/09/16,03/09/16,03:05 PM,06:05 PM,FALSE,TRUE,03/09/16,11:05 AM,02:05 PM,FREE,BUSY
03/11/16,12:05 PM,03:05 PM,Mariners at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/11/16,03/11/16,03:05 PM,06:05 PM,FALSE,TRUE,03/11/16,11:05 AM,02:05 PM,FREE,BUSY
03/12/16,12:05 PM,03:05 PM,D-backs at Giants,Scottsdale Stadium - Scottsdale,"Local TV: CSN-BA ----- Local Radio: KNBR 680",03/12/16,03/12/16,03:05 PM,06:05 PM,FALSE,TRUE,03/12/16,11:05 AM,02:05 PM,FREE,BUSY
03/13/16,03:05 PM,06:05 PM,Padres at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680",03/13/16,03/13/16,06:05 PM,09:05 PM,FALSE,TRUE,03/13/16,02:05 PM,05:05 PM,FREE,BUSY
03/18/16,07:05 PM,10:05 PM,Padres at Giants,Scottsdale Stadium - Scottsdale,"Local TV: NBC Bay Area- MLB.TV ----- Local Radio: MLB.com",03/18/16,03/19/16,10:05 PM,01:05 AM,FALSE,TRUE,03/18/16,06:05 PM,09:05 PM,FREE,BUSY
03/19/16,01:05 PM,04:05 PM,Athletics at Giants,Scottsdale Stadium - Scottsdale,"Local TV: CSN-BA- MLB.TV ----- Local Radio: KNBR 680",03/19/16,03/19/16,04:05 PM,07:05 PM,FALSE,TRUE,03/19/16,12:05 PM,03:05 PM,FREE,BUSY
03/21/16,01:05 PM,04:05 PM,Athletics at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/21/16,03/21/16,04:05 PM,07:05 PM,FALSE,TRUE,03/21/16,12:05 PM,03:05 PM,FREE,BUSY
03/24/16,04:05 PM,07:05 PM,Cubs at Giants,Scottsdale Stadium - Scottsdale,"Local TV: ESPN- MLB.TV ----- Local Radio: KNBR 680",03/24/16,03/24/16,07:05 PM,10:05 PM,FALSE,TRUE,03/24/16,03:05 PM,06:05 PM,FREE,BUSY
03/25/16,01:05 PM,04:05 PM,Royals at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: MLB.com",03/25/16,03/25/16,04:05 PM,07:05 PM,FALSE,TRUE,03/25/16,12:05 PM,03:05 PM,FREE,BUSY
03/27/16,01:05 PM,04:05 PM,White Sox at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",03/27/16,03/27/16,04:05 PM,07:05 PM,FALSE,TRUE,03/27/16,12:05 PM,03:05 PM,FREE,BUSY
03/28/16,07:05 PM,10:05 PM,D-backs at Giants,Scottsdale Stadium - Scottsdale,"Local TV: CSN-BA- MLB.TV ----- Local Radio: MLB.com",03/28/16,03/29/16,10:05 PM,01:05 AM,FALSE,TRUE,03/28/16,06:05 PM,09:05 PM,FREE,BUSY
03/31/16,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: CSN-BA- MLB.TV ----- Local Radio: KNBR 680",03/31/16,04/01/16,10:15 PM,01:15 AM,FALSE,TRUE,03/31/16,06:15 PM,09:15 PM,FREE,BUSY
04/01/16,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,"Local TV: NBC Bay Area- MLBN- MLB.TV ----- Local Radio: KNBR 680",04/01/16,04/02/16,10:15 PM,01:15 AM,FALSE,TRUE,04/01/16,06:15 PM,09:15 PM,FREE,BUSY
04/07/16,01:35 PM,04:35 PM,Dodgers at Giants,AT&T Park - San Francisco,"",04/07/16,04/07/16,04:35 PM,07:35 PM,FALSE,TRUE,04/07/16,12:35 PM,03:35 PM,FREE,BUSY
04/08/16,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,"",04/08/16,04/09/16,10:15 PM,01:15 AM,FALSE,TRUE,04/08/16,06:15 PM,09:15 PM,FREE,BUSY
04/09/16,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: FS1",04/09/16,04/09/16,04:05 PM,07:05 PM,FALSE,TRUE,04/09/16,12:05 PM,03:05 PM,FREE,BUSY
04/10/16,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"",04/10/16,04/10/16,04:05 PM,07:05 PM,FALSE,TRUE,04/10/16,12:05 PM,03:05 PM,FREE,BUSY
04/18/16,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"",04/18/16,04/19/16,10:15 PM,01:15 AM,FALSE,TRUE,04/18/16,06:15 PM,09:15 PM,FREE,BUSY
04/19/16,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"",04/19/16,04/20/16,10:15 PM,01:15 AM,FALSE,TRUE,04/19/16,06:15 PM,09:15 PM,FREE,BUSY
04/20/16,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"",04/20/16,04/21/16,10:15 PM,01:15 AM,FALSE,TRUE,04/20/16,06:15 PM,09:15 PM,FREE,BUSY
04/21/16,12:45 PM,03:45 PM,D-backs at Giants,AT&T Park - San Francisco,"",04/21/16,04/21/16,03:45 PM,06:45 PM,FALSE,TRUE,04/21/16,11:45 AM,02:45 PM,FREE,BUSY
04/22/16,07:15 PM,10:15 PM,Marlins at Giants,AT&T Park - San Francisco,"",04/22/16,04/23/16,10:15 PM,01:15 AM,FALSE,TRUE,04/22/16,06:15 PM,09:15 PM,FREE,BUSY
04/23/16,06:05 PM,09:05 PM,Marlins at Giants,AT&T Park - San Francisco,"",04/23/16,04/24/16,09:05 PM,12:05 AM,FALSE,TRUE,04/23/16,05:05 PM,08:05 PM,FREE,BUSY
04/24/16,01:05 PM,04:05 PM,Marlins at Giants,AT&T Park - San Francisco,"",04/24/16,04/24/16,04:05 PM,07:05 PM,FALSE,TRUE,04/24/16,12:05 PM,03:05 PM,FREE,BUSY
04/25/16,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"",04/25/16,04/26/16,10:15 PM,01:15 AM,FALSE,TRUE,04/25/16,06:15 PM,09:15 PM,FREE,BUSY
04/26/16,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"",04/26/16,04/27/16,10:15 PM,01:15 AM,FALSE,TRUE,04/26/16,06:15 PM,09:15 PM,FREE,BUSY
04/27/16,12:45 PM,03:45 PM,Padres at Giants,AT&T Park - San Francisco,"",04/27/16,04/27/16,03:45 PM,06:45 PM,FALSE,TRUE,04/27/16,11:45 AM,02:45 PM,FREE,BUSY
05/05/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",05/05/16,05/06/16,10:15 PM,01:15 AM,FALSE,TRUE,05/05/16,06:15 PM,09:15 PM,FREE,BUSY
05/06/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",05/06/16,05/07/16,10:15 PM,01:15 AM,FALSE,TRUE,05/06/16,06:15 PM,09:15 PM,FREE,BUSY
05/07/16,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,"",05/07/16,05/07/16,04:05 PM,07:05 PM,FALSE,TRUE,05/07/16,12:05 PM,03:05 PM,FREE,BUSY
05/08/16,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,"",05/08/16,05/08/16,04:05 PM,07:05 PM,FALSE,TRUE,05/08/16,12:05 PM,03:05 PM,FREE,BUSY
05/09/16,07:15 PM,10:15 PM,Blue Jays at Giants,AT&T Park - San Francisco,"",05/09/16,05/10/16,10:15 PM,01:15 AM,FALSE,TRUE,05/09/16,06:15 PM,09:15 PM,FREE,BUSY
05/10/16,07:15 PM,10:15 PM,Blue Jays at Giants,AT&T Park - San Francisco,"",05/10/16,05/11/16,10:15 PM,01:15 AM,FALSE,TRUE,05/10/16,06:15 PM,09:15 PM,FREE,BUSY
05/11/16,12:45 PM,03:45 PM,Blue Jays at Giants,AT&T Park - San Francisco,"",05/11/16,05/11/16,03:45 PM,06:45 PM,FALSE,TRUE,05/11/16,11:45 AM,02:45 PM,FREE,BUSY
05/20/16,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park - San Francisco,"",05/20/16,05/21/16,10:15 PM,01:15 AM,FALSE,TRUE,05/20/16,06:15 PM,09:15 PM,FREE,BUSY
05/21/16,04:15 PM,07:15 PM,Cubs at Giants,AT&T Park - San Francisco,"Local TV: FOX",05/21/16,05/21/16,07:15 PM,10:15 PM,FALSE,TRUE,05/21/16,03:15 PM,06:15 PM,FREE,BUSY
05/22/16,05:05 PM,08:05 PM,Cubs at Giants,AT&T Park - San Francisco,"Local TV: ESPN",05/22/16,05/22/16,08:05 PM,11:05 PM,FALSE,TRUE,05/22/16,04:05 PM,07:05 PM,FREE,BUSY
05/23/16,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"",05/23/16,05/24/16,10:15 PM,01:15 AM,FALSE,TRUE,05/23/16,06:15 PM,09:15 PM,FREE,BUSY
05/24/16,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"",05/24/16,05/25/16,10:15 PM,01:15 AM,FALSE,TRUE,05/24/16,06:15 PM,09:15 PM,FREE,BUSY
05/25/16,12:45 PM,03:45 PM,Padres at Giants,AT&T Park - San Francisco,"",05/25/16,05/25/16,03:45 PM,06:45 PM,FALSE,TRUE,05/25/16,11:45 AM,02:45 PM,FREE,BUSY
06/07/16,07:15 PM,10:15 PM,Red Sox at Giants,AT&T Park - San Francisco,"",06/07/16,06/08/16,10:15 PM,01:15 AM,FALSE,TRUE,06/07/16,06:15 PM,09:15 PM,FREE,BUSY
06/08/16,07:15 PM,10:15 PM,Red Sox at Giants,AT&T Park - San Francisco,"",06/08/16,06/09/16,10:15 PM,01:15 AM,FALSE,TRUE,06/08/16,06:15 PM,09:15 PM,FREE,BUSY
06/10/16,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,"",06/10/16,06/11/16,10:15 PM,01:15 AM,FALSE,TRUE,06/10/16,06:15 PM,09:15 PM,FREE,BUSY
06/11/16,04:15 PM,07:15 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: FOX",06/11/16,06/11/16,07:15 PM,10:15 PM,FALSE,TRUE,06/11/16,03:15 PM,06:15 PM,FREE,BUSY
06/12/16,05:30 PM,08:30 PM,Dodgers at Giants,AT&T Park - San Francisco,"Local TV: ESPN",06/12/16,06/12/16,08:30 PM,11:30 PM,FALSE,TRUE,06/12/16,04:30 PM,07:30 PM,FREE,BUSY
06/13/16,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park - San Francisco,"",06/13/16,06/14/16,10:15 PM,01:15 AM,FALSE,TRUE,06/13/16,06:15 PM,09:15 PM,FREE,BUSY
06/14/16,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park - San Francisco,"",06/14/16,06/15/16,10:15 PM,01:15 AM,FALSE,TRUE,06/14/16,06:15 PM,09:15 PM,FREE,BUSY
06/15/16,12:45 PM,03:45 PM,Brewers at Giants,AT&T Park - San Francisco,"",06/15/16,06/15/16,03:45 PM,06:45 PM,FALSE,TRUE,06/15/16,11:45 AM,02:45 PM,FREE,BUSY
06/24/16,07:15 PM,10:15 PM,Phillies at Giants,AT&T Park - San Francisco,"",06/24/16,06/25/16,10:15 PM,01:15 AM,FALSE,TRUE,06/24/16,06:15 PM,09:15 PM,FREE,BUSY
06/25/16,07:05 PM,10:05 PM,Phillies at Giants,AT&T Park - San Francisco,"",06/25/16,06/26/16,10:05 PM,01:05 AM,FALSE,TRUE,06/25/16,06:05 PM,09:05 PM,FREE,BUSY
06/26/16,01:05 PM,04:05 PM,Phillies at Giants,AT&T Park - San Francisco,"",06/26/16,06/26/16,04:05 PM,07:05 PM,FALSE,TRUE,06/26/16,12:05 PM,03:05 PM,FREE,BUSY
06/27/16,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,"",06/27/16,06/28/16,10:15 PM,01:15 AM,FALSE,TRUE,06/27/16,06:15 PM,09:15 PM,FREE,BUSY
06/28/16,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park - San Francisco,"",06/28/16,06/29/16,10:15 PM,01:15 AM,FALSE,TRUE,06/28/16,06:15 PM,09:15 PM,FREE,BUSY
07/04/16,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park - San Francisco,"",07/04/16,07/04/16,04:05 PM,07:05 PM,FALSE,TRUE,07/04/16,12:05 PM,03:05 PM,FREE,BUSY
07/05/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",07/05/16,07/06/16,10:15 PM,01:15 AM,FALSE,TRUE,07/05/16,06:15 PM,09:15 PM,FREE,BUSY
07/06/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",07/06/16,07/07/16,10:15 PM,01:15 AM,FALSE,TRUE,07/06/16,06:15 PM,09:15 PM,FREE,BUSY
07/08/16,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"",07/08/16,07/09/16,10:15 PM,01:15 AM,FALSE,TRUE,07/08/16,06:15 PM,09:15 PM,FREE,BUSY
07/09/16,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park - San Francisco,"",07/09/16,07/09/16,04:05 PM,07:05 PM,FALSE,TRUE,07/09/16,12:05 PM,03:05 PM,FREE,BUSY
07/10/16,05:00 PM,08:00 PM,D-backs at Giants,AT&T Park - San Francisco,"Local TV: ESPN",07/10/16,07/10/16,08:00 PM,11:00 PM,FALSE,TRUE,07/10/16,04:00 PM,07:00 PM,FREE,BUSY
07/12/16,07:00 PM,08:00 PM,American at National,Petco Park - San Diego,"",07/12/16,07/12/16,10:00 PM,11:00 PM,FALSE,TRUE,07/12/16,06:00 PM,07:00 PM,FREE,BUSY
07/25/16,07:15 PM,10:15 PM,Reds at Giants,AT&T Park - San Francisco,"",07/25/16,07/26/16,10:15 PM,01:15 AM,FALSE,TRUE,07/25/16,06:15 PM,09:15 PM,FREE,BUSY
07/26/16,07:15 PM,10:15 PM,Reds at Giants,AT&T Park - San Francisco,"",07/26/16,07/27/16,10:15 PM,01:15 AM,FALSE,TRUE,07/26/16,06:15 PM,09:15 PM,FREE,BUSY
07/27/16,12:45 PM,03:45 PM,Reds at Giants,AT&T Park - San Francisco,"",07/27/16,07/27/16,03:45 PM,06:45 PM,FALSE,TRUE,07/27/16,11:45 AM,02:45 PM,FREE,BUSY
07/28/16,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park - San Francisco,"",07/28/16,07/29/16,10:15 PM,01:15 AM,FALSE,TRUE,07/28/16,06:15 PM,09:15 PM,FREE,BUSY
07/29/16,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park - San Francisco,"",07/29/16,07/30/16,10:15 PM,01:15 AM,FALSE,TRUE,07/29/16,06:15 PM,09:15 PM,FREE,BUSY
07/30/16,01:05 PM,04:05 PM,Nationals at Giants,AT&T Park - San Francisco,"Local TV: FS1",07/30/16,07/30/16,04:05 PM,07:05 PM,FALSE,TRUE,07/30/16,12:05 PM,03:05 PM,FREE,BUSY
07/31/16,01:05 PM,04:05 PM,Nationals at Giants,AT&T Park - San Francisco,"",07/31/16,07/31/16,04:05 PM,07:05 PM,FALSE,TRUE,07/31/16,12:05 PM,03:05 PM,FREE,BUSY
08/12/16,07:15 PM,10:15 PM,Orioles at Giants,AT&T Park - San Francisco,"",08/12/16,08/13/16,10:15 PM,01:15 AM,FALSE,TRUE,08/12/16,06:15 PM,09:15 PM,FREE,BUSY
08/13/16,06:05 PM,09:05 PM,Orioles at Giants,AT&T Park - San Francisco,"",08/13/16,08/14/16,09:05 PM,12:05 AM,FALSE,TRUE,08/13/16,05:05 PM,08:05 PM,FREE,BUSY
08/14/16,01:05 PM,04:05 PM,Orioles at Giants,AT&T Park - San Francisco,"",08/14/16,08/14/16,04:05 PM,07:05 PM,FALSE,TRUE,08/14/16,12:05 PM,03:05 PM,FREE,BUSY
08/15/16,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park - San Francisco,"",08/15/16,08/16/16,10:15 PM,01:15 AM,FALSE,TRUE,08/15/16,06:15 PM,09:15 PM,FREE,BUSY
08/16/16,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park - San Francisco,"",08/16/16,08/17/16,10:15 PM,01:15 AM,FALSE,TRUE,08/16/16,06:15 PM,09:15 PM,FREE,BUSY
08/17/16,12:45 PM,03:45 PM,Pirates at Giants,AT&T Park - San Francisco,"",08/17/16,08/17/16,03:45 PM,06:45 PM,FALSE,TRUE,08/17/16,11:45 AM,02:45 PM,FREE,BUSY
08/18/16,07:15 PM,10:15 PM,Mets at Giants,AT&T Park - San Francisco,"",08/18/16,08/19/16,10:15 PM,01:15 AM,FALSE,TRUE,08/18/16,06:15 PM,09:15 PM,FREE,BUSY
08/19/16,07:15 PM,10:15 PM,Mets at Giants,AT&T Park - San Francisco,"",08/19/16,08/20/16,10:15 PM,01:15 AM,FALSE,TRUE,08/19/16,06:15 PM,09:15 PM,FREE,BUSY
08/20/16,01:05 PM,04:05 PM,Mets at Giants,AT&T Park - San Francisco,"Local TV: FS1",08/20/16,08/20/16,04:05 PM,07:05 PM,FALSE,TRUE,08/20/16,12:05 PM,03:05 PM,FREE,BUSY
08/21/16,01:05 PM,04:05 PM,Mets at Giants,AT&T Park - San Francisco,"",08/21/16,08/21/16,04:05 PM,07:05 PM,FALSE,TRUE,08/21/16,12:05 PM,03:05 PM,FREE,BUSY
08/26/16,07:15 PM,10:15 PM,Braves at Giants,AT&T Park - San Francisco,"",08/26/16,08/27/16,10:15 PM,01:15 AM,FALSE,TRUE,08/26/16,06:15 PM,09:15 PM,FREE,BUSY
08/27/16,06:05 PM,09:05 PM,Braves at Giants,AT&T Park - San Francisco,"",08/27/16,08/28/16,09:05 PM,12:05 AM,FALSE,TRUE,08/27/16,05:05 PM,08:05 PM,FREE,BUSY
08/28/16,01:05 PM,04:05 PM,Braves at Giants,AT&T Park - San Francisco,"",08/28/16,08/28/16,04:05 PM,07:05 PM,FALSE,TRUE,08/28/16,12:05 PM,03:05 PM,FREE,BUSY
08/30/16,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park - San Francisco,"",08/30/16,08/31/16,10:15 PM,01:15 AM,FALSE,TRUE,08/30/16,06:15 PM,09:15 PM,FREE,BUSY
08/31/16,12:45 PM,03:45 PM,D-backs at Giants,AT&T Park - San Francisco,"",08/31/16,08/31/16,03:45 PM,06:45 PM,FALSE,TRUE,08/31/16,11:45 AM,02:45 PM,FREE,BUSY
09/12/16,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"",09/12/16,09/13/16,10:15 PM,01:15 AM,FALSE,TRUE,09/12/16,06:15 PM,09:15 PM,FREE,BUSY
09/13/16,07:15 PM,10:15 PM,Padres at Giants,AT&T Park - San Francisco,"",09/13/16,09/14/16,10:15 PM,01:15 AM,FALSE,TRUE,09/13/16,06:15 PM,09:15 PM,FREE,BUSY
09/14/16,12:45 PM,03:45 PM,Padres at Giants,AT&T Park - San Francisco,"",09/14/16,09/14/16,03:45 PM,06:45 PM,FALSE,TRUE,09/14/16,11:45 AM,02:45 PM,FREE,BUSY
09/15/16,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park - San Francisco,"",09/15/16,09/16/16,10:15 PM,01:15 AM,FALSE,TRUE,09/15/16,06:15 PM,09:15 PM,FREE,BUSY
09/16/16,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park - San Francisco,"",09/16/16,09/17/16,10:15 PM,01:15 AM,FALSE,TRUE,09/16/16,06:15 PM,09:15 PM,FREE,BUSY
09/17/16,06:05 PM,09:05 PM,Cardinals at Giants,AT&T Park - San Francisco,"",09/17/16,09/18/16,09:05 PM,12:05 AM,FALSE,TRUE,09/17/16,05:05 PM,08:05 PM,FREE,BUSY
09/18/16,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park - San Francisco,"",09/18/16,09/18/16,04:05 PM,07:05 PM,FALSE,TRUE,09/18/16,12:05 PM,03:05 PM,FREE,BUSY
09/27/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",09/27/16,09/28/16,10:15 PM,01:15 AM,FALSE,TRUE,09/27/16,06:15 PM,09:15 PM,FREE,BUSY
09/28/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",09/28/16,09/29/16,10:15 PM,01:15 AM,FALSE,TRUE,09/28/16,06:15 PM,09:15 PM,FREE,BUSY
09/29/16,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park - San Francisco,"",09/29/16,09/30/16,10:15 PM,01:15 AM,FALSE,TRUE,09/29/16,06:15 PM,09:15 PM,FREE,BUSY
09/30/16,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park - San Francisco,"",09/30/16,10/01/16,10:15 PM,01:15 AM,FALSE,TRUE,09/30/16,06:15 PM,09:15 PM,FREE,BUSY
10/01/16,01:05 PM,04:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"",10/01/16,10/01/16,04:05 PM,07:05 PM,FALSE,TRUE,10/01/16,12:05 PM,03:05 PM,FREE,BUSY
10/02/16,12:05 PM,03:05 PM,Dodgers at Giants,AT&T Park - San Francisco,"",10/02/16,10/02/16,03:05 PM,06:05 PM,FALSE,TRUE,10/02/16,11:05 AM,02:05 PM,FREE,BUSY'''

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
