import os
import re
import requests
import uuid
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from globalsnu.wiki.models import Page


########################
##### Univ Objects #####
########################

class BaseUnivObject(models.Model):
    """
    This model corresponds to special Page objects (e.g. country pages and
    school pages) and carries additional information. All pages linked with
    this model should be in Wiki #1 (the default wiki).
    """
    page = models.OneToOneField(Page, models.SET_NULL, blank=True, null=True)
    name_cached = models.CharField(max_length=100, blank=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        model_name = self._meta.model_name.capitalize()
        return self.name or "{} {}".format(model_name, self.id)

    @property
    def name(self):
        if self.page and self.page.title:
            return self.page.title
        else:
            return self.name_cached

    def get_absolute_url(self):
        if self.page:
            return self.page.get_absolute_url()
        else:
            return None

    def save(self, *args, **kwargs):
        if self.name:
            self.name_cached = self.name
        return super().save(*args, **kwargs)


class Country(BaseUnivObject):

    CONTINENTS = [
        ('AS', _('Asia')),
        ('AF', _('Africa')),
        ('NA', _('North America')),
        ('SA', _('South America')),
        ('EU', _('Europe')),
        ('AU', _('Australia')),
    ]
    continent = models.CharField(max_length=2, blank=True, choices=CONTINENTS)

    PATH = os.path.join(settings.STATIC_ROOT, "img", "flags")
    flag_path = models.FilePathField(path=PATH, blank=True)

    class Meta:
        verbose_name_plural = "countries"

    @classmethod
    def get_continents_with_countries(cls):
        continents = []
        for code, name in cls.CONTINENTS:
            continent = {
                'code': code,
                'name': name,
                'countries': Country.objects.filter(continent=code).order_by(
                    'page__current_revision__title').all(),
            }
            continents.append(continent)
        return continents

    def get_flag_path(self):
        relative_path = self.flag_path.replace(settings.STATIC_ROOT, "").replace("\\", "/")[1:]
        return settings.STATIC_URL + relative_path


class School(BaseUnivObject):

    country = models.ForeignKey(Country, models.SET_NULL,
        blank=True, null=True, related_name='schools')
    tags = models.ManyToManyField('Tag', related_name='schools')
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Like', related_name='liked_schools')
    raters = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Rating', related_name='rated_schools')

    schltype = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)

    def upload_directory_path(instance, filename):
        return "school/logo/{}.{}".format(uuid.uuid4(), filename.split(".")[-1])

    logo = models.ImageField(upload_to=upload_directory_path, blank=True)

    def get_short_url(self):
        if self.website.endswith("/"):
            url = self.website[:-1]
        else:
            url = self.website

        if self.website.startswith("http://"):
            return url[7:]
        elif self.website.startswith("https://"):
            return url[8:]
        else:
            return url

    def get_top_tags(self):
        return self.tags.all()[:3]

    def get_average_rating(self):
        avg = self.ratings.all().aggregate(models.Avg('rate'))['rate__avg']
        if avg:
            return round(avg)
        else:
            return 0

    def fetch_logo_url(self):
        query = self.name.replace(" ", "+")
        r = requests.get("https://en.wikipedia.org/w/index.php?search={}&go=Go".format(query))
        soup = BeautifulSoup(r.text, "lxml")
        if "/wiki/" not in r.url:
            try:
                href = soup.select_one("a[data-serp-pos=0]")['href']
                r = requests.get(href)
                soup = BeautifulSoup(r.text, "lxml")
            except:
                pass
        if "en.wikipedia.org" not in r.url:
            try:
                href = soup.select_one("a[lang=en]")['href']
                r = requests.get(href)
                soup = BeautifulSoup(r.text, "lxml")
            except:
                pass
        try:
            return "http://" + soup.select_one("table.infobox.vcard img")['src'].split("//")[1]
        except:
            return ""

    def initialize_logo(self):
        if not self.logo:
            url = self.fetch_logo_url()
            if url:
                r = requests.get(self.fetch_logo_url(), stream=True)
                f = NamedTemporaryFile()
                for chunk in r.iter_content(1024):
                    f.write(chunk)
                f.flush()
                filename = "{}.{}".format(self.id, r.url.rsplit(".")[-1])
                self.logo.save(filename, File(f))

    def initialize_address(self):
        if not self.address:
            query = "{}+{}".format(self.name.replace(" ", "+"), "address")
            r = requests.get("https://www.google.com/search?q={}&hl=en-US".format(query))
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, "lxml")
            try:
                identifier = soup.find("div", string=re.compile(", Address"))
                self.address = identifier.previous_sibling.string
                self.save()
            except Exception as e:
                print(e)

            self.address = self.update_coordinates()
            self.save()

    def update_coordinates(self):
        if self.address:
            query = self.address.replace(" ", "+")
            r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCppx7h6DkJBulA0JBjdxiM4A7ktJBsrtc".format(query))
            try:
                result = r.json()['results'][0]
                self.latitude = result['geometry']['location']['lat']
                self.longitude = result['geometry']['location']['lng']
                self.save()
                return result['formatted_address']
            except:
                pass
        return ""


########################
##### SNU in World #####
########################

class SNUInWorld(models.Model):

    city = models.CharField(max_length=30)
    page = models.ForeignKey(Page, models.SET_NULL, blank=True, null=True,
        related_name='+')
    redirect = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SNU in World"
        verbose_name_plural = "SNU in World"

    def __str__(self):
        return "SNU in {}".format(self.city.title())

    def get_absolute_url(self):
        return reverse("univ:snu_in_world_detail", args=[self.city])

    def save(self, *args, **kwargs):
        self.city = self.city.lower()
        return super().save(*args, **kwargs)


###############################
##### OIA Student Reports #####
###############################

class Report(models.Model):

    school = models.ForeignKey(School, models.CASCADE, related_name='reports')
    title = models.CharField(max_length=100)
    message_id = models.PositiveIntegerField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or "Report {}".format(self.id)

    def get_absolute_url(self):
        return "http://community.snu.ac.kr/bbs/bbs.enmessage.view.screen?bbs_id=511&message_id={}".format(self.message_id)


##########################
##### Tagging System #####
##########################

class Tag(models.Model):

    category = models.ForeignKey('self', models.SET_NULL,
        blank=True, null=True, related_name='child_tags')
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name or "Tag {}".format(self.id)

    def get_absolute_url(self):
        return reverse("univ:tag_detail", args=[self.id])


class TagLog(models.Model):

    school = models.ForeignKey(School, models.CASCADE, related_name='tag_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL,
        blank=True, null=True, related_name='tag_logs')
    time = models.DateTimeField(auto_now_add=True)

    tag = models.ForeignKey(Tag, models.SET_NULL, blank=True, null=True)
    name_cached = models.CharField(max_length=30, blank=True)
    is_addition = models.BooleanField()  # add: True, remove: False

    def save(self, *args, **kwargs):
        if self.tag:
            self.name_cached = self.tag.name
        return super().save(*args, **kwargs)


############################
##### User Interaction #####
############################

class Like(models.Model):

    school = models.ForeignKey(School, models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE,
        related_name='school_likes')
    time = models.DateTimeField(auto_now=True)


class Rating(models.Model):

    school = models.ForeignKey(School, models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL,
        blank=True, null=True, related_name='school_ratings')
    time = models.DateTimeField(auto_now=True)
    rate = models.PositiveSmallIntegerField()
