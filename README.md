
# Belkin Harvest
Belkin Firmware Files Harvest

## selectCategory() (1) 
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f.png" >
```python
>>>  [_.text for _ in CSSs('.filter-list a')]
"['Access Points', 'Business', 'Business Networking', 'Cables', 'Commercial', 'Conserve', 'Desktop Accessories', 'Enterprise', 'Entertainment', 'Gaming', 'Home Theater', 'KVM', 'Kindle Tablets', 'Laptop', 'Modems', 'Network Adapters', 'Network Cameras', 'Network Switches', 'Power', 'Powerline', 'Router', 'Samsung Phone and Tablet', 'Tablet', 'Thunderbolt', 'USB and Firewire', 'VoIP', 'WEMO', 'Yolk Case Creation', 'iPad', 'iPhone 5', 'iPhone 6', 'iPhone, iPod and MP3']"
```

## selectCategory() (2) 
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f_Router.png" >
```python
In [43]: CSS('.accordion-activate a').text
Out[43]: 'ROUTER'

In [45]: str([_.text for _ in CSSs('.filter-list a')])
Out[45]: "['10/100', 'AC1000 Wireless Router', 'AC1200 Wireless Router', 'AC1800 Wireless Router', 'AC2000', 'AC800', 'AC900 Wireless Router', 'B', 'Basic / Connect N150', 'G', 'N', 'N150', 'N150 Wireless Router', 'N300 Wireless Router', 'N450 Wireless Router', 'N600 DB Wireless Router', 'N750 DB Wireless Router', 'N900 DB Wireless Router', 'Play/Play Max/Play N600/Play N600 HD', 'Router', 'Share / Share MAX / Share N300', 'Surf / Surf N300', 'Surf N150', 'VPN', 'Wireless Dual Band N']"
```

## selectProduct()
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f_Router_G.png">
```python
In [61]: CSS('.search-results-notification').text
Out[61]: 'Your search for f returned 14 results'

In [64]: str([(i,_.text) for i,_ in enumerate(CSSs('.items a span'))])
Out[64]: "[(0, 'G Wireless Router'), (1, 'Wireless G Travel Router'), (2, 'Wireless G+ MIMO Router'), (3, 'N150 Enhanced Wireless Router')]"
```

## selectSupport()
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f_Router_G_Wireless_G_Travel_Router.png">
```python
In [75]: CSS('.product-name-price').text.strip()
Out[75]: 'Wireless G Travel Router\nPart # F5D7233'

In [76]: CSS('.product-info img').get_attribute('src')
Out[76]: 'http://www.belkin.com/images/product/F5D7233/STD1_F5D7233.jpg'

In [77]: CSSs('.icon-list-header-container h2')[2].text
Out[77]: 'DOWNLOADS'

In [80]: str([_.text for _ in CSSs('.icon-list-header-container')[2].find_elements_by_css_selector('a')])
Out[80]: "['Belkin router firmware updates', 'Wireless G Travel Router F5D7233 v1 - Firmware (US)']"
```

## selectDownload() go into iframe
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_art4450.png">
```python
In [96]: CSS('iframe[name~=inlineFrame]').get_attribute('src')
Out[96]: 'http://belkin.force.com/Articles/apex/pkb_viewArticle?articleNum=000004450&l=en_US'
```

## selectDownload() guess Date, fileSize, version
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_F5D7233v1_Download.png">

Use [html2text](https://github.com/aaronsw/html2text) to convert HTML to plain text with URL link.
```python
page_src = waitVisible('.sfdc_richtext').get_attribute('innerHTML')
h = html2text.HTML2Text()
h.ignore_emphasis=True # don't add '*' surrounding word
h.body_width=0 # don't wrap long line
artTxt = h.handle(page_src)
```

The artTxt becomes to
```markdown
After you download your firmware file click [here](http://www.belkin.com/us/support-article?articleNum=10797) for installation instructions.  

###  Version 1xxx

  * [Download](http://cache-www.belkin.com/support/dl/f5d7233v1_us_1_01_20.bin) version: 1.01.20, OS compatibility: Any, size: 768KB
```

```python
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
        return datetime.strptime(m.group(0), '%m/%d/%Y')
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
```

## selectDownload() - Wrong Case
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_art_4971.png">
```python
In [87]: CSS('iframe[name~=inlineFrame]').get_attribute('src')
Out[87]: 'http://belkin.force.com/Articles/apex/pkb_viewArticle?articleNum=000004971&l=en_US'
```

## selectDownload() - Wrong Case
<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_art_23.png">
This page is another portal page, not download page. Go back. 

