from ripozo import picky_processor

from utvsapi.magic import db, register, resources


@register
class Destination(db.Model):
    __tablename__ = 'v_destination'

    id = db.Column('id_destination', db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)


@register
class Hall(db.Model):
    __tablename__ = 'v_hall'

    id = db.Column('id_hall', db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)


@register
class Teacher(db.Model):
    __tablename__ = 'v_lectors'

    id = db.Column('id_lector', db.Integer, primary_key=True)
    degrees_before = db.Column('title_before', db.String)
    first_name = db.Column('name', db.String)
    last_name = db.Column('surname', db.String)
    degrees_after = db.Column('title_behind', db.String)
    personal_number = db.Column('pers_number', db.String)
    url = db.Column(db.String)


@register
class Sport(db.Model):
    __tablename__ = 'v_sports'

    id = db.Column('id_sport', db.Integer, primary_key=True)
    shortcut = db.Column('short', db.String)
    name = db.Column('sport', db.String)
    description = db.Column(db.String)


@register
class Enrollment(db.Model):
    __tablename__ = 'v_students'

    id = db.Column('id_student', db.Integer, primary_key=True)
    personal_number = db.Column(db.Integer)
    kos_course_code = db.Column('kos_kod', db.String)
    semester = db.Column(db.String)
    registration_date = db.Column(db.DateTime)
    tour = db.Column(db.Boolean)

    kos_code_flag = db.Column('kos_code', db.Boolean)

    fk_course = db.Column('utvs', db.Integer,
                          db.ForeignKey('v_subjects.id_subjects'))

    def _post_kos_code_null(cls, function_name, request, resource):
        '''This will me called as a function, so no self!'''
        if not resource.properties['kos_code_flag']:
            resource.properties['kos_course_code'] = None
        del resource.properties['kos_code_flag']

    __postprocessors__ = (picky_processor(_post_kos_code_null,
                                          include=['retrieve']),)


@register
class Course(db.Model):
    __tablename__ = 'v_subjects'

    id = db.Column('id_subjects', db.Integer,
                   primary_key=True)
    shortcut = db.Column(db.String)
    day = db.Column(db.Integer)
    starts_at = db.Column('begin', db.String)
    ends_at = db.Column('end', db.String)
    notice = db.Column(db.String)
    semester = db.Column(db.Integer)

    fk_sport = db.Column('sport', db.Integer,
                         db.ForeignKey('v_sports.id_sport'))
    fk_hall = db.Column('hall', db.Integer, db.ForeignKey('v_hall.id_hall'))
    fk_teacher = db.Column('lector', db.Integer,
                           db.ForeignKey('v_lectors.id_lector'))

    def _post_day_int(cls, function_name, request, resource):
        '''This will me called as a function, so no self!'''
        resource.properties['day'] = int(resource.properties['day'])

    __postprocessors__ = (picky_processor(_post_day_int,
                                          include=['retrieve']),)
