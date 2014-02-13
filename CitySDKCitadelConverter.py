import urllib2
import cookielib
import json

class Object:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

LANG = "pt-PT"
CITY = "Lisboa"

site= "http://tourism.citysdk.cm-lisboa.pt/pois/search?limit=-1"

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

req = urllib2.Request(site, headers=hdr)

try:
    page = urllib2.urlopen(req)
except urllib2.HTTPError, e:
    print e.fp.read()

content = page.read()
decoded_data = json.loads(content)

dataset = Object()
general = Object()
general.id = "http://tourism.citysdk.cm-lisboa.pt/resources"
general.updated = "20121128T09:38:21-5:00"
general.created = "20121128T09:38:21-5:00"
general.lang = LANG
general.updatefrequency = "semester"

author = Object()
author.id = "http://tourism.citysdk.cm-lisboa.pt/resources"
author.value = "CitySDK"
general.author = author

license = Object()
license.href = "http://www.gnu.org/licenses/gpl.html"
license.term = "GNU GPL"
general.license = license

link = Object()
link.href = "http://tourism.citysdk.cm-lisboa.pt/resources"
link.term = "source"
general.link = link

general.poi = []

for i in decoded_data['poi']:
    me = Object()
    me.id = i['id']

    me.title = ""
   
    if 'label' in i:
        for j in i['label']:
            if 'lang' in j:
                if j['lang'] == LANG:
                    me.title = j['value']
            elif 'lang' in i:
                if i['lang'] == LANG:
                    me.title = j['value']


    me.description = ""
    if 'description' in i:
        for j in i['description']:
           if 'lang' in j:
                if j['lang'] == LANG:
                    me.description = j['value']
           elif 'lang' in i:
                if i['lang'] == LANG:
                    me.description = j['value']

    me.category = []
    if 'category' in i:
        for j in i['category']:
            if 'lang' in j:
                if j['lang'] == LANG:
                    me.category.append(j['value'])
            elif 'lang' in i:
                if i['lang'] == LANG:
                    me.category.append(j['value'])

    me.location = Object()
    
    pos = Object()
    pos.srsName = "http://www.opengis.net/def/crs/EPSG/0/4326"
    pos.posList = ""
    
    address = Object()
    address.value = ""
    address.postal = ""
    address.city = CITY

    if 'location' in i:
        if 'point' in i['location']:
            for j in i['location']['point']:
                pos.posList = j['Point']['posList']
        #if 'address' in i['location']:
            #if 'type' in i['location']['address']:
                #if i['location']['address']['type'] == "text/vcard":
                    #address.value = i['location']['address']['value']
                    #address.postal =  i['location']['address']['value']
                
    point = Object()
    point.term = "centroid"
    point.pos = pos
    
    me.location.point = point
    me.location.address = address
    
    tel = Object()
    tel.term = "telephone"
    tel.type = "tel"
    tel.text = ""
    tel.tplIdentifier = "#Citadel_telephone"
    
    mail = Object()
    mail.term = "email"
    mail.type = "mail"
    mail.text = ""
    mail.tplIdentifier = "#Citadel_email"

    url = Object()
    url.term = "website"
    url.type = "url"
    url.text = ""
    url.tplIdentifier = "Citadel_website"
 
    me.attribute = []
    me.attribute.append(tel)
    me.attribute.append(url)
    me.attribute.append(mail)

    general.poi.append(me)
    
dataset.dataset = general

f = open('POI_lisbon.json', 'w')
f.write(dataset.to_JSON())
