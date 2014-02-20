import os
import datetime

def isoparse(s):
    try:
        year =  s[0:4]
        month = s[5:7]
        day = s[8:10]
        numericYear = int(year, 10)
        if numericYear < 2000:
            return None

        return datetime.date( numericYear, int(month,10),int(day, 10) )
    except:
        return None

def make_url( originalPath ):

    base = originalPath
    
    root =  base.strip();
    
    replacedWrongSlash = root.replace("\\", "/" )
    replacedDuplicateHyphens = re.sub(r"[^a-z0-9\-/]", "-", replacedWrongSlash)
    replacedBadChars = re.sub(r"(\-{2,})", "-", replacedDuplicateHyphens )
    replacedEndingHyphens = replacedBadChars.rstrip('-') 

    if replacedEndingHyphens.endswith( '/' ) == False:
        replacedEndingHyphens = replacedEndingHyphens + '/'

    return replacedEndingHyphens

def is_development():
    env = os.environ['SERVER_SOFTWARE']

    return env.startswith('Development/')