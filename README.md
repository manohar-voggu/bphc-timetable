# bphc-timetable
Scripts and static assets related to parsing timetable pdf of bphc

### Instructions
* Adjust variables like path/url to pdf, start & end page numbers, area for tabula, columns to parse in `pdf2json.py` <br>
* `python3 pdf2json.py`

### Note
Lookout for the following while parsing the output json:
* null values in midsem_date , compre_date in courses
* empty lists for days, hours in sections