import tabula
import pandas as pd
import json
from json import JSONEncoder

# path/url to time table pdf
pdf_path = 'timetable.pdf'
# start and end page numbers in pdf for coursewise timetable
start_page = 7
end_page = 52

# specify area using coordinates: https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool#grab-coordinates-of-the-table-you-want
df_list = tabula.read_pdf(pdf_path, pages=[i for i in range(start_page, end_page + 1)], pandas_options={'dtype': 'str'}, area=(121.275,45.54,557.865,742.5))
df = pd.concat(df_list, ignore_index=True)
df.columns = [i for i in range(12)]
df.drop([0, 3, 4, 5], axis=1, inplace=True)
df.columns = ['course_no', 'course_name','section_no', 'instructor', 'days', 'hours', 'midsem_date','compre_date']


class Course:
    def __init__(self, no, name, midsem_date, compre_date):
        self.no = no
        self.name = name
        self.midsem_date = midsem_date
        self.compre_date = compre_date
        self.sections = []


class Section:
    def __init__(self, category, no, instructor, days, hours):
        self.category = category
        self.no = no
        # list so that more instructors can be added as loop runs
        self.instructors = [instructor]
        self.days = days
        self.hours = hours


# https://pynative.com/make-python-class-json-serializable/
# to make the classes json serialisable
class CoursesEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def exists(field):
    # checks if field is non-null
    # dtype=str was passed to read_pdf, so all non-null fields are forced to be of type str
    return isinstance(field, str)


courses = []
# L(Lecture), T(Tutorial), P(Practical) are the possible values
category_current = "L"

# what might and what might not be null can be guessed from output of df.isnull().sum()
for _, row in df.iterrows():
    if exists(row['course_no']):  # new course
        category_current = "L"  # reset category to Lecture
        courses.append(Course(row['course_no'], row['course_name'], row['midsem_date'], row['compre_date']))

        # days & hours may not exist (for study projects etc.)
        days = row['days'].split() if exists(row['days']) else []
        hours = row['hours'].split() if exists(row['hours']) else []
        # add section to latest course
        courses[-1].sections.append(Section(category_current,
                                            1 + len(courses[-1].sections), row['instructor'], days, hours))

    else:
        # same course
        if exists(row['course_name']):
            # change category
            if row['course_name'].lower() == 'tutorial':
                category_current = "T"
            if row['course_name'].lower() == 'practical':
                category_current = "P"

            days = row['days'].split() if exists(row['days']) else []
            hours = row['hours'].split() if exists(row['hours']) else []
            courses[-1].sections.append(Section(category_current,
                                                1 + len(courses[-1].sections), row['instructor'], days, hours))
        else:
            # same category
            if exists(row['section_no']):
                # new section
                days = row['days'].split() if exists(row['days']) else []
                hours = row['hours'].split() if exists(row['hours']) else []
                courses[-1].sections.append(Section(category_current,
                                                    1 + len(courses[-1].sections), row['instructor'], days, hours))
            else:
                # same section
                days = row['days'].split() if exists(row['days']) else []
                hours = row['hours'].split() if exists(row['hours']) else []
                courses[-1].sections[-1].instructors.append(row['instructor'])
                courses[-1].sections[-1].days.extend(days)
                courses[-1].sections[-1].hours.extend(hours)

with open('courses.json', 'w') as output:
    output_json = CoursesEncoder().encode(courses)
    output.write(output_json)
    if 'NaN' in output_json:
        raise Exception('"NaN" found in json. Wrote to file anyway. Correct it manually')
