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
import ipdb
import traceback
from my_utils import uprint,ulog
from contextlib import suppress
import random
import math

driver,conn=None,None


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
        if query.startswith('SELECT') or 'RETURNING' in query:
            return rows.fetchall()
        else:
            return
    except sqlite3.Error as ex:
        print(ex)
        raise ex


def getDepth()->int:
    # if at "Select a Software Type" or "versionWalker"
    numCrumbs=len(getElems('.csProductSelectorBreadcrumb a'))+1
    assert numCrumbs >=2
    return numCrumbs - 2

def getCurDepthAtTreeWalker()->int:
    numCrumbs=len(getElems('#psa_crumbs a'))+1
    assert numCrumbs >2
    return numCrumbs - 2
    


def guessDate(txt:str)->datetime.datetime:
    """ txt = '08-SEP-2015'
        txt = '08/SEP/2015'
    """
    try:
        return datetime.datetime.strptime(txt, '%d-%b-%Y')
    except ValueError:
        try:
            return datetime.datetime.strptime(txt, '%d/%b/%Y')
        except Exception as ex:
            ipdb.set_trace()
            print('txt=',txt)
    except Exception as ex:
        ipdb.set_trace()
        print('txt=',txt)

def guessFileSize(txt:str)->int:
    """ txt='0.52 MB'
       txt='256 / 128'
    """
    m = re.search(r'(\d*[.])?\d+', txt, re.IGNORECASE)
    if not m:
        uprint('[guessFileSize] error txt="%s"'%txt)
        return 0
    unitTxt = txt[m.span()[1]:].strip()
    if 'MB' in unitTxt:
        return int(float(m.group(0))* 1024*1024)
    elif 'KB' in unitTxt:
        return int(float(m.group(0))* 1024)
    else:
        try:
            return int(float(m.group(0))* 1024*1024)
        except Exception as ex:
            ipdb.set_trace()
            uprint('txt=%s'%txt)

def combinePerFour(ls:[str]) -> [[str]]:
    return [ [ls[i+0],ls[i+1],ls[i+2],ls[i+3]] for i in range(0,len(ls),4) ]

def flatCarts(ls:[str])->[str]:
    """ 
    Case 1:
       ls=['Download', 'Add to Cart', 'Download', 'Add to Cart', 'Download', 'Download']
       returns ['Download add to cart', 'Download add to cart', 'Download', 'Download']
    """
    i=0
    ret=[]
    while i<len(ls):
        assert ls[i]=='download'
        if len(ls) > i+1 and 'cart' in ls[i+1].lower():
            ret += [ls[i]+' '+ls[i+1].lower()]
            i += 2
        else:
            ret += [ls[i]]
            i += 1
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
    raise TimeoutException('retryUntilTrue: timeOut=%f'%timeOut)

def cssWithText(css:str, txt:str)->WebElement:
    global driver
    return next(_ for _ in driver.find_elements_by_css_selector(css) if _.text==txt)

Mouse_Over_Again='Mouse_Over_Again'
def clickOverlayA(timeOut=6.2, pollFreq=0.3):
    global driver
    CSS=driver.find_element_by_css_selector
    CSSs=driver.find_elements_by_css_selector
    act = ActionChains(driver)
    driver.save_screenshot('clickOverlayA_1.png')
    try:
        retryUntilTrue(lambda:[
            cssWithText('#overlay_copy strong a','...').click(), 
            True][-1])
        driver.save_screenshot('clickOverlayA_2.png')
        with suppress(StaleElementReferenceException):
            overlayTxt=CSS('.overlay_body_div').text
            if overlayTxt and '...' not in overlayTxt:
                return overlayTxt
            if CSS('#image_overlay').is_displayed() == False:
                return Mouse_Over_Again
        ddrect = retryUntilTrue(lambda:cssWithText('#overlay_copy strong a','...').rect)
        driver.save_screenshot('clickOverlayA_3.png')

        time.sleep(pollFreq)
        timeElap=0
        while timeElap < timeOut:
            timeBegin= time.time()
            overlayTxt=CSS('.overlay_body_div').text
            if overlayTxt and '...' not in overlayTxt:
                return overlayTxt
            driver.save_screenshot('clickOverlayA_4.png')
            x,y=OffsetGenerator(ddrect)
            ulog('click "..." offset (x,y)=(%d,%d)'%(x,y))
            try:
                act.move_to_element_with_offset(dd,x,y).click().perform()
            except StaleElementReferenceException as ex:
                if CSS('#image_overlay').is_displayed() == False:
                    return Mouse_Over_Again
                raise ex
            time.sleep(pollFreq)
            timeElap += (time.time()-timeBegin)
    except Exception:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot('cisco_clickOverlayA.png')
    raise TimeoutException('clickOverlayA timeOut=%f'%timeOut)

def closeOverlay(timeOut=25.3, pollFreq=0.4):
    global driver
    try:
        CSS=driver.find_element_by_css_selector
        driver.save_screenshot('1.png')
        overlay = CSS('#image_overlay')
        if overlay.is_displayed()==False:
            ulog('overlay already closed. url=%s'%driver.current_url)
            return
        xbtn = CSS('#image_overlay td.overlay_colhead:nth-child(2) a:nth-child(1)')
        ulog('xbtn.rect= %s'%xbtn.rect)
        training = CSS('#training-mm-item > a:nth-child(1)')
        ulog('training.rect= %s'%training.rect)
        timeElap=0.0
        while timeElap < timeOut:
            try:
                driver.save_screenshot('2.png')
                xbtn.click()
                ulog('click x button, url=%s'%driver.current_url)
                time.sleep(pollFreq)
                # test
                ulog('check overlay.is_displayer(), url=%s'%driver.current_url)
                driver.save_screenshot('3.png')
                if overlay.is_displayed()==False:
                    return
                ulog('overlay still shown. url=%s'%driver.current_url)
                driver.save_screenshot('4.png')
            except StaleElementReferenceException as ex:
                print(ex); traceback.print_exc()
                ulog('url= %s'%driver.current_url)
            timeElap += (time.time()-timeBegin)
    except Exception as ex:
        ipdb.set_trace()
        print(ex); print(type(ex)); traceback.print_exc()
    raise TimeoutException('closeOverlay failed timeOut=%f'%timeOut)

def closeOverlayB():
    global driver
    CSS=driver.find_element_by_css_selector
    act = ActionChains(driver)
    try:
        overlay = CSS('#image_overlay')
        if overlay.is_displayed()==False:
            ulog('already closed')
            return
        act.move_to_element(CSS('#footer-nav > a:nth-child(1)')).perform()
        ulog('move to bottom right footer')
        time.sleep(1.0)
        if overlay.is_displayed()==False:
            return
        ulog('failed first time')
        act.move_to_element(CSS('#fw-mbl > p:nth-child(1) > a:nth-child(1)')).perform()
        ulog('move to top right logo')
        time.sleep(1.0)
        if overlay.is_displayed()==False:
            return
    except Exception as ex:
        ipdb.set_trace()
        print(ex); print(type(ex)); traceback.print_exc()
    ulog('failed')

def absfloor(x:float)->int:
    r = int(math.floor(abs(x)))
    return r if x>=0 else r

def OffsetGenerator(rect):
    w = rect['width']
    h = rect['height']
    x = random.uniform(-w/2.0, w/2.0)
    y = random.uniform(-h/2.0, h/2.0)
    return (absfloor(x), absfloor(y))

def waitUntilOverlayText(elm:WebElement, timeOut=7.1, pollFreq=0.5):
    global driver
    CSS=driver.find_element_by_css_selector
    act=ActionChains(driver)
    timeElap=0.0
    ulog('elm.rect=%s'%elm.rect)
    retries = 0
    while timeElap < timeOut:
        timeBegin = time.time()
        try:
            if retries==0:
                x,y=0,0
            else:
                x,y = OffsetGenerator(elm.rect)
            ulog('move to elm with ofs x=%d, y=%d'%(x,y))
            act.move_to_element_with_offset(elm,x,y).perform()
            time.sleep(pollFreq)
            imageOverlay=CSS('#image_overlay')
            if imageOverlay.is_displayed():
                return imageOverlay.text
            ulog('#image_overlay not displayed, sleep')
        except Exception:
            ipdb.set_trace()
            print(ex); print(type(ex)); traceback.print_exc()
            pass
        timeElap += (time.time()-timeBegin)
        retries += 1
    raise TimeoutException('waitUntilOverlayText: timeOut=%f'%timeOut)


def getSha512(elm)->dict:
    global driver
    try:
        while True:
            overlayTxt = waitUntilOverlayText(elm)
            # try:
            #     overlayBody = waitVisible('.overlay_body_div', 2.3, 0.4)
            # except TimeoutException:
            #     ulog("waitVisible('.overlay_body_div') timeout")
            #     return None
            # overlayTxt = overlayBody.text
            # if not overlayTxt:
            #     return None
            if '...' in overlayTxt:
                overlayTxt = clickOverlayA()
                if overlayTxt == Mouse_Over_Again:
                    continue
                else:
                    break
        ulog('overlayTxt="%s"'%overlayTxt)
        closeOverlayB()

        if not overlayTxt:
            return None
        """
        Description: Cisco Intelligent Automation for Cloud 4.1.1 Virtual Appliance. PSC appliance mode is not supported on 4.1.1.
        Release: 4.1.1
        Release Date: 12/Dec/2014
        File Name: IAC-virtual_appliance-4.1.1_v4.1.1.82511.19.ova
        Size: 5196.04 MB (5448437760 bytes)
        MD5 Checksum: 11343669d3b0cf2ae7542051b55d53cf
        SHA512 Checksum:
        ebc0fe3b234cf89b09351726eee917234e06072bc12d105de78c2321e418210152b5548a21caa19a12bf7193bc1d5674a041c4721f32b07895fd7cc2eb286fa2
        """
        lines=iter(overlayTxt.splitlines())
        for line in lines:
            line=line.strip()
            if not line:
                continue
            vaName, _, vaValue=line.strip().partition(':')
            vaValue=vaValue.strip()
            if vaName.startswith('Description'):
                fileTitle=vaValue
            elif 'Date' in vaName:
                relDate = guessDate(vaValue)
            elif vaName.startswith('Release'):
                fwVer = vaValue
            elif vaName.startswith('File Name'):
                fileName = vaValue
            elif vaName.startswith('Size'):
                m=re.search(r"(\d+)\s*bytes", vaValue, re.IGNORECASE)
                fileSize=int(m.group(1))
            elif vaName.startswith('MD5'):
                md5=vaValue
            elif vaName.startswith('SHA512'):
                if not vaValue:
                    vaValue = next(lines).strip()
                sha512=vaValue
                # assert '...' not in sha512
            else:
                ulog('vaName="%s"'%vaName)
                continue
        return dict(fwVer=fwVer, relDate=relDate, fileName=fileName, \
                fileSize=fileSize, md5=md5, sha512=sha512, fileTitle=fileTitle)
    except Exception as ex:
        ipdb.set_trace()
        print(ex); traceback.print_exc()
        driver.save_screenshot('cisco_mouseOver.png')

startTrail=[]
prevTrail=[]
def tableRowWalker(fwVer:str):
    global startTrail,prevTrail,driver
    try:
        try:
            cells = getElems('table#imageTableContainer tr td')
        except TimeoutException:
            ulog("Timeout at getElems('table#imageTableContainer tr td'); bypass!")
            return
        assert len(cells)%4==0
        numFiles=int(len(cells)/4)
        cellTxt = [getElemText(_) for _ in cells]

        try:
            carts = getElems('table#imageTableContainer tr td input', 10)
            cartsTxt = [getElemAttr(_,'title').lower().strip() for _ in carts]
            # https://software.cisco.com/download/release.html?mdfid=282822110&flowid=266&softwareid=280805680&release=15.0.2-SE8&relind=AVAILABLE&rellifecycle=MD&reltype=latest
            # fwVer='15.0.2-SE1(ED)' has len(cells)==6 and numFiles==4
            cartsTxt = flatCarts(cartsTxt)
            assert len(cartsTxt)==numFiles
            needContracts=[ int('cart' in _) for _ in cartsTxt]
            # needContract=int(int(len(cells2)/numFiles)==2)
        except TimeoutException:
            ulog('needContract= "Deferral"')
            needContracts= [-1]*numFiles # Deferral
        ulog('needContracts=%s'%needContracts)

        quats = combinePerFour(cellTxt)
        assert len(quats)==len(needContracts)
        quats = list(zip(quats, needContracts))
        fileDescs=[]
        for quat,needContract in quats:
            fileTitle=quat[0].split('\n')[0].strip()
            fileName=quat[0].split('\n')[1].strip()
            relDate=guessDate(quat[1])
            fileSize=guessFileSize(quat[2])
            fileDescs.append((fileTitle,fileName,relDate,fileSize, needContract))

        model = waitText('td.SDPBannerTitle')
        ulog('model="%s"'%model)
        pageUrl=driver.current_url

        if startTrail:
            startIdx=startTrail.pop(0)
        else:
            startIdx=0
        ulog('startIdx=%d'%startIdx)

        try:
            imageRhSide=driver.find_element_by_css_selector('div#imageRhSide')
            driver.execute_script(
                "arguments[0].scroll(0,%d);"%(62*startIdx),
                imageRhSide)
        except:
            pass

        spans=getElems('#imageTableContainer tr td span.overlay_img')
        assert len(spans)==numFiles
        for idx in range(startIdx, numFiles):
            ulog('getSha512 Trail=%s'%(prevTrail+[idx]))
            infos = getSha512(spans[idx])
            if infos:
                infos.update(dict(needContract=needContracts[idx], model=model,
                    pageUrl=pageUrl,treeTrail=str(prevTrail+[idx])))
            else:
                fileTitle,fileName,relDate,fileSize,needContract=fileDescs[idx]
                infos=dict(fileTitle=fileTitle,fileName=fileName,relDate=relDate,
                        fileSize=fileSize,needContract=needContract,
                        pageUrl=pageUrl,treeTrail=str(prevTrail+[idx]),
                        md5=None,sha512=None,model=model,fwVer=fwVer)
            sql("INSERT OR REPLACE INTO TFiles(model,"
                " fw_date,fw_ver,file_title,file_name,file_size,"
                " need_contract, page_url, tree_trail, md5, sha512) "
                "VALUES (:model,"
                " :relDate,:fwVer,:fileTitle,:fileName,:fileSize,"
                " :needContract, :pageUrl, :treeTrail, :md5, :sha512)",
                infos)
            ulog('UPSERT "%(model)s", "%(relDate)s", "%(fwVer)s", '
                '"%(fileTitle)s", "%(fileName)s", %(needContract)d,'
                ' "%(treeTrail)s", %(pageUrl)s, "%(md5)s", "%(sha512)s"'
                %infos)
    except Exception as ex:
        ipdb.set_trace()
        print(ex); traceback.print_exc()
        driver.save_screenshot('cisco_tableRowWalker.png')


def versionWalker():
    global startTrail,prevTrail,driver
    try:
        waitClickable('.treeLinks > a:nth-child(1)')
        ulog('current_url=%s'%driver.current_url)
        crumbs=waitText('.csProductSelectorBreadcrumb').replace('\n', ' > ')
        ulog('crumbs=%s'%crumbs)

        # click Expand All
        numNodes = len(driver.find_elements_by_css_selector('.tree a'))
        ulog('number of versions=%d'%numNodes)
        try:
            with UntilTextChanged('.tree'):
                clickElem(waitClickable('.treeLinks > a:nth-child(1)'))
        except TimeoutException:
            pass
        treeText=waitText('.tree')
        ulog('treeText="%s"'%treeText)

        if startTrail:
            startIdx=startTrail.pop(0)
        else:
            startIdx=1
        ulog('startTrail=%s'%startTrail)
        ulog('prevTrail=%s'%prevTrail)
        ulog('startIdx=%d'%startIdx)
        assert startIdx >= 1

        try:
            prevFwVer=waitText('.tree a.nodeSel', 5)
        except TimeoutException:
            uprint("css='.tree a.nodeSel' not found")
            prevFwVer=None
        ulog('prevFwVer="%s"'%prevFwVer)
        for idx in range(startIdx, numNodes):
            nodes = driver.find_elements_by_css_selector('.tree a')
            isLeaf = (nodes[idx-1].text != '')
            ulog('goto Trail=%s'%(prevTrail+[idx]))
            if isLeaf:
                if not nodes[idx].text.strip():
                    continue
                fwVer=nodes[idx].text.strip()
                nodeClass=nodes[idx].get_attribute('class')
                ulog('fwVer="%s", nodeClass="%s"'%(fwVer,nodeClass))
                if 'nodeSel' not in nodeClass:
                    noWait= (prevFwVer==fwVer) if prevFwVer else False
                    try:
                        with UntilTextChanged('table#imageTableContainer',10,1,noWait):
                            ulog('Click "%s"'%fwVer)
                            clickElem(nodes[idx])
                    except TimeoutException:
                        with UntilTextChanged('table#imageTableContainer',10,1,noWait):
                            ulog('Click "%s" twice'%fwVer)
                            clickElem(nodes[idx])

                        
                prevTrail+=[idx]
                tableRowWalker(fwVer)
                prevTrail.pop()
                prevFwVer=fwVer
        # go back page
        crumbs=getElems('.csProductSelectorBreadcrumb a')
        ulog('backto "%s"'%getElemText(crumbs[-1]))
        ulog('prevTail=%s'%prevTrail)
        if prevTrail==[2, 1, 0, 1, 2, 0]:
            ipdb.set_trace()
        clickElem(crumbs[-1])
    except Exception as ex:
        ipdb.set_trace()
        print(ex); traceback.print_exc()
        driver.save_screenshot('cisco_versionWalker.png')


def selectSoftwareType():
    """ This page would be jumped to versionWalker() 
       or either jumped back to treeWalker
       forward: may auto jump
       backward: not auto jump
    """
    global startTrail,prevTrail,driver
    try:
        waitText('.csProductSelectorBreadcrumb', 5, 1)
        waitUntilStable('.csProductSelectorBreadcrumb', 1, 0.3)
        depth = getDepth()
        jumpedLevels =depth - len(prevTrail)
        ulog('jumpedLevels=%d'%jumpedLevels)
        assert jumpedLevels>=0
        ulog('depth=%d, but prevTrail=%s'%(depth, prevTrail))

        startIdxFromStartTrail=False
        def getStartIdx()->int:
            if startTrail:
                nonlocal startIdxFromStartTrail
                startIdxFromStartTrail=True
                return startTrail.pop(0)
            else:
                return 0

        if jumpedLevels>0:
            while depth>len(prevTrail):
                startIdx=getStartIdx()
                prevTrail+=[startIdx]
        else:
            startIdx=getStartIdx()

        assert depth==len(prevTrail)
        ulog('startTrail=%s'%startTrail)
        ulog('prevTrail=%s'%prevTrail)
        ulog('startIdx=%d'%startIdx)

        ulog('url=%s'%driver.current_url)
        crumbs = waitText('.csProductSelectorBreadcrumb')
        uprint('crumbs=%s'%(crumbs.replace('\n',' > ')))

        if not hasElem('table#imageTableContainer', 1.5,0.4):
            if jumpedLevels>0:
                startIdx=getStartIdx()
                if depth > len(prevTrail):
                    prevTrail+=[startIdx]
            sdpBannerTitle=waitText('td.SDPBannerTitle').strip()
            ulog('SDBBannerTitle="%s"'%sdpBannerTitle)
            assert sdpBannerTitle.lower().startswith('select ')
            waitUntil(lambda: getNumElem('div.csWrapper li a') > 0)
            swtypes = getElems('div.csWrapper li a')
            ulog('%s'%[(i,getElemText(_)) for i,_ in enumerate(swtypes)])
            numSwTypes=len(swtypes)
            assert numSwTypes > 0
            for idx in range(startIdx, numSwTypes):
                ulog('goto Trail=%s'%(prevTrail+[idx]))
                swtypes = getElems('div.csWrapper li a')
                ulog('Click "%s"'% getElemText(swtypes[idx]))
                clickElem(swtypes[idx])
                prevTrail+=[idx]
                selectSoftwareType()
                prevTrail.pop()
            # Select a Product -> Select a Software type -> Select a Platform
            # https://software.cisco.com/download/type.html?mdfid=277873153&flowid=170&softwareid=283724313
            # Downloads Home >Products >Cisco Interfaces and Modules >WAN Interface Cards >1700/2600/3600/3700 Series 2-Port Analog Modem WAN Interface Card >Analog Firmware Loader >Windows 2000-v6780 
            # not auto back to treeWalker
            # go back manually
            crumbs = getElems('.csProductSelectorBreadcrumb a')
            ulog('manually backto "%s"'%getElemText(crumbs[-1]))
            ulog('prevTail=%s'%prevTrail)
            clickElem(crumbs[-1])
            # do I need to pop prevTrail?
            # prevTrail.pop()
        else:
            ulog('auto forward to versionWalker')
            if startIdxFromStartTrail:
                startTrail.insert(0, startIdx)
            for i in range(jumpedLevels):
                if not startTrail:
                    break
                startTrail.pop(0)
            versionWalker()
        for i in range(jumpedLevels):
            crumbs = getElems('.csProductSelectorBreadcrumb a')
            ulog('manually backto "%s"'%getElemText(crumbs[-1]))
            ulog('prevTail=%s'%prevTrail)
            clickElem(crumbs[-1])
            prevTrail.pop()
    except Exception as ex:
        ipdb.set_trace()
        print(ex); traceback.print_exc()
        driver.save_screenshot('cisco_selectSoftwareType.png')


def treeWalker():
    global startTrail,prevTrail, driver
    def getNodes():
        return getElems('#psbox3 li a' if prevTrail else '#psbox2 li a')
    nodes=getNodes()
    numNodes=len(nodes)

    if startTrail:
        startIdx=startTrail.pop(0)
    else:
        startIdx=0

    ulog('startTrail=%s'%startTrail)
    ulog('prevTrail=%s'%prevTrail)
    ulog('startIdx=%d'%startIdx)

    nodeTxts=[getElemText(_) for _ in getNodes()]
    ulog('nodes=%s (len=%d)'%([(i,_) for i,_ in enumerate(nodeTxts)],numNodes))
    for idx in range(startIdx, numNodes):
        try:
            crumbs=waitText('#psa_crumbs').replace('\n',' > ')
            ulog('crumbs=%s'%crumbs)
            nodeTxt = getElemText(nodes[idx])
            nodeId = nodes[idx].get_attribute('id').strip()
            ulog('nodeId="%s"'%nodeId)
            if not nodeId: # isLeaf
                ulog('Click Leaf "%s"'%nodeTxt)
                clickElem(nodes[idx])
                with suppress(StaleElementReferenceException):
                    nodes[idx].click()
                prevTrail+=[idx]
                # if not waitUntil(lambda: not driver.find_elements_by_css_selector('#psbox3')):
                #     nodes[idx].click()
                selectSoftwareType()
                prevTrail.pop()
                assert getCurDepthAtTreeWalker()==len(prevTrail)
                nodes=getNodes()
                continue
            with UntilTextChanged('#psbox3'):
                ulog('Click branch "%s"'%nodeTxt)
                clickElem(nodes[idx])
            prevTrail+=[idx]
            treeWalker()
            prevTrail.pop()
            nodes=getNodes()
        except Exception as ex:
            ipdb.set_trace()
            print(ex); traceback.print_exc()
            driver.save_screenshot('cisco_treeWalker.png')
    # end for
    crumbs=getElems('#psa_crumbs a')
    ulog('back to "%s"'%getElemText(crumbs[-1]))
    ulog('prevTrail=%s'%prevTrail)
    clickElem(crumbs[-1])


def main():
    global startTrail,prevTrail
    startTrail = [int(re.search(r'\d+', _).group(0)) for _ in sys.argv[1:]]
    uprint('startTrail=%s'%startTrail)
    global driver,conn
    conn=sqlite3.connect('cisco.sqlite3')
    sql(
        "CREATE TABLE IF NOT EXISTS TFiles("
        "id INTEGER NOT NULL,"
        "model TEXT,"
        "fw_date DATE,"
        "fw_ver TEXT,"
        "file_title TEXT,"
        "file_name TEXT,"
        "file_size INTEGER,"
        "need_contract INTEGER," # 1=needContract, -1=Deferral
        "page_url TEXT,"
        "tree_trail TEXT," # pssub_7_1_1_0_0_0 => 7_1_1_0_0_0
        "file_sha1 TEXT,"
        "PRIMARY KEY (id)"
        "UNIQUE(model,fw_ver,file_name,fw_date)"
        ");")
    driver=harvest_utils.getFirefox(path.abspath('cisco_files'), 2, False)
    driver.implicitly_wait(2.0)
    harvest_utils.driver=driver
    driver.get('https://software.cisco.com/download/')
    prevTrail=[]
    treeWalker()
    prevTrail.pop()
    

if __name__=='__main__':
    try:
        main()
    except Exception as ex:
        ipdb.set_trace()
        print(str(ex)); traceback.print_exc()
        try:
            driver.save_screenshot('cisco.png')
            driver.quit()
        except Exception:
            pass

