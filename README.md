# Belkin_Harvest
Belkin Firmware Files Harvest

<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f.png" >
```python
[_.text for _ in CSSs('.filter-list a')]
>>> "['Access Points', 'Business', 'Business Networking', 'Cables', 'Commercial', 'Conserve', 'Desktop Accessories', 'Enterprise', 'Entertainment', 'Gaming', 'Home Theater', 'KVM', 'Kindle Tablets', 'Laptop', 'Modems', 'Network Adapters', 'Network Cameras', 'Network Switches', 'Power', 'Powerline', 'Router', 'Samsung Phone and Tablet', 'Tablet', 'Thunderbolt', 'USB and Firewire', 'VoIP', 'WEMO', 'Yolk Case Creation', 'iPad', 'iPhone 5', 'iPhone 6', 'iPhone, iPod and MP3']"
```


<img src="https://raw.githubusercontent.com/MikimotoH/Belkin_Harvest/master/belkin_f_Router.png" >
```python
In [43]: CSS('.accordion-activate a').text
Out[43]: 'ROUTER'
In [45]: str([_.text for _ in CSSs('.filter-list a')])
Out[45]: "['10/100', 'AC1000 Wireless Router', 'AC1200 Wireless Router', 'AC1800 Wireless Router', 'AC2000', 'AC800', 'AC900 Wireless Router', 'B', 'Basic / Connect N150', 'G', 'N', 'N150', 'N150 Wireless Router', 'N300 Wireless Router', 'N450 Wireless Router', 'N600 DB Wireless Router', 'N750 DB Wireless Router', 'N900 DB Wireless Router', 'Play/Play Max/Play N600/Play N600 HD', 'Router', 'Share / Share MAX / Share N300', 'Surf / Surf N300', 'Surf N150', 'VPN', 'Wireless Dual Band N']"
```
