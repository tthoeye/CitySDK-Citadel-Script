import urllib2
import cookielib
import json
import vobject

#CONFIGURATION
LANG = "pt-PT"
CITY = "Lisboa"
SITE = "http://tourism.citysdk.cm-lisboa.pt/pois/search?limit=-1"
OUTPUTFILE = "POI_lisboa.json"

LINKINFO = "http://tourism.citysdk.cm-lisboa.pt/resources"
UPDATEDDATE = "20121128T09:38:21-5:00"
CREATEDDATE = "20121128T09:38:21-5:00"
UPDATEFREQUENCY = "semester"
AUTHOR = "CitySDK"
LICENSE = "GNU GPL"
LICENSEURL = "http://www.gnu.org/licenses/gpl.html"


class Object:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False).encode('utf8')
 
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

req = urllib2.Request(SITE, headers=hdr)

try:
    page = urllib2.urlopen(req)
except urllib2.HTTPError, e:
    print e.fp.read()

content = page.read()
decoded_data = json.loads(content)

dataset = Object()
general = Object()
general.id = LINKINFO
general.updated = CREATEDDATE
general.created = UPDATEDDATE
general.lang = LANG
general.updatefrequency = UPDATEFREQUENCY

author = Object()
author.id = LINKINFO
author.value = AUTHOR
general.author = author

license = Object()
license.href = LICENSEURL
license.term = LICENSE
general.license = license

link = Object()
link.href = LINKINFO
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
                    if i['lang']  == j['lang']:
                        me.title = j['value']
            else:
                me.title = j['value']

    me.description = ""
    if 'description' in i:
        for j in i['description']:
           if 'lang' in j:
                if j['lang'] == LANG:
                    me.description = j['value']
                elif 'lang' in i:
                    if i['lang'] == j['lang']:
                        me.description = j['value']
           else:
                me.description = j['value']           

    me.category = []
    if 'category' in i:
        for j in i['category']:
            if 'lang' in j:
                if j['lang'] == LANG:
                    me.category.append(j['value'])
                elif 'lang' in i:
                    if i['lang']  == j['lang']:
                        me.category.append(j['value'])
            else:
                me.category.append(j['value'])

    me.location = Object()
    
    pos = Object()
    pos.srsName = "http://www.opengis.net/def/crs/EPSG/0/4326"
    pos.posList = ""
    
    address = Object()
   
    address.city = CITY

    telText = ""
    mailText = ""
    urlText = ""
    addressText = ""
    postalText = ""
    if 'location' in i:
        if 'point' in i['location']:
            for j in i['location']['point']:
                pos.posList = j['Point']['posList']
        if 'address' in i['location']:
            if 'type' in i['location']['address']:
                if i['location']['address']['type'] == "text/vcard":

                    try:
                        vobj=vobject.readOne( i['location']['address']['value'])
                        mylist = vobj.adr.value.split(";")
                        telText = vobj.tel.value
                        urlText = vobj.url.value
                        mailText = vobj.email.value
                        addressText = mylist[1]
                        postalText = mylist[5]
                    except: 
                        pass
        
    address.value = addressText
    address.postal = postalText        

    point = Object()
    point.term = "centroid"
    point.pos = pos
    
    me.location.point = point
    me.location.address = address
    
    tel = Object()
    tel.term = "telephone"
    tel.type = "tel"
    tel.text = telText
    tel.tplIdentifier = "#Citadel_telephone"
    
    mail = Object()
    mail.term = "email"
    mail.type = "mail"
    mail.text = mailText
    mail.tplIdentifier = "#Citadel_email"

    url = Object()
    url.term = "website"
    url.type = "url"
    url.text = urlText
    url.tplIdentifier = "Citadel_website"
 
    me.attribute = []
    me.attribute.append(tel)
    me.attribute.append(url)
    me.attribute.append(mail)

    general.poi.append(me)
    
dataset.dataset = general

f = open(OUTPUTFILE, "w")
f.write(dataset.to_JSON())
f.close()
