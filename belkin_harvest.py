#!/usr/bin/env python3
# coding: utf-8
import harvest_utils
from harvest_utils import waitVisible, waitText, getElems, getFirefox,driver,waitTextChanged, getElemText
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement
import sys
import sqlite3
import re
import time
import datetime
from datetime import datetime
import ipdb
import traceback
from my_utils import uprint,ulog,getFuncName
from contextlib import suppress
import random
import math
import html2text
from belkin_art_parse import getSizeDateVersion


driver,conn=None,None
category,productName,model='','',''
prevTrail=[]
startTrail=[]

def getScriptName():
    from os import path
    return path.splitext(path.basename(__file__))[0]


def getStartIdx():
    global startTrail
    if startTrail:
        return startTrail.pop(0)
    else:
        return 0

def sql(query:str, var=None):
    global conn
    csr=conn.cursor()
    try:
        if var:
            rows = csr.execute(query,var)
        else:
            rows = csr.execute(query)
        if not query.startswith('SELECT'):
            conn.commit()
        if query.startswith('SELECT'):
            return rows.fetchall()
        else:
            return
    except sqlite3.Error as ex:
        print(ex)
        raise ex

def glocals()->dict:
    """ globals() + locals()
    """
    import inspect
    ret = dict(inspect.stack()[1][0].f_locals)
    ret.update(globals())
    return ret

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
    raise TimeoutException(getFuncName()+': timeOut=%f'%timeOut)


def enterElem(e:WebElement):
   driver.get(e.get_attribute('href'))


def selectDownload():
    global driver,category,productName,model,prevTrail
    try:
        # switch to frame
        pageUrl=waitVisible('iframe[name~=inlineFrame]').get_attribute('src')
        # http://www.belkin.com/us/support-article?articleNum=4879
        driver.get(pageUrl)
        # convert html to Markdown Text
        page_src = waitVisible('.sfdc_richtext').get_attribute('innerHTML')
        h = html2text.HTML2Text()
        h.ignore_emphasis=True
        h.body_width=0
        artTxt = h.handle(page_src)
        startIdx=getStartIdx()
        for idx in range(startIdx, sys.maxsize):
            try:
                fileSize,relDate,fwVer,downUrl=getSizeDateVersion(artTxt, idx)
            except StopIteration:
                break
            prevTrail+=[idx]
            trailStr=str(prevTrail)
            sql("INSERT OR REPLACE INTO TFiles("
                " category, product_name, model"
                ",rel_date,fw_ver,file_size,page_url,download_url,tree_trail)"
                " VALUES"
                "(:category, :productName, :model,"
                ":relDate,:fwVer,:fileSize,:pageUrl,:downUrl,:trailStr)",
                glocals())
            ulog('UPSERT "%(category)s", "%(productName)s", "%(model)s",'
                ' "%(relDate)s", "%(fwVer)s", %(fileSize)s,'
                ' "%(downUrl)s", %(prevTrail)s '%glocals())
            prevTrail.pop()
        driver.back()
        waitVisible('iframe[name~=inlineFrame]')
        driver.back()
        waitVisible('.product-name-price')
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')

def selectSupport():
    global prevTrail,category,productName,model,driver
    CSS=driver.find_element_by_css_selector
    try:
        waitVisible('.product-name-price')
        productName=CSS('.product-name-price h2').text.strip()
        ulog('productName="%s"'%productName)
        # 'Wireless G Travel Router'
        model=CSS('.product-name-price p').text.strip()
        # 'Part # F5D7233'
        model = model.split('#')[1].strip()
        ulog('model="%s"'%model)
        # 'F5D7233'
        if not productName:
            ulog('productName is empty, bypass!')
            driver.back()
            waitText('.search-results-notification')
            return

        try:
            support = next(_ for _ in getElems('.icon-list-header-container') if getElemText(_).startswith('DOWNLOAD'))
        except StopIteration:
            ulog('No download in '+driver.current_url)
            trailStr=str(prevTrail)
            sql("INSERT OR REPLACE INTO TFiles(category, product_name, model, tree_trail) VALUES (:category, :model, :productName, :trailStr)", glocals())
            ulog('UPSERT "%(category)s", "%(model)s", "%(productName)s" %(prevTrail)s'%glocals())
            driver.back()
            waitText('.search-results-notification')
            return
        downloads = support.find_elements_by_css_selector('a')
        numDownloads = len(downloads)
        startIdx=getStartIdx()
        for idx in range(startIdx, numDownloads):
            txt=downloads[idx].text
            if model not in txt:
                ulog('bypass %s,"%s" because it\'s Portal'%(idx,txt))
                continue
            ulog('click %s,"%s"'%(idx,txt))
            enterElem(downloads[idx])
            prevTrail += [idx]
            selectDownload()
            prevTrail.pop()
            support = next(_ for _ in getElems('.icon-list-header-container') if getElemText(_).startswith('DOWNLOAD'))
            downloads = support.find_elements_by_css_selector('a')
        driver.back()
        waitText('.search-results-notification')
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')


searchResultsNotification=""
def selectProduct():
    global category, prevTrail, searchResultsNotification,driver
    try:
        searchResultsNotification=waitTextChanged('.search-results-notification', searchResultsNotification).strip()
        products=getElems('.items a')
        retryUntilTrue(lambda:ulog('products=%s'%[(i,_.text) for i,_ in enumerate(products)])>=0)
        numProducts=len(products)
        startIdx=getStartIdx()
        for idx in range(startIdx,numProducts):
            ulog('click %s,"%s"'%(idx,products[idx].text))
            prevTrail+=[idx]
            enterElem(products[idx])
            selectSupport()
            prevTrail.pop()
            products=getElems('.items a')
        driver.back()
        searchResultsNotification=waitTextChanged('.search-results-notification', searchResultsNotification).strip()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')


def selectCategory():
    global category, prevTrail, searchResultsNotification,driver
    try:
        if len(prevTrail)==1:
            waitVisible('.filter-list')
            searchResultsNotification=waitText('.search-results-notification').strip()
            # Your search for f returned 4196 results
        elif len(prevTrail)==2:
            searchResultsNotification=waitTextChanged('.search-results-notification', searchResultsNotification).strip()
            # Your search for f returned 67 results
        ulog('%s'%searchResultsNotification)

        category = waitText('.accordion-activate a')
        ulog('category="%s"'%category)

        cats=getElems('.filter-list a')

        retryUntilTrue(lambda:ulog('cats=%s'%[(i,_.text)for i,_ in enumerate(cats)]))
        numCats=len(cats)
        startIdx = getStartIdx()
        for idx in range(startIdx, numCats):
            ulog('click %s,"%s"'%(idx,cats[idx].text))
            enterElem(cats[idx])
            prevTrail+=[idx]
            if len(prevTrail)==2:
                selectCategory()
            else:
                selectProduct()
            prevTrail.pop()
            cats = getElems('.filter-list a')
        driver.back()
        searchResultsNotification=waitTextChanged('.search-results-notification', searchResultsNotification).strip()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')


charset='abcdefghijklmnopqrstuvwxyz0123456789'
def main():
    global startTrail, prevTrail,driver,conn
    try:
        startTrail = [int(re.search(r'\d+', _).group(0)) for _ in sys.argv[1:]]
        ulog('startTrail=%s'%startTrail)
        conn=sqlite3.connect('belkin.sqlite3')
        sql("CREATE TABLE IF NOT EXISTS TFiles("
            "id INTEGER NOT NULL,"
            "category TEXT," # ROUTER > N900 DB Wireless Router
            "product_name TEXT," # Advance N900 Dual-Band Wireless Router
            "model TEXT," # F9K1104
            "rel_date DATE," # Post Date: 06/20/2012 
            "fw_ver TEXT," # Download version: 1.00.23 
            "file_size INTEGER," # Size: 3.74 MB
            "page_url TEXT," # http://belkin.force.com/Articles/articles/en_US/Download/7371
            "download_url TEXT," # http://nextnet.belkin.com/update/files/F9K1104/v1/WW/F9K1104_WW_1.0.23.bin
            "tree_trail TEXT," # [26, 2, 1, 0, 0]
            "file_sha1 TEXT," # 5d3bc16eec2f6c34a5e46790b513093c28d8924a
            "PRIMARY KEY (id)"
            "UNIQUE(product_name,model,rel_date,fw_ver)"
            ")")
        driver=harvest_utils.getFirefox()
        driver.implicitly_wait(2.0)
        harvest_utils.driver=driver
        startIdx=getStartIdx()
        for idx in range(startIdx, len(charset)):
            ulog('idx=%s, search "%s"'%(idx,charset[idx]))
            driver.get('http://www.belkin.com/us/support-search?search=%s'%charset[idx])
            prevTrail+=[idx]
            selectCategory()
            prevTrail.pop()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')


if __name__=='__main__':
    try:
        main()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        try:
            driver.save_screenshot(getScriptName()+'_excep.png')
            driver.quit()
        except Exception:
            pass

