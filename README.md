# Belkin_Harvest
Belkin Firmware Files Harvest

<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f.png" >
```python
>>>  [_.text for _ in CSSs('.filter-list a')]
"['Access Points', 'Business', 'Business Networking', 'Cables', 'Commercial', 'Conserve', 'Desktop Accessories', 'Enterprise', 'Entertainment', 'Gaming', 'Home Theater', 'KVM', 'Kindle Tablets', 'Laptop', 'Modems', 'Network Adapters', 'Network Cameras', 'Network Switches', 'Power', 'Powerline', 'Router', 'Samsung Phone and Tablet', 'Tablet', 'Thunderbolt', 'USB and Firewire', 'VoIP', 'WEMO', 'Yolk Case Creation', 'iPad', 'iPhone 5', 'iPhone 6', 'iPhone, iPod and MP3']"
```


<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f_Router.png" >
```python
In [43]: CSS('.accordion-activate a').text
Out[43]: 'ROUTER'

In [45]: str([_.text for _ in CSSs('.filter-list a')])
Out[45]: "['10/100', 'AC1000 Wireless Router', 'AC1200 Wireless Router', 'AC1800 Wireless Router', 'AC2000', 'AC800', 'AC900 Wireless Router', 'B', 'Basic / Connect N150', 'G', 'N', 'N150', 'N150 Wireless Router', 'N300 Wireless Router', 'N450 Wireless Router', 'N600 DB Wireless Router', 'N750 DB Wireless Router', 'N900 DB Wireless Router', 'Play/Play Max/Play N600/Play N600 HD', 'Router', 'Share / Share MAX / Share N300', 'Surf / Surf N300', 'Surf N150', 'VPN', 'Wireless Dual Band N']"
```

<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f_Router_G.png">
```python
In [61]: CSS('.search-results-notification').text
Out[61]: 'Your search for f returned 14 results'

In [64]: str([(i,_.text) for i,_ in enumerate(CSSs('.items a span'))])
Out[64]: "[(0, 'G Wireless Router'), (1, 'Wireless G Travel Router'), (2, 'Wireless G+ MIMO Router'), (3, 'N150 Enhanced Wireless Router')]"
```

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


<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_art_4971.png">
```python
In [87]: CSS('iframe[name~=inlineFrame]').get_attribute('src')
Out[87]: 'http://belkin.force.com/Articles/apex/pkb_viewArticle?articleNum=000004971&l=en_US'
```


<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_art_23.png">
This page is another portal page, not download page. Go back. 

<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_art4450.png">
```python
In [96]: CSS('iframe[name~=inlineFrame]').get_attribute('src')
Out[96]: 'http://belkin.force.com/Articles/apex/pkb_viewArticle?articleNum=000004450&l=en_US'
```


<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_F5D7233v1_Download.png">
```python
In [101]: CSS('#articleContainer').text                                                                                                                                
Out[101]: 'Wireless G Travel Router F5D7233 v1 - Firmware (US)\nAfter you download your firmware file click here for installation instructions.\nVersion 1xxx\nDownload version: 1.01.20, OS compatibility: Any, size: 768KB\n\n '

In [102]: artTxt=CSS('#articleContainer').text

# Get file_fize
In [108]: re.search(r'size:(.+)', artTxt, re.IGNORECASE)
Out[108]: <_sre.SRE_Match object; span=(195, 206), match='size: 768KB'>

# Get firmware_version
In [110]: re.search(r'version:\s*(\d+(\.\d+)*)', artTxt, re.IGNORECASE)
Out[110]: <_sre.SRE_Match object; span=(154, 170), match='version: 1.01.20'>

# Get download_url
In [117]: next(_.get_attribute('href') for _ in CSSs('a') if _.text.startswith('Download'))
Out[117]: 'http://cache-www.belkin.com/support/dl/f5d7233v1_us_1_01_20.bin'
```

