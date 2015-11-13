#!/usr/bin/env python3
# coding:utf-8
import sqlite3
import re
from web_utils import firefox_url_req,urlFileName,downloadFile,safeFileName,\
        uprint, getFileSha1
from os import path
import os
import sys
import urllib
import traceback
import ftputil
from ftp_credentials import ftpHostName,ftpUserName,ftpPassword


conn=None
dlDir=path.abspath('firmware_files/')

def main():
    startIdx = int(sys.argv[1]) if len(sys.argv)>1 else 0
    global conn
    with sqlite3.connect('Linksys.sqlite3') as conn:
        csr=conn.cursor()
        rows=csr.execute(
            "SELECT brand,model,revision,file_title,href,file_sha1 FROM TFiles "
            "LIMIT -1 OFFSET %d"%startIdx).fetchall()
        for idx, row in enumerate(rows,startIdx):
            brand,model,revision,fileTitle,url,fileSha1=row
            print('idx= %d, fileSha1=%s'%(idx, fileSha1))
            if fileSha1:
                uprint('"%s" already downloaded, bypass!'%fileTitle)
                continue
            if not url:
                continue
            fname=urlFileName(url)
            if not fname:
                fname = safeFileName(fileTitle)
            uprint('url='+url)
            uprint('download "%s" as "%s"'%(fileTitle,fname))
            fname = path.join(dlDir, fname)
            try:
                downloadFile(url, fname)
            except urllib.error.HTTPError:
                print(ex)
                continue
            except OSError as ex:
                if ex.errno == 28:
                    print(ex)
                    print('[Errno 28] No space left on device')
                    break
            except Exception as ex:
                import pdb; pdb.set_trace()
                import traceback; traceback.print_exc()
                print(ex)
                continue

            fileSha1=getFileSha1(fname)
            fileSize=path.getsize(fname)
            print('sha1="%s" for "%s"'%(fileSha1,fname))
            csr.execute(
                "UPDATE TFiles SET file_sha1=:fileSha1, file_size=:fileSize"
                " WHERE brand=:brand AND model=:model AND revision=:revision"
                " AND file_title=:fileTitle",locals())
            conn.commit()
            print('UPDATE fileSha1=%(fileSha1)s, fileSize=%(fileSize)d'
                ' WHERE "%(brand)s", "%(model)s", "%(revision)s", '
                '"%(fileTitle)s" '%locals())
            with ftputil.FTPHost(ftpHostName,ftpUserName,ftpPassword) as ftp:
                ftp.upload(fname, path.basename(fname))
                print('uploaded "%s" to ftp://%s/'
                    %(path.basename(fname), ftpHostName))
            os.remove(fname)

if __name__=='__main__':
    main()
