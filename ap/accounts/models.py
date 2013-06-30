from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from aputils.models import Vehicle, Address, EmergencyInfo
from terms.models import Term
from teams.models import Team
from houses.models import House, Bunk
from services.models import Service

""" accounts models.py
The user accounts module takes care of user accounts for the attendance+ and
utilizes/extends Django's auth system to handle user authentication.

There are several different kinds of users
    - Trainee: a regular (full-time) trainee at the FTTA
    - TrainingAssistant: a TA
    - ShortTermTrainee: a short-termer (that stays for longer than 2 weeks).
                        this is used to assign services to short-termers
    - HospitalityGuest: this is for those who take LSM hospitality during the
                        semiannual training. they will be assigned services

Each of these users is extended from UserAccount, which itself is extended from
django's AbstractUser.
"""


class UserAccount(AbstractUser):

    GENDER = (
        ('B', 'Brother'),
        ('S', 'Sister')
    )

    #optional middle name. First and last are in the abstract
    middleName = models.CharField(max_length=30, blank=True)

    nickname = models.CharField(max_length=30, blank=True)

    maidenName = models.CharField(max_length=30, blank=True)

    birthdate = models.DateField()

    gender = models.CharField(max_length=1, choices=GENDER)

    spouse = models.OneToOneField('self', null=True)

    # refers to the user's home address, not their training residence
    address = models.ForeignKey(Address)

    #return the age based on birthday
    def _get_age(self):
        today = date.today()
        birth = date.fromtimestamp(self.birthdate)
        try:
            birthday = birth.replace(year=today.year)
        except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
            birthday = birth.replace(year=today.year, day=birth.day-1)
        if birthday > today:
            return today.year - birth - 1
        else:
            return today.year - birth

    age = property(_get_age)

    maritalStatus = models.BooleanField()


class TrainingAssistant(UserAccount):

    user = models.ForeignKey(UserAccount)


class Trainee(UserAccount):

    TRAINEE_TYPES = (
        ('R', 'Regular (full-time)'),  # a regular full-time trainee
        ('S', 'Short-term (long-term)'),  # a 'short-term' long-term trainee
        ('C', 'Commuter')
    )

    user = models.ForeignKey(UserAccount)

    # many-to-many because a trainee can go through multiple terms
    term = models.ManyToManyField(Term)

    type = models.CharField(max_length=1, choices=TRAINEE_TYPES)

    emergencyInfo = models.OneToOneField(EmergencyInfo)

    dateBegin = models.DateField()

    dateEnd = models.DateField()

    degree = models.CharField(max_length=30)

    mentor = models.ForeignKey('self')

    vehicle = models.ForeignKey(Vehicle)

    team = models.ForeignKey(Team)

    services = models.ManyToManyField(Service)

    house = models.ForeignKey(House)

    TA = models.ForeignKey(TrainingAssistant)

    bunkNumber = models.ForeignKey(Bunk)

    #boolean for if the trainee is active in the training or not.
    active = models.BooleanField()

    #flag for trainees being self attended. This will be false for 1st years and true for 2nd with some exceptions.
    selfAttendance = models.BooleanField()


class ShortTermTrainee(UserAccount):

    user = models.ForeignKey(UserAccount)

    #date that they begin to be assigned to service
    serviceDate = models.DateField()

    #date that they leave the training. No service should be assigned after this point
    departureDate = models.DateField()


class HospitalityGuest(UserAccount):

    user = models.ForeignKey(UserAccount)

    #date that they leave the training. No service should be assigned after this point
    departureDate = models.DateField()