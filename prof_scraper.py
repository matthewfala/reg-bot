import myuscauth
import ratemyprof_scraper
import requests
import lxml
from lxml import html
from lxml import etree
import pickle
import os
import re
from datetime import time
import credentials
from datetime import timedelta

pickle_file = 'my_usc_session.pkl'
term = 'fall' # Options, Spring Fall Summer
course_name = 'writ-150'

home = 'https://my.usc.edu/'
webreg_connect = 'https://my.usc.edu/portal/oasis/webregbridge.php'
webreg = "https://webreg.usc.edu/"

def new_saved_session(_pickle_file):
    print "No pickle file, generating new session"
    with open(_pickle_file, 'wb') as output:
        s = myuscauth.usc_auth(credentials.get_username(), credentials.get_password())
        pickle.dump(s, output, pickle.HIGHEST_PROTOCOL)
        print "Logged In"


def recover_session(_pickle_file):
    with open(_pickle_file, 'rb') as myinput:
        print "File exists! recovering session ..."
        recovered_s = pickle.load(myinput)
        return recovered_s

# Save and recover session
if not os.path.isfile(pickle_file):
    new_saved_session(pickle_file)
s = recover_session(pickle_file)

terms_page = s.get(webreg_connect)

session_end_phrase = 'Your session has ended.'
session_ended = session_end_phrase in terms_page.text

if session_ended:
    print "Session ended, forcing new session"
    # force new session
    new_saved_session(pickle_file)
    s = recover_session(pickle_file)
    terms_page = s.get(webreg_connect)

#print terms_page.content

tree = lxml.html.fromstring(terms_page.content)


if term == 'fall':
    term_element = tree.xpath("//ul//li[@id='termmenuFall']/a")
elif term == 'spring':
    term_element = tree.xpath("//ul//li[@id='termmenuSumm']/a")
elif term == 'summer':
    term_element = tree.xpath("//ul//li[@id='termmenuSpr']/a")

print term_element[0].attrib['href']

addr = webreg + term_element[0].attrib['href']
catalogue = s.get(addr)
print catalogue.content

search = s.get('https://webreg.usc.edu/Srch')

print search.content

payload = {
    'AutoCompleteCoursePath': '/Courses/AutoCompleteCourse',
    'AutoCompleteCourseTitlePath': '/Courses/AutoCompleteCourseTitle',
    'AutoCompleteDeptPath': '/Courses/AutoCompleteDept',
    'AutoCompleteInstrPath': '/Courses/AutoCompleteInstr',
    'AutoCompleteSectionPath': '/Courses/AutoCompleteSection',
    'Course': course_name,
    'CourseTitle': '',
    'Dept': '',
    'F': 'False',
    'Instr': '',
    'M': 'False',
    'Section': '',
    'T': 'False',
    'Th': 'False',
    'Units': '',
    'W': 'False',
    'bDCSI': 'true',
    'bTimSrch': 'false',
    'tim1HrList': '',
    'tim1MinList': '',
    'tim1ampmList' : '',
    'tim2HrList': '',
    'tim2MinList': '',
    'tim2ampmList': ''
}

def mins_from_midnight(mytime):
    return mytime.hour * 60 + mytime.min

class Course:
    def __init__(self, section, time_unformatted, instructor):
        self.section = section

        self.time_unformatted = time_unformatted
        times = time_unformatted.split('-')

        ts = times[0]
        te = times[1]
        timeAdd = [0, 0]
        if "pm" in ts:
            if '12' not in ts:
                print "PM found in start time"
                timeAdd[0] = 12
        if "pm" in te:
            if '12' not in te:
                print "Add 12 to end time"
                timeAdd[1] = 12

        times = re.split(':|pm|am', ts)
        start_hour = int(times[0]) + timeAdd[0]
        start_min = int(times[1])

        times = re.split(':|pm|am', te)
        end_hour = int(times[0]) + timeAdd[1]
        end_min = int(times[1])

        # course values
        self.start_time = time(start_hour, start_min)
        self.end_time = time(end_hour, end_min)
        self.instructor = instructor
        self.teacher_rating = ratemyprof_scraper.get_rating(instructor)
        self.difficulty = ratemyprof_scraper.get_difficulty(instructor)
        self.easiness = 5 - self.difficulty

    def course_rating(self, importance_rating, importance_easiness, importance_time, optimal_start_time):

        delta_time = abs(mins_from_midnight(optimal_start_time) - mins_from_midnight(self.start_time))
        # scale 0 to 5 for time rating
        time_scaled = 5 - delta_time * 5 / (12 * 60)

        c_rating = importance_rating * self.teacher_rating
        c_rating += importance_easiness * self.easiness
        c_rating += importance_time * time_scaled

        return c_rating


print " --------------------------------------------------------- "
search = s.post('https://webreg.usc.edu/Search', data=payload)

tree = lxml.html.fromstring(search.content)
classes_html = tree.xpath("//div[@class = 'col-xs-12 col-sm-12 col-md-12 col-lg-12']/div")

print "Classes count: " + str(len(classes_html))

for c in classes_html:
    class_elements = c.Element("span")
    print "Course number: " + html.tostring(class_elements[0])


#print search.content
# print "Trying to print terms"
# print term_element[0].text_content()
#
# timeStr = "12:00pm-1:00pm"
# times = timeStr.split('-')
#
# ts = times[0]
# te = times[1]
# timeAdd = [0, 0]
# if "pm" in ts:
#     if '12' not in ts:
#         print "PM found in start time"
#         timeAdd[0] = 12
# if "pm" in te:
#     if '12' not in te:
#         print "Add 12 to end time"
#         timeAdd[1] = 12
#
# times = re.split(':|pm|am', ts)
# start_hour = int(times[0]) + timeAdd[0]
# start_min = int(times[1])
# print "start hour = " + str(start_hour)
# start_time = time(start_hour, start_min)
#
# times = re.split(':|pm|am', te)
# end_hour = int(times[0]) + timeAdd[1]
# end_min = int(times[1])
#
# print "end hour = " + str(end_hour)
# end_time = time(end_hour, end_min)
#
# # times = re.split(':|-|pm|am', timeStr)
# # start_hour = int(times[0])
# # start_min = int(times[1])
# # print "time " + str(start_hour) + ":" + str(start_min)
# # start_time = time(start_hour, start_min)
# #
# # end_hour = int(times[3])
# # end_min = int(times[4])
# # end_time = time(end_hour, end_min)
#
# # need to consider am and pm
# print "Class time length" + str(start_time.hour * 60 + start_time.minute - end_time.hour*60 - end_time.minute)
#
# print "WRIT"
#
# print "----"
