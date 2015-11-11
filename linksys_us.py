#!/usr/bin/env python3
# coding: utf-8
from fuzzywuzzy import fuzz
import harvest_utils
from harvest_utils import waitClickable, waitVisible, waitText, getElems, \
        getElemText,getFirefox,driver,dumpSnapshot,\
        getText,getNumElem,waitTextChanged,waitElem,\
        waitUntil
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, \
        TimeoutException, StaleElementReferenceException, \
        WebDriverException
from infix_operator import Infix
import os
from os import path
import time
import sys
import sqlite3
import re
import datetime
from dateutil.parser import parse as dateparse
import http

fzeq=Infix(fuzz.token_set_ratio)
preq=Infix(fuzz.partial_token_set_ratio)
driver,conn=None,None

def glocals()->dict:
    """ globals() + locals()
    """
    import inspect
    ret = dict(inspect.stack()[1][0].f_locals)
    ret.update(globals())
    return ret

def uprint(msg:str):
    sys.stdout.buffer.write((msg+'\n').encode('utf8'))

def guessModel(txt:str)->str:
    """ txt='WRT51AB - Dual-Band Wireless A+B Broadband Router'
    """
    return txt.partition('-')[0].strip()

def guessRevision(txt:str)->str:
    """ txt="Hardware Version 1.0"
        txt="Version 1"
    """
    return re.search(r'\d+[0-9\.]*',txt,flags=re.IGNORECASE).group(0)

def guessVersion(txt:str) -> str:
    """ txt='Version:  1.1.40 (Build 166516)'
      or txt='Ver.3.2.1.0'
    """
    try:
        txt = next(_ for _ in txt.splitlines() if 'Ver' in _)
    except StopIteration:
        return ''
    if 'Version:' in txt:
        return txt.partition(':')[2].strip()
    elif 'Ver.' in txt:
        return txt.partition('.')[2].strip()
    elif 'Version' in txt:
        return txt.partition('Version')[2].strip()
    else:
        import pdb; pdb.set_trace()
        uprint('txt=%s'%txt)

def guessDate(txt:str) -> datetime.datetime:
    """ txt='Latest Date:  05/27/2015'
    """
    try:
        txt = next(_ for _ in txt.splitlines() if 'Date' in _)
    except StopIteration:
        return None
    return dateparse(txt.partition(':')[2].strip())

def guessFileSize(txt:str)->int:
    """ txt='Download 29.8 MB'
    """
    txt = next(_ for _ in txt.splitlines() if 'Download' in _)
    m = re.search(r'(\d*[.])?\d+', txt, re.IGNORECASE)
    unitTxt = txt[m.span()[1]:].strip()
    if 'MB' in unitTxt or 'BM' in unitTxt:
        return int(float(m.group(0))* 1024*1024)
    elif 'KB' in unitTxt:
        return int(float(m.group(0))* 1024)
    else:
        import pdb; pdb.set_trace()
        uprint('txt=%s'%txt)

def getCount(txt:str, pat:str)->int:
    cnt,start=0,0
    while True:
        idx = txt.find(pat, start)
        if idx==-1:
            return cnt
        cnt+=1
        start = idx+len(pat)

def guessFileTitle2(foreword:str)->str:
    lines =iter(foreword.splitlines())
    try:
        while True:
            line = next(lines).strip()
            if line and 'Date' not in line \
                    and 'Download' not in line:
                return line
    except StopIteration:
        uprint('Failed to guess fileTitle from foreword="%s"'%foreword)
        return ''

def guessFileTitle(foreword:str, fwVer:str)->str:
    lines =iter(foreword.splitlines())
    while True:
        line = next(lines).strip()
        if fwVer in line:
            break
    try:
        while True:
            line = next(lines).strip()
            if line and 'Date' not in line:
                return line
    except StopIteration:
        uprint('Failed to guess fileTitle from foreword="%s"'%foreword)
        return ''


def getNthIndex(txt:str, nth:int, pat:str)->int:
    assert nth>=0
    cnt,start=0,0
    while True:
        idx = txt.find(pat,start)
        if idx==-1:
            return -1
        if cnt==nth:
            return idx
        cnt+=1
        start=idx+len(pat)


def getElemTextUntilStabled(elm:WebElement, timeOut:float=60, pollFreq:float=3)->str:
    import time
    beginTime = time.time()
    try:
        oldText=getElemText(elm, timeOut)
    except TimeoutException:
        oldText=None
    elapsedTime = time.time() - beginTime
    while elapsedTime < timeOut:
        beginTime = time.time()
        time.sleep(pollFreq)
        newText=getElemText(elm, timeOut)
        if oldText == newText:
            return newText
        oldText = newText
        elapsedTime += time.time() - beginTime
    raise TimeoutException('[getElemTextUntilStabled] time out with '
        'timeOut=%f seconds, pollFreq=%f seconds'%(timeOut,pollFreq))

def main():
    startModelIdx = int(sys.argv[1]) if len(sys.argv)>1 else 0
    startRevisionIdx = int(sys.argv[2]) if len(sys.argv)>2 else 0
    brand='Linksys'
    global driver,conn
    harvest_utils.driver=getFirefox()
    driver = harvest_utils.driver
    conn=sqlite3.connect('Linksys.sqlite3')
    csr=conn.cursor()
    csr.execute(
        "CREATE TABLE IF NOT EXISTS TFiles("
        "brand TEXT,"
        "model TEXT,"
        "revision TEXT," # hardware version
        "fw_date DATE,"
        "fw_ver TEXT,"
        "file_title TEXT,"
        "file_size INTEGER,"
        "href TEXT,"
        "file_sha1 TEXT,"
        "PRIMARY KEY (brand,model,revision,file_title)"
        ");")
    conn.commit()
    driver.get('http://www.linksys.com/us/support/sitemap/')
    try:
        numModels = getNumElem('.item ul li a')
        print('numModels=',numModels)
        for modelIdx in range(startModelIdx, numModels):
            startModelIdx=0
            modelElm = getElems('.item ul li a')[modelIdx]
            modelText = getElemText(modelElm, 5)
            print('modelIdx=',modelIdx)
            uprint('modelText="%s"'%modelText)
            # guess Possible Model
            model = guessModel(modelText)
            print('model=',model)
            rows = csr.execute(
                "SELECT model from TFiles WHERE model=:model",locals()
                ).fetchall()
            if rows:
                print('model "%s" already in TFiles, bypass!!'%model)
                continue
            modelElm.click()
            # click 'Download Software'
            try:
                waitClickable('a[title="Download Software"]', 40).click()
            except TimeoutException:
                print('No "Download Software" link found, bypass!!')
                csr.execute(
                    "INSERT INTO TFiles(brand,model,revision)VALUES"
                    "(:brand,:model,'')", locals())
                conn.commit()
                print('INSERT model="%s"'%model)
                driver.back()
                continue
            # enumerate all accordians
            accordians = getElems('.article-accordian', 10)
            numAccordians=len(accordians)
            print('numAccordians=',numAccordians)
            print('driver.current_url=', driver.current_url)
            for revisionIdx in range(startRevisionIdx, numAccordians):
                startRevisionIdx=0
                accordians = getElems('.article-accordian')
                # expand accordian (one-based)
                accordian = accordians[revisionIdx]
                revisionTxt = getElemText(accordian)
                print('revisionIdx=',revisionIdx)
                uprint('revisionTxt="%s"'%revisionTxt)
                revision = guessRevision(revisionTxt)
                print('revision=',revision)
                divId = accordian.get_attribute('data-collapse-target')
                # expand accordian 'revision'='Hardware Version'
                driver.execute_script(
                    "document.querySelectorAll('.article-accordian')[%d].click()"
                    %(revisionIdx))
                divElm = waitVisible('#'+divId)
                divTxt = getElemTextUntilStabled(divElm,10,2.5)
                assert divTxt 
                uprint('divTxt="%s"'%divTxt)
                numDowns = getCount(divTxt, 'Download')
                if numDowns ==0:
                    csr.execute(
                        "INSERT INTO TFiles(brand,model,revision)VALUES"
                        "(:brand,:model,:revision)",locals())
                    conn.commit()
                    print('INSERT "%(model)s","%(revision)s"'%locals())
                    continue
                downElms =iter(divElm.find_elements_by_css_selector('a'))
                lastSpanEnd=0
                for downIdx in range(numDowns):
                    spanBegin = getNthIndex(divTxt, downIdx, 'Download')
                    spanEnd = divTxt.find('\n', spanBegin+len('Download'))
                    if spanEnd==-1:
                        spanEnd=len(divTxt)
                    foreword='\n'.join(reversed(divTxt[lastSpanEnd:spanEnd].splitlines()))
                    fwDate=guessDate(foreword)
                    fileSize = guessFileSize(foreword)
                    fwVer = guessVersion(foreword)
                    if fwVer:
                        fileTitle = guessFileTitle(foreword, fwVer)
                    else:
                        fileTitle = guessFileTitle2(foreword)
                    while True:
                        downElm = next(downElms)
                        if downElm.text.strip().startswith('Download'):
                            break
                    href=downElm.get_attribute('href')
                    lastSpanEnd=spanEnd
                    csr.execute(
                        "INSERT OR REPLACE INTO TFiles(brand,model,revision,"
                        "fw_date, fw_ver, file_title, file_size, "
                        "href) VALUES (:brand,:model,:revision,"
                        ":fwDate, :fwVer, :fileTitle,"
                        ":fileSize, :href)", locals())
                    conn.commit()
                    uprint("INSERT '%(model)s', '%(revision)s', '%(fwDate)s'"
                        ", '%(fwVer)s', '%(fileTitle)s', '%(fileSize)d'"
                        ", '%(href)s'" %locals())
            driver.back()
            driver.back()
    except http.client.IncompleteRead as ex:
        print(ex)
        import traceback; traceback.print_exc()
        print('-- Selenium exhausted')
        driver.quit()
    except Exception as ex:
        import ipdb; ipdb.set_trace()
        print(ex)
        print('driver.current_url=',driver.current_url)
        import traceback; traceback.print_exc()
    print('-- terminate firefox')
    driver.quit()


if __name__=='__main__':
    try:
        main()
    except Exception as ex:
        import pdb; pdb.set_trace()
        print(str(ex))
        dumpSnapshot(str(ex))
        try:
            driver.quit()
        except Exception:
            pass
