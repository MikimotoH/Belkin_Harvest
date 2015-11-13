#!/usr/bin/env python3
#coding: utf-8
import re
import datetime
from datetime import datetime
import pdb
import traceback

ex_artTxt1=r"""
This product has multiple versions.  Please check the version number on your router to ensure that you load the appropriate firmware below.  
  
Click [here](http://www.belkin.com/us/support-article?articleNum=8064) for help on finding your version number.  
  
After you download your firmware file click [here](http://www.belkin.com/us/support-article?articleNum=10797) for installation instructions.  
  
Version 2xxx Firmware

  * [Download](http://cache-www.belkin.com/support/dl/f5d9230-4-v2_usa_2.00.02.bin) version: 2.00.02, OS compatibility: Any, size: 3.22 MB

###  Version 3xxx Firmware

  * [Download](http://cache-www.belkin.com/support/dl/f5d9230-4v3_uk_3.01.53.bin) version: 3.01.53, OS compatibility: Any, size: 2.16 MB

###  Version 4xxx Firmware

  * [Download](http://cache-www.belkin.com/support/dl/20061222_belkin_f5d9230us4_4.01.09\(mr\).bin) version: 4.01.09, OS compatibility: Any, size: 747 KB

###  Version 5xxx Firmware

  * [Download](http://cache-www.belkin.com/support/dl/f5d9230-4_ww_5.02.08.bin) version: 5.02.08, OS compatibility: Any, size: 2.68 MB
"""

ex_artTxt2=r""" Download version: 1.0, OS compatibility: Windows 98 SE, Windows 2000, Windows ME, Windows XP 32 Bit, size: 588KB """

ex_artTxt3=r"""The Belkin AC 1800 DB Wi-Fi Dual-Band AC+ Gigabit Router, F9K1118 is the fastest dual-band speed router for video streaming and gaming.  It comes with two (2) USB 2.0 Ports for ultra-fast media streaming and printer sharing.  The Belkin AC1800 router works seamlessly with N and G Wi-Fi devices.

 Updating your wireless router's firmware fixes the previous version's bugs and improves its functionality.  This action must be done especially if you start experiencing connectivity issues with your device.

  IMPORTANT:  This device has multiple versions.  Please check the version number on your router to ensure that you load the appropriate firmware below.  For instructions on how to find your version number, click here.

  Version 1xxx Firmware
  Posted date: 10/26/2012

   Release Notes
   Improved HTML loading times for both setup and firmware interface.
   Fixes the FW update within the firmware interface to point at the correct URL.
   Fixes issue where media server will cause router reset when browsing photos.
   Fixes issue where devices moving from guest network to standard network are shown twice in the connected devices list and fixes some devices not being listed.
   version: 1.03.04, OS compatibility: Windows 7 32 bit;Windows 7 64 bit;Windows Vista 32 bit;Windows Vista 64 bit;Windows XP 32 bit;Windows XP 64 bit;Mac OS 10.6;Mac OS 10.5;Mac OS 10.4;Mac OS 10.7; MAC OS 10.8; Apple iOS 4;Apple iOS 5;Android 2.3;Android 2.4, Android 4.x; Size: 9.85 MB

    Download version:  1.00.25, OS compatibility: Any, Size: 8.26 MB
    Version 2xxx Firmware

     Post Date: 4/15/2014

      Release Notes
      Fixed buffer overflow bug in MiniHttpd
      OS compatibility: Windows 7 32 bit;Windows 7 64 bit;Windows Vista 32 bit;Windows Vista 64 bit;Windows XP 32 bit;Windows XP 64 bit;Windows 2000;Mac OS 10.6;Mac OS 10.5;Mac OS 10.4;Mac OS 10.7;Apple iOS 4;Apple iOS 5;Android 2.3;Android 2.4

       Download version: 2.03.38; Size: 7.5 MB
       To know how to update the firmware of your router, click here.  """

ex_artTxt3=r"""
The Belkin AC 1800 DB Wi-Fi Dual-Band AC+ Gigabit Router, F9K1118 is the fastest dual-band speed router for video streaming and gaming.  It comes with two (2) USB 2.0 Ports for ultra-fast media streaming and printer sharing.  The Belkin AC1800 router works seamlessly with N and G Wi-Fi devices.  
   
Updating your wireless router's firmware fixes the previous version's bugs and improves its functionality.  This action must be done especially if you start experiencing connectivity issues with your device.    
   
IMPORTANT:  This device has multiple versions.  Please check the version number on your router to ensure that you load the appropriate firmware below.  For instructions on how to find your version number, click [here](http://www.belkin.com/us/support-article?rnId=6356).   
  
Version 1xxx Firmware  
   
Posted date: 10/26/2012  
   
Release Notes  


  * Improved HTML loading times for both setup and firmware interface.
  * Fixes the FW update within the firmware interface to point at the correct URL.
  * Fixes issue where media server will cause router reset when browsing photos.
  * Fixes issue where devices moving from guest network to standard network are shown twice in the connected devices list and fixes some devices not being listed.
version: 1.03.04, OS compatibility: Windows 7 32 bit;Windows 7 64 bit;Windows Vista 32 bit;Windows Vista 64 bit;Windows XP 32 bit;Windows XP 64 bit;Mac OS 10.6;Mac OS 10.5;Mac OS 10.4;Mac OS 10.7; MAC OS 10.8; Apple iOS 4;Apple iOS 5;Android 2.3;Android 2.4, Android 4.x; Size: 9.85 MB  
   
[Download](http://cache-www.belkin.com/support/dl/F9K1118_WW_1.00.25.bin) version:  1.00.25, OS compatibility: Any, Size: 8.26 MB  
   
Version 2xxx Firmware  
   
Post Date: 4/15/2014  
   
Release Notes  


  * Fixed buffer overflow bug in MiniHttpd
OS compatibility: Windows 7 32 bit;Windows 7 64 bit;Windows Vista 32 bit;Windows Vista 64 bit;Windows XP 32 bit;Windows XP 64 bit;Windows 2000;Mac OS 10.6;Mac OS 10.5;Mac OS 10.4;Mac OS 10.7;Apple iOS 4;Apple iOS 5;Android 2.3;Android 2.4  
   
[Download](http://cache-www.belkin.com/support/dl/F9K1118v2_WW_2.03.38.bin) version: 2.03.38; Size: 7.5 MB  
   
To know how to update the firmware of your router, click [here](http://www.belkin.com/us/support-article?articleNum=10797).
"""

ex_artTxt4=r"""
The Belkin AC 1800 DB Wi-Fi Dual-Band AC+ Gigabit Router, F9K1118 is the fastest dual-band speed router for video streaming and gaming.  It comes with two (2) USB 2.0 Ports for ultra-fast media streaming and printer sharing.  The Belkin AC1800 router works seamlessly with N and G Wi-Fi devices.

Updating your wireless router's firmware fixes the previous version's bugs and improves its functionality.  This action must be done especially if you start experiencing connectivity issues with your device.  This article will provide you firmware updates for your Belkin AC 1800 DB Wi-Fi Dual-Band AC+ Gigabit Router, F9K1118 v2.    IMPORTANT:  This device has multiple versions.  Please check the version number on your router to ensure that you load the appropriate firmware below.  For instructions on how to find your version number, click [here](http://www.belkin.com/us/support-article?articleNum=8064).      Version 2 Firmware     IMPORTANT: Do NOT power cycle the Router during the firmware upgrade process.     Firmware version: 2.03.43   Post Date: 12/12/2014      Release Notes: 

  * Resolved IPv6 connection issue for ISP customer.
  * Resolved UPnP issue with customer device.[Download](http://cache-www.belkin.com/support/dl/F9K1118v2_WW_2.03.43.bin); Size: 7.48 MB  
===========================================================================  
Download version: 2.03.36  Post Date: 9/20/2013 

  * Initial release===========================================================================  
Version 2 Firmware  
   
Post Date: 8/13/2014  
   
Release Notes:

  * Resolved 2.4 G low throughput issue while WAN port > 1 G Mbps
  * Resolved WIFI UI SSID page for changing 20/40 MHz back to 20 MHz not working issue
  * To support BCM4708/47081 rev. A4 chip
[Download](http://cache-www.belkin.com/support/dl/F9K1118v2_WW_2.03.40.bin) version: 2.03.40; OS compatibility:  Windows 8 64 bit; Windows 8.1 32 bit; Windows 8.1 64 bit;  Windows 7 32 bit; Windows 7 64 bit; Windows Vista 32 bit; Windows Vista 64 bit; Mac OS 10.4  
  
To know how to update the firmware of your router, click [here](http://www.belkin.com/us/support-article?articleNum=10797).

"""

def guessVersion(txt:str)->str:
    m=re.search(r'version:\s*(\d+[\.\d]*)', txt, re.I)
    if m:
        return m.group(1)
    else:
        return None

def guessFileSize(txt:str)->int:
    m = re.search(r'size:\s*(\d+\.?\d+?)\s*(KB|MB)', txt, re.I)
    if m:
        unitDic=dict(KB=1024,MB=1024*1024)
        return int(float(m.group(1)) * unitDic[m.group(2).upper()])
    else:
        return None

def guessDate(txt:str) -> datetime:
    m = re.search(r'\d{1,2}/\d{1,2}/\d{4}', txt)
    if m:
        try:
            return datetime.strptime(m.group(0), '%m/%d/%Y')
        except ValueError:
            return datetime.strptime(m.group(0), '%d/%m/%Y')
    else:
        return None

def getSizeDateVersion(txt:str, ithDownload:int)->(int,datetime,str,str):
    lines = txt.splitlines()
    def getLineIdx():
        numDownloads=0
        for lineIdx,line in enumerate(lines):
            if '[Download]' in line:
                if numDownloads == ithDownload:
                    return lineIdx
                numDownloads+=1
        return -1
    lineIdx=getLineIdx()
    if lineIdx==-1:
        raise StopIteration('ithDownload=%d'%ithDownload)
    fileSize,relDate,version=None,None,None
    downUrl=None
    for idx,line in enumerate(lines[lineIdx::-1]):
        line = line
        if '[Download]'in line:
            if idx>0:
                break
            if not downUrl:
                downUrl=re.search(r'\[Download\]\((.+?)\)',line).group(1)
        if not fileSize:
            fileSize = guessFileSize(line)
        if not relDate:
            relDate = guessDate(line)
        if not version:
            version = guessVersion(line)
        if fileSize is not None and relDate is not None and version is not None:
            return fileSize,relDate,version,downUrl
    return fileSize,relDate,version,downUrl


def main():
    for iArt,artTxt in enumerate([ex_artTxt1,ex_artTxt2,ex_artTxt3,ex_artTxt4], 1):
        for i in range(20):
            try:
                fileSize,relDate,fwVer,downUrl=getSizeDateVersion(artTxt, i)
                print('artText%d'%iArt)
                print('  idthDownload=%d'%i)
                print('    size,date,ver=(%s,%s,%s)'%(fileSize,relDate,fwVer))
                print('    url= %s'%downUrl)
            except StopIteration:
                print('StopIteration at ithDownload=%d'%i)
                break

if __name__=='__main__':
    try:
        main()
    except Exception as ex:
        traceback.print_exc()
        print(ex); print(type(ex))
