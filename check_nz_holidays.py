#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2016 Ben Jones'

from datetime import date
from datetime import timedelta

import requests

# openHAB details
host            = 'localhost'
port            = 8080
username        = 'username'
password        = 'password'
holidayitem     = 'VT_Holiday'          # SwitchItem
holidaynameitem = 'VT_HolidayName'      # StringItem

def update_item(item, value):
    if item is not None:
        url = 'http://%s:%s@%s:%d/rest/items/%s/state' % (username, password, host, port, item)
        headers = { 'Content-Type': 'text/plain' }
        requests.put(url, headers=headers, data=value)

def push_to_monday(date):
    if date.weekday() == 5:
        return date + timedelta(days=2)
    if date.weekday() == 6:
        return date + timedelta(days=1)
    return date

def push_consecutive_to_monday(date):
    date2 = date + timedelta(days=1)
    if date.weekday() == 5 or date.weekday() == 6:
        date += timedelta(days=2)
    if date2.weekday() == 5 or date2.weekday() == 6:
        date2 += timedelta(days=2)
    return date, date2

def calculate_easter_sunday(year):
    a = year % 19
    b = year / 100
    c = year % 100
    d = b / 4
    e = b % 4
    f = (b + 8) / 25
    g = (b - f + 1) / 3
    h = (19 * a + b - d - g + 15) % 30
    i = c / 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) / 451

    month = (h + L - 7 * m + 114) / 31
    day = ((h + L - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def calculate_holidays(year):
    holidays = {}

    # monday = 0, sunday = 6
    newyears1, newyears2 = push_consecutive_to_monday(date(year, 1, 1))
    holidays[newyears1] = 'New Years Day'
    holidays[newyears2] = 'Day After New Years Day'

    waitangiday = push_to_monday(date(year, 2, 6))	
    holidays[waitangiday] = 'Waitangi Day'

    eastersunday = calculate_easter_sunday(year)
    goodfriday = eastersunday - timedelta(days=2)
    eastermonday = eastersunday + timedelta(days=1)
    holidays[goodfriday] = 'Good Friday'
    holidays[eastermonday] = 'Easter Monday'

    anzacday = push_to_monday(date(year, 4, 25))
    holidays[anzacday] = 'Anzac Day'
	
    # queens birthday, first monday in june
    queensbirthday = date(year, 6, 1)
    if queensbirthday.weekday() == 6:
        queensbirthday += timedelta(days=1)
    elif queensbirthday.weekday() != 0:
        queensbirthday += timedelta(days=7 - queensbirthday.weekday())
    holidays[queensbirthday] = 'Queens Birthday'

    # labour day, 4th monday in october
    labourday = date(year, 10, 1)
    while labourday.weekday() != 0:
        labourday += timedelta(days=1)
    labourday += timedelta(weeks=3)
    holidays[labourday] = 'Labour Day'

    # show day, second friday after the first tuesday in november
    showday = date(year, 11, 1)
    while showday.weekday() != 1:
        showday += timedelta(days=1)
    showday += timedelta(days=10)
    holidays[showday] = 'Show Day'

    xmasday, boxingday = push_consecutive_to_monday(date(year, 12, 25))
    holidays[xmasday] = 'Xmas Day'
    holidays[boxingday] = 'Boxing Day'

    return holidays

def test(years):
    for year in years:
        print "Holidays for %s..." % (year)
        holidays = calculate_holidays(year)
        for holiday in sorted(holidays):
            print "%s is %s" % (holiday, holidays[holiday])

# testing
#test(range(2010, 2019))


# get the holidays for this year
today = date.today()
holidays = calculate_holidays(today.year)

# check if today is a holiday
if today in holidays:
    update_item(holidayitem, 'ON')
    update_item(holidaynameitem, holidays[today])
else:
    update_item(holidayitem, 'OFF')
    update_item(holidaynameitem, '')
