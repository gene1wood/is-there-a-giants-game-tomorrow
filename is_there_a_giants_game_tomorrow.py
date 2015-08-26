#!/bin/env python

import csv
from datetime import time, datetime, timedelta
import logging
import json
import pyzmail
import sys

# http://mlb.mlb.com/soa/ical/schedule.csv?home_team_id=137&season=2015
CSV_DATA = '''START_DATE,START_TIME,START_TIME_ET,SUBJECT,LOCATION,DESCRIPTION,END_DATE,END_DATE_ET,END_TIME,END_TIME_ET,REMINDER_OFF,REMINDER_ON,REMINDER_DATE,REMINDER_TIME,REMINDER_TIME_ET,SHOWTIMEAS_FREE,SHOWTIMEAS_BUSY
03/04/15,12:05 PM,03:05 PM,Athletics at Giants,Scottsdale Stadium,"Local Radio: KNBR 680",03/04/15,03/04/15,03:05 PM,06:05 PM,FALSE,TRUE,03/04/15,11:05 AM,02:05 PM,FREE,BUSY
03/05/15,12:05 PM,03:05 PM,Cubs at Giants,Scottsdale Stadium,"Local Radio: MLB.com",03/05/15,03/05/15,03:05 PM,06:05 PM,FALSE,TRUE,03/05/15,11:05 AM,02:05 PM,FREE,BUSY
03/07/15,12:05 PM,03:05 PM,Padres at Giants,Scottsdale Stadium,"Local TV: MLBN (delay) -- CSN-BA ----- Local Radio: KNBR 680",03/07/15,03/07/15,03:05 PM,06:05 PM,FALSE,TRUE,03/07/15,11:05 AM,02:05 PM,FREE,BUSY
03/08/15,01:05 PM,04:05 PM,D-backs at Giants,Scottsdale Stadium,"Local Radio: KNBR 680",03/08/15,03/08/15,04:05 PM,07:05 PM,FALSE,TRUE,03/08/15,12:05 PM,03:05 PM,FREE,BUSY
03/09/15,01:05 PM,04:05 PM,Dodgers at Giants,Scottsdale Stadium,"Local TV: MLBN (delay) ----- Local Radio: KNBR 680",03/09/15,03/09/15,04:05 PM,07:05 PM,FALSE,TRUE,03/09/15,12:05 PM,03:05 PM,FREE,BUSY
03/11/15,01:05 PM,04:05 PM,Brewers at Giants,Scottsdale Stadium,"Local Radio: MLB.com",03/11/15,03/11/15,04:05 PM,07:05 PM,FALSE,TRUE,03/11/15,12:05 PM,03:05 PM,FREE,BUSY
03/13/15,01:05 PM,04:05 PM,Rangers at Giants,Scottsdale Stadium,"Local Radio: MLB.com",03/13/15,03/13/15,04:05 PM,07:05 PM,FALSE,TRUE,03/13/15,12:05 PM,03:05 PM,FREE,BUSY
03/15/15,03:05 PM,06:05 PM,D-backs at Giants,Scottsdale Stadium,"Local TV: MLBN (delay) -- NBC Bay Area ----- Local Radio: KNBR 680",03/15/15,03/15/15,06:05 PM,09:05 PM,FALSE,TRUE,03/15/15,02:05 PM,05:05 PM,FREE,BUSY
03/17/15,01:05 PM,04:05 PM,D-backs at Giants,Scottsdale Stadium,"Local Radio: MLB.com",03/17/15,03/17/15,04:05 PM,07:05 PM,FALSE,TRUE,03/17/15,12:05 PM,03:05 PM,FREE,BUSY
03/20/15,06:05 PM,09:05 PM,Reds at Giants,Scottsdale Stadium,"Local TV: MLBN -- NBC Bay Area ----- Local Radio: MLB.com",03/20/15,03/21/15,09:05 PM,12:05 AM,FALSE,TRUE,03/20/15,05:05 PM,08:05 PM,FREE,BUSY
03/22/15,01:05 PM,04:05 PM,Angels at Giants,Scottsdale Stadium,"Local Radio: KNBR 680",03/22/15,03/22/15,04:05 PM,07:05 PM,FALSE,TRUE,03/22/15,12:05 PM,03:05 PM,FREE,BUSY
03/23/15,01:05 PM,04:05 PM,Royals at Giants,Scottsdale Stadium,"Local Radio: KNBR 680",03/23/15,03/23/15,04:05 PM,07:05 PM,FALSE,TRUE,03/23/15,12:05 PM,03:05 PM,FREE,BUSY
03/26/15,07:05 PM,10:05 PM,Athletics at Giants,Scottsdale Stadium,"Local TV: CSN-BA -- MLBN (delay) ----- Local Radio: KNBR 680",03/26/15,03/27/15,10:05 PM,01:05 AM,FALSE,TRUE,03/26/15,06:05 PM,09:05 PM,FREE,BUSY
03/28/15,01:05 PM,04:05 PM,Giants Futures at Giants,Scottsdale Stadium,,03/28/15,03/28/15,04:05 PM,07:05 PM,FALSE,TRUE,03/28/15,12:05 PM,03:05 PM,FREE,BUSY
03/29/15,01:05 PM,04:05 PM,Dodgers at Giants,Scottsdale Stadium,"Local TV: CSN-BA ----- Local Radio: KNBR 680",03/29/15,03/29/15,04:05 PM,07:05 PM,FALSE,TRUE,03/29/15,12:05 PM,03:05 PM,FREE,BUSY
03/31/15,01:05 PM,04:05 PM,Rockies at Giants,Scottsdale Stadium,"Local Radio: MLB.com",03/31/15,03/31/15,04:05 PM,07:05 PM,FALSE,TRUE,03/31/15,12:05 PM,03:05 PM,FREE,BUSY
04/01/15,01:05 PM,04:05 PM,Indians at Giants,Scottsdale Stadium,"Local Radio: MLB.com",04/01/15,04/01/15,04:05 PM,07:05 PM,FALSE,TRUE,04/01/15,12:05 PM,03:05 PM,FREE,BUSY
04/02/15,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park,"Local TV: MLBN ----- Local Radio: KNBR 680",04/02/15,04/03/15,10:15 PM,01:15 AM,FALSE,TRUE,04/02/15,06:15 PM,09:15 PM,FREE,BUSY
04/03/15,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680",04/03/15,04/04/15,10:15 PM,01:15 AM,FALSE,TRUE,04/03/15,06:15 PM,09:15 PM,FREE,BUSY
04/13/15,01:35 PM,04:35 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",04/13/15,04/13/15,04:35 PM,07:35 PM,FALSE,TRUE,04/13/15,12:35 PM,03:35 PM,FREE,BUSY
04/14/15,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park,"Local TV: MLBN -- CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",04/14/15,04/15/15,10:15 PM,01:15 AM,FALSE,TRUE,04/14/15,06:15 PM,09:15 PM,FREE,BUSY
04/15/15,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",04/15/15,04/16/15,10:15 PM,01:15 AM,FALSE,TRUE,04/15/15,06:15 PM,09:15 PM,FREE,BUSY
04/16/15,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park,"Local TV: MLBN -- CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",04/16/15,04/17/15,10:15 PM,01:15 AM,FALSE,TRUE,04/16/15,06:15 PM,09:15 PM,FREE,BUSY
04/17/15,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",04/17/15,04/18/15,10:15 PM,01:15 AM,FALSE,TRUE,04/17/15,06:15 PM,09:15 PM,FREE,BUSY
04/18/15,06:05 PM,09:05 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA -- MLBN ----- Local Radio: KNBR 680 -- KTRB 860",04/18/15,04/19/15,09:05 PM,12:05 AM,FALSE,TRUE,04/18/15,05:05 PM,08:05 PM,FREE,BUSY
04/19/15,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",04/19/15,04/19/15,04:05 PM,07:05 PM,FALSE,TRUE,04/19/15,12:05 PM,03:05 PM,FREE,BUSY
04/21/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",04/21/15,04/22/15,10:15 PM,01:15 AM,FALSE,TRUE,04/21/15,06:15 PM,09:15 PM,FREE,BUSY
04/22/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",04/22/15,04/23/15,10:15 PM,01:15 AM,FALSE,TRUE,04/22/15,06:15 PM,09:15 PM,FREE,BUSY
04/23/15,12:45 PM,03:45 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA -- MLBN ----- Local Radio: KNBR 680 -- KTRB 860",04/23/15,04/23/15,03:45 PM,06:45 PM,FALSE,TRUE,04/23/15,11:45 AM,02:45 PM,FREE,BUSY
05/01/15,07:15 PM,10:15 PM,Angels at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/01/15,05/02/15,10:15 PM,01:15 AM,FALSE,TRUE,05/01/15,06:15 PM,09:15 PM,FREE,BUSY
05/02/15,01:05 PM,04:05 PM,Angels at Giants,AT&T Park,"Local TV: CSN-BA -- FS1 ----- Local Radio: KNBR 680 -- KTRB 860",05/02/15,05/02/15,04:05 PM,07:05 PM,FALSE,TRUE,05/02/15,12:05 PM,03:05 PM,FREE,BUSY
05/03/15,01:05 PM,04:05 PM,Angels at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/03/15,05/03/15,04:05 PM,07:05 PM,FALSE,TRUE,05/03/15,12:05 PM,03:05 PM,FREE,BUSY
05/04/15,07:15 PM,10:15 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/04/15,05/05/15,10:15 PM,01:15 AM,FALSE,TRUE,05/04/15,06:15 PM,09:15 PM,FREE,BUSY
05/05/15,07:15 PM,10:15 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/05/15,05/06/15,10:15 PM,01:15 AM,FALSE,TRUE,05/05/15,06:15 PM,09:15 PM,FREE,BUSY
05/06/15,12:45 PM,03:45 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/06/15,05/06/15,03:45 PM,06:45 PM,FALSE,TRUE,05/06/15,11:45 AM,02:45 PM,FREE,BUSY
05/07/15,07:15 PM,10:15 PM,Marlins at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",05/07/15,05/08/15,10:15 PM,01:15 AM,FALSE,TRUE,05/07/15,06:15 PM,09:15 PM,FREE,BUSY
05/08/15,07:15 PM,10:15 PM,Marlins at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/08/15,05/09/15,10:15 PM,01:15 AM,FALSE,TRUE,05/08/15,06:15 PM,09:15 PM,FREE,BUSY
05/09/15,06:05 PM,09:05 PM,Marlins at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680 -- KTRB 860",05/09/15,05/10/15,09:05 PM,12:05 AM,FALSE,TRUE,05/09/15,05:05 PM,08:05 PM,FREE,BUSY
05/10/15,01:05 PM,04:05 PM,Marlins at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",05/10/15,05/10/15,04:05 PM,07:05 PM,FALSE,TRUE,05/10/15,12:05 PM,03:05 PM,FREE,BUSY
05/19/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA -- MLBN ----- Local Radio: KTRB 860 -- KNBR 680",05/19/15,05/20/15,10:15 PM,01:15 AM,FALSE,TRUE,05/19/15,06:15 PM,09:15 PM,FREE,BUSY
05/20/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",05/20/15,05/21/15,10:15 PM,01:15 AM,FALSE,TRUE,05/20/15,06:15 PM,09:15 PM,FREE,BUSY
05/21/15,12:45 PM,03:45 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA -- MLBN ----- Local Radio: KNBR 680 -- KTRB 860",05/21/15,05/21/15,03:45 PM,06:45 PM,FALSE,TRUE,05/21/15,11:45 AM,02:45 PM,FREE,BUSY
05/28/15,07:15 PM,10:15 PM,Braves at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",05/28/15,05/29/15,10:15 PM,01:15 AM,FALSE,TRUE,05/28/15,06:15 PM,09:15 PM,FREE,BUSY
05/29/15,07:15 PM,10:15 PM,Braves at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",05/29/15,05/30/15,10:15 PM,01:15 AM,FALSE,TRUE,05/29/15,06:15 PM,09:15 PM,FREE,BUSY
05/30/15,07:05 PM,10:05 PM,Braves at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",05/30/15,05/31/15,10:05 PM,01:05 AM,FALSE,TRUE,05/30/15,06:05 PM,09:05 PM,FREE,BUSY
05/31/15,01:05 PM,04:05 PM,Braves at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",05/31/15,05/31/15,04:05 PM,07:05 PM,FALSE,TRUE,05/31/15,12:05 PM,03:05 PM,FREE,BUSY
06/01/15,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",06/01/15,06/02/15,10:15 PM,01:15 AM,FALSE,TRUE,06/01/15,06:15 PM,09:15 PM,FREE,BUSY
06/02/15,07:15 PM,10:15 PM,Pirates at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/02/15,06/03/15,10:15 PM,01:15 AM,FALSE,TRUE,06/02/15,06:15 PM,09:15 PM,FREE,BUSY
06/03/15,12:45 PM,03:45 PM,Pirates at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",06/03/15,06/03/15,03:45 PM,06:45 PM,FALSE,TRUE,06/03/15,11:45 AM,02:45 PM,FREE,BUSY
06/12/15,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",06/12/15,06/13/15,10:15 PM,01:15 AM,FALSE,TRUE,06/12/15,06:15 PM,09:15 PM,FREE,BUSY
06/13/15,04:15 PM,07:15 PM,D-backs at Giants,AT&T Park,"Local TV: FOX ----- Local Radio: KTRB 860 -- KNBR 680",06/13/15,06/13/15,07:15 PM,10:15 PM,FALSE,TRUE,06/13/15,03:15 PM,06:15 PM,FREE,BUSY
06/14/15,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/14/15,06/14/15,04:05 PM,07:05 PM,FALSE,TRUE,06/14/15,12:05 PM,03:05 PM,FREE,BUSY
06/15/15,07:15 PM,10:15 PM,Mariners at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/15/15,06/16/15,10:15 PM,01:15 AM,FALSE,TRUE,06/15/15,06:15 PM,09:15 PM,FREE,BUSY
06/16/15,12:45 PM,03:45 PM,Mariners at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/16/15,06/16/15,03:45 PM,06:45 PM,FALSE,TRUE,06/16/15,11:45 AM,02:45 PM,FREE,BUSY
06/23/15,07:15 PM,10:15 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",06/23/15,06/24/15,10:15 PM,01:15 AM,FALSE,TRUE,06/23/15,06:15 PM,09:15 PM,FREE,BUSY
06/24/15,07:15 PM,10:15 PM,Padres at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",06/24/15,06/25/15,10:15 PM,01:15 AM,FALSE,TRUE,06/24/15,06:15 PM,09:15 PM,FREE,BUSY
06/25/15,12:45 PM,03:45 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/25/15,06/25/15,03:45 PM,06:45 PM,FALSE,TRUE,06/25/15,11:45 AM,02:45 PM,FREE,BUSY
06/26/15,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",06/26/15,06/27/15,10:15 PM,01:15 AM,FALSE,TRUE,06/26/15,06:15 PM,09:15 PM,FREE,BUSY
06/27/15,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/27/15,06/27/15,04:05 PM,07:05 PM,FALSE,TRUE,06/27/15,12:05 PM,03:05 PM,FREE,BUSY
06/28/15,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",06/28/15,06/28/15,04:05 PM,07:05 PM,FALSE,TRUE,06/28/15,12:05 PM,03:05 PM,FREE,BUSY
07/06/15,07:15 PM,10:15 PM,Mets at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",07/06/15,07/07/15,10:15 PM,01:15 AM,FALSE,TRUE,07/06/15,06:15 PM,09:15 PM,FREE,BUSY
07/07/15,07:15 PM,10:15 PM,Mets at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",07/07/15,07/08/15,10:15 PM,01:15 AM,FALSE,TRUE,07/07/15,06:15 PM,09:15 PM,FREE,BUSY
07/08/15,12:45 PM,03:45 PM,Mets at Giants,AT&T Park,"Local TV: CSN-BA -- MLBN ----- Local Radio: KNBR 680 -- KTRB 860",07/08/15,07/08/15,03:45 PM,06:45 PM,FALSE,TRUE,07/08/15,11:45 AM,02:45 PM,FREE,BUSY
07/10/15,07:15 PM,10:15 PM,Phillies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",07/10/15,07/11/15,10:15 PM,01:15 AM,FALSE,TRUE,07/10/15,06:15 PM,09:15 PM,FREE,BUSY
07/11/15,07:05 PM,10:05 PM,Phillies at Giants,AT&T Park,"Local TV: NBC Bay Area -- MLBN ----- Local Radio: KNBR 680 -- KTRB 860",07/11/15,07/12/15,10:05 PM,01:05 AM,FALSE,TRUE,07/11/15,06:05 PM,09:05 PM,FREE,BUSY
07/12/15,01:05 PM,04:05 PM,Phillies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",07/12/15,07/12/15,04:05 PM,07:05 PM,FALSE,TRUE,07/12/15,12:05 PM,03:05 PM,FREE,BUSY
07/14/15,07:00 PM,07:00 PM,AL All-Stars at NL All-Stars,Great American Ball Park,,07/14/15,07/14/15,10:00 PM,10:00 PM,FALSE,TRUE,07/14/15,06:00 PM,06:00 PM,FREE,BUSY
07/24/15,07:15 PM,10:15 PM,Athletics at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",07/24/15,07/25/15,10:15 PM,01:15 AM,FALSE,TRUE,07/24/15,06:15 PM,09:15 PM,FREE,BUSY
07/25/15,01:05 PM,04:05 PM,Athletics at Giants,AT&T Park,"Local TV: FS1 -- CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",07/25/15,07/25/15,04:05 PM,07:05 PM,FALSE,TRUE,07/25/15,12:05 PM,03:05 PM,FREE,BUSY
07/26/15,01:05 PM,04:05 PM,Athletics at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",07/26/15,07/26/15,04:05 PM,07:05 PM,FALSE,TRUE,07/26/15,12:05 PM,03:05 PM,FREE,BUSY
07/27/15,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680 -- KTRB 860",07/27/15,07/28/15,10:15 PM,01:15 AM,FALSE,TRUE,07/27/15,06:15 PM,09:15 PM,FREE,BUSY
07/28/15,07:15 PM,10:15 PM,Brewers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",07/28/15,07/29/15,10:15 PM,01:15 AM,FALSE,TRUE,07/28/15,06:15 PM,09:15 PM,FREE,BUSY
07/29/15,12:45 PM,03:45 PM,Brewers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",07/29/15,07/29/15,03:45 PM,06:45 PM,FALSE,TRUE,07/29/15,11:45 AM,02:45 PM,FREE,BUSY
08/11/15,07:15 PM,10:15 PM,Astros at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/11/15,08/12/15,10:15 PM,01:15 AM,FALSE,TRUE,08/11/15,06:15 PM,09:15 PM,FREE,BUSY
08/12/15,12:45 PM,03:45 PM,Astros at Giants,AT&T Park,"Local TV: MLBN -- CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/12/15,08/12/15,03:45 PM,06:45 PM,FALSE,TRUE,08/12/15,11:45 AM,02:45 PM,FREE,BUSY
08/13/15,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park,"Local TV: MLBN -- NBC Bay Area ----- Local Radio: KTRB 860 -- KNBR 680",08/13/15,08/14/15,10:15 PM,01:15 AM,FALSE,TRUE,08/13/15,06:15 PM,09:15 PM,FREE,BUSY
08/14/15,07:15 PM,10:15 PM,Nationals at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/14/15,08/15/15,10:15 PM,01:15 AM,FALSE,TRUE,08/14/15,06:15 PM,09:15 PM,FREE,BUSY
08/15/15,07:05 PM,10:05 PM,Nationals at Giants,AT&T Park,"Local TV: FS1 -- CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/15/15,08/16/15,10:05 PM,01:05 AM,FALSE,TRUE,08/15/15,06:05 PM,09:05 PM,FREE,BUSY
08/16/15,01:05 PM,04:05 PM,Nationals at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/16/15,08/16/15,04:05 PM,07:05 PM,FALSE,TRUE,08/16/15,12:05 PM,03:05 PM,FREE,BUSY
08/25/15,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/25/15,08/26/15,10:15 PM,01:15 AM,FALSE,TRUE,08/25/15,06:15 PM,09:15 PM,FREE,BUSY
08/26/15,07:15 PM,10:15 PM,Cubs at Giants,AT&T Park,"Local TV: ESPN -- CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/26/15,08/27/15,10:15 PM,01:15 AM,FALSE,TRUE,08/26/15,06:15 PM,09:15 PM,FREE,BUSY
08/27/15,12:45 PM,03:45 PM,Cubs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/27/15,08/27/15,03:45 PM,06:45 PM,FALSE,TRUE,08/27/15,11:45 AM,02:45 PM,FREE,BUSY
08/28/15,07:15 PM,10:15 PM,Cardinals at Giants,AT&T Park,"Local TV: NBC Bay Area -- MLBN ----- Local Radio: KNBR 680 -- KTRB 860",08/28/15,08/29/15,10:15 PM,01:15 AM,FALSE,TRUE,08/28/15,06:15 PM,09:15 PM,FREE,BUSY
08/29/15,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",08/29/15,08/29/15,04:05 PM,07:05 PM,FALSE,TRUE,08/29/15,12:05 PM,03:05 PM,FREE,BUSY
08/30/15,01:05 PM,04:05 PM,Cardinals at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",08/30/15,08/30/15,04:05 PM,07:05 PM,FALSE,TRUE,08/30/15,12:05 PM,03:05 PM,FREE,BUSY
09/11/15,07:15 PM,10:15 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",09/11/15,09/12/15,10:15 PM,01:15 AM,FALSE,TRUE,09/11/15,06:15 PM,09:15 PM,FREE,BUSY
09/12/15,06:05 PM,09:05 PM,Padres at Giants,AT&T Park,"Local TV: NBC Bay Area ----- Local Radio: KNBR 680 -- KTRB 860",09/12/15,09/13/15,09:05 PM,12:05 AM,FALSE,TRUE,09/12/15,05:05 PM,08:05 PM,FREE,BUSY
09/13/15,01:05 PM,04:05 PM,Padres at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",09/13/15,09/13/15,04:05 PM,07:05 PM,FALSE,TRUE,09/13/15,12:05 PM,03:05 PM,FREE,BUSY
09/14/15,07:15 PM,10:15 PM,Reds at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",09/14/15,09/15/15,10:15 PM,01:15 AM,FALSE,TRUE,09/14/15,06:15 PM,09:15 PM,FREE,BUSY
09/15/15,07:15 PM,10:15 PM,Reds at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",09/15/15,09/16/15,10:15 PM,01:15 AM,FALSE,TRUE,09/15/15,06:15 PM,09:15 PM,FREE,BUSY
09/16/15,07:15 PM,10:15 PM,Reds at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",09/16/15,09/17/15,10:15 PM,01:15 AM,FALSE,TRUE,09/16/15,06:15 PM,09:15 PM,FREE,BUSY
09/18/15,07:15 PM,10:15 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",09/18/15,09/19/15,10:15 PM,01:15 AM,FALSE,TRUE,09/18/15,06:15 PM,09:15 PM,FREE,BUSY
09/19/15,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",09/19/15,09/19/15,04:05 PM,07:05 PM,FALSE,TRUE,09/19/15,12:05 PM,03:05 PM,FREE,BUSY
09/20/15,01:05 PM,04:05 PM,D-backs at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",09/20/15,09/20/15,04:05 PM,07:05 PM,FALSE,TRUE,09/20/15,12:05 PM,03:05 PM,FREE,BUSY
09/28/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",09/28/15,09/29/15,10:15 PM,01:15 AM,FALSE,TRUE,09/28/15,06:15 PM,09:15 PM,FREE,BUSY
09/29/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",09/29/15,09/30/15,10:15 PM,01:15 AM,FALSE,TRUE,09/29/15,06:15 PM,09:15 PM,FREE,BUSY
09/30/15,07:15 PM,10:15 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",09/30/15,10/01/15,10:15 PM,01:15 AM,FALSE,TRUE,09/30/15,06:15 PM,09:15 PM,FREE,BUSY
10/01/15,12:45 PM,03:45 PM,Dodgers at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",10/01/15,10/01/15,03:45 PM,06:45 PM,FALSE,TRUE,10/01/15,11:45 AM,02:45 PM,FREE,BUSY
10/02/15,07:15 PM,10:15 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KNBR 680 -- KTRB 860",10/02/15,10/03/15,10:15 PM,01:15 AM,FALSE,TRUE,10/02/15,06:15 PM,09:15 PM,FREE,BUSY
10/03/15,01:05 PM,04:05 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",10/03/15,10/03/15,04:05 PM,07:05 PM,FALSE,TRUE,10/03/15,12:05 PM,03:05 PM,FREE,BUSY
10/04/15,12:05 PM,03:05 PM,Rockies at Giants,AT&T Park,"Local TV: CSN-BA ----- Local Radio: KTRB 860 -- KNBR 680",10/04/15,10/04/15,03:05 PM,06:05 PM,FALSE,TRUE,10/04/15,11:05 AM,02:05 PM,FREE,BUSY'''

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
        start = datetime.strptime('%s %s' % (row['START_DATE'], row['START_TIME']),
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