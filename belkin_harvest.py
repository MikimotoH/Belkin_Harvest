#!/usr/bin/env python3
# coding: utf-8
import harvest_utils
from harvest_utils import waitClickable, waitVisible, waitText, getElems, \
        getElemText,getFirefox,driver,dumpSnapshot,\
        getText,getNumElem,waitTextChanged,waitElem,\
        waitUntil,clickElem,getElemAttr,hasElem,waitUntilStable,\
        waitUntilA,mouseClickE,waitTextA,UntilTextChanged,mouseOver
from selenium.common.exceptions import NoSuchElementException, \
        TimeoutException, StaleElementReferenceException, \
        WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.common.action_chains import ActionChains
import sys
import sqlite3
from os import path
import os
import re
import time
import datetime
from datetime import datetime
import ipdb
import traceback
from my_utils import uprint,ulog
from contextlib import suppress
import random
import math

driver,conn=None,None
category,subCatg,productName,model,fileTitle='','','','',''
prevTrail=[]

charset='abcdefghijklmnopqrstuvwxyz0123456789'

def retryUntilTrue(statement, timeOut:float=6.2, pollFreq:float=0.3):
    timeElap=0
    while timeElap<timeOut:
        timeBegin=time.time()
        try:
            r = statement()
            ulog('r="%s"'%str(r))
            if r is not None:
                return r
        except (StaleElementReferenceException, StopIteration):
            pass
        except Exception as ex:
            ulog('raise %s %s'%(type(ex),str(ex)))
            raise ex
        ulog('sleep %f secs'%pollFreq)
        time.sleep(pollFreq)
        timeElap+=(time.time()-timeBegin)
    raise TimeoutException('retryUntilTrue: timeOut=%f'%timeOut)

def selectDownload():
    global driver
    # switch to frame
    pageUrl=driver.find_element_by_css_selector('iframe[name~=inlineFrame]').get_attribute('src')
    # http://www.belkin.com/us/support-article?articleNum=4879
    driver.get(pageUrl)
    artTxt = driver.find_element_by_css_selector('div#articleContainer').text
    downAnc= = next(_ for _ in getElems('a') if _.text.startswith('Download'))
    downUrl = downAnc.get_attribute('href')
    version = re.search(r'version:?\s*(\d(\.\d+)+)', artTxt).group(1)
    dateTxt = re.search(r'\d+/\d+/\d+', artTxt).group(0)
    relDate = datetime.strptime(dateTxt, '%m/%d/%Y')
    fileSizeM = re.search(r'Size: (\d+(\.\d+)*) (\w+)', artTxt, re.IGNORECASE).group(1)
    fileSize = int(fileSizeM[0])
    sql(
        "INSERT OR REPLACE INTO TFiles(category, product_name, model, file_tile, rel_date, fw_ver, file_size, page_url, download_url)VALUES( :category, :sub_catg, :productName, :model, :fileTitle, :relData, :fwVer, :fileSize, :pageUrl, downUrl)", glocals())
    ulog('INSERT %(category)s, %(productName)s, %(model)s, %(fileTitle)s, %(relDate)s, %(fwVer)s, %(fileSize)s, %(pageUrl)s, %(downUrl)s')
    
    driver.back()

def selectSupport():
    supports=getElems(' div.icon-list-header-container ')
    idx = next(i for i,_ in enumerate(supports) if _.text.strip().startswith('DOWNLOAD') for _ in supports)
    downloads = supports[idx].find_elements_by_css_selector('a')
    numDownloads = len(downloads)
    for idx in range(numDownloads):
        ulog('click "%s"'%downloads[idx].text)
        clickElem(downloads[idx])
        selectDownload()
        downloads = supports[idx].find_elements_by_css_selector('a')
    driver.back()

def selectProduct():
    products=getElems('.items a')
    waitUntil(lambda:ulog('products=%s'%[(i,_.text) for i,_ in enumerate(products)])
    numProducts=len(products)
    for idx in numProducts:
        product=products[idx]
        ulog('click "%s"'%getElemText(product))
        clickElem(products[idx])
        selectSupport()
        products=getElems('.items a')
    driver.back()

    

def selectSubCatg():
    with UntilTextChanged('.filter-list'):
        subCatgs=getElems('.filter-list a')
    numSubCatgs=len(subCatgs)
    for idx in numSubCatgs:
        ulog('idx=%d'%idx)
        ulog('click "%s"'%subCatgs[idx])
        clickElem(subCatgs[idx])
        subCatg=subCatg[idx].text
        selectProduct()
        subCatgs=getElems('.filter-list a')
    driver.back()

def selectCategory():
    global category, prevTrail
    waitVisible('.filter-list')
    with UntilTextChanged('.filter-list'):
        cats=getElems('.filter-list a')

    retryUntilTrue(lambda: ulog('cats=%s'%[_.text for _ in cats]))
    numCats=len(cats)
    for idx in range(startIdx, numCats):
        ulog('idx=%d'%idx)
        ulog('click "%s"'%cats[idx].text)
        clickElem(cats[idx])
        category+=cats[idx].text
        prevTrail+=[idx]
        selectCategory()
        prevTrail.pop()
        cats = getElems('div.filter-list a')
    driver.back()
    waitUntilTextChanged('.filter-list')

def getStartIdx():
    global startTrail
    if startTrail:
        startIdx = startTrail.pop(0)
    else:
        startIdx = 0

def main():
    global startTrail, prevTrail
    startTrail = [int(re.search(r'\d+', _).group(0)) for _ in sys.argv[1:]]
    ulog('startTrail=%s'%startTrail)
    global driver,conn
    conn=sqlite3.connect('belkin.sqlite3')
    sql(
        "CREATE TABLE IF NOT EXISTS TFiles("
        "id INTEGER NOT NULL,"
        "category TEXT," # ROUTER > N900 DB Wireless Router
        "product_name TEXT," # Advance N900 Dual-Band Wireless Router
        "model TEXT," # F9K1104
        "file_title TEXT," # N900 Wireless Router F9K1104 v1 - Firmware (US)
        "rel_date DATE," # Post Date: 06/20/2012 
        "fw_ver TEXT," # Download version: 1.00.23 
        "file_size INTEGER," # Size: 3.74 MB
        "page_url TEXT," # http://belkin.force.com/Articles/articles/en_US/Download/7371
        "download_url TEXT," # http://nextnet.belkin.com/update/files/F9K1104/v1/WW/F9K1104_WW_1.0.23.bin
        "tree_trail TEXT," # [26, 2, 1, 0, 0]
        "file_sha1 TEXT," # 5d3bc16eec2f6c34a5e46790b513093c28d8924a
        "PRIMARY KEY (id)"
        "UNIQUE(product_name,model,file_title,rel_date,fw_ver)"
        ");")
    driver=harvest_utils.getFirefox()
    driver.implicitly_wait(2.0)
    harvest_utils.driver=driver
    startIdx=getStartIdx()
    for idx in range(startIdx, len(charset)):
        ulog('idx=%d, search "%S"'%(idx,charset[idx]))
        driver.get('http://www.belkin.com/us/support-search?search=%s'%charset[idx])
        prevTrail+=[idx]
        selectCategory()
        prevTrail.pop()
    

if __name__=='__main__':
    try:
        main()
    except Exception as ex:
        ipdb.set_trace()
        print(str(ex)); traceback.print_exc()
        try:
            driver.save_screenshot('belkin.png')
            driver.quit()
        except Exception:
            pass

