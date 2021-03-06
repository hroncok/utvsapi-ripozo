from ripozo import picky_processor, RequestContainer

from utvsapi import exceptions
from utvsapi.magic import db, register, resources, onemany


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
    personal_number = db.Column('pers_number', db.Integer)
    url = db.Column(db.String)

    @onemany
    def _post_pnum_int(cls, function_name, request, resource):
        '''This will be called as a function, so no self!'''
        resource.properties['personal_number'] = int(
            resource.properties['personal_number'])

    __postprocessors__ = (_post_pnum_int,)


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

    course_id = db.Column('utvs', db.Integer,
                          db.ForeignKey('v_subjects.id_subjects'))

    def _prepost_auth_logic(cls, message, request, resource=None):
        '''
        This is both pre- and postprocessor (cool, huh?).
        For retrieve_list, we need to filter this in the beginning.
        For retrieve we need to have the resource.

        It's the logic behind permissions.

        Only allows to see enrollment(s) for:

         * cvut:utvs:enrollments:all scope
         * cvut:utvs:enrollments:by-role scope for:
          * teachers
          * students (any non-teacher with personal number)

        If the retrieve_list request comes from a student,
        filter it immediately to boost performance.
        This will hide all the enrollments a student shouldn't see.

        If the retrieve request comes from a student,
        decide whether it belongs to that student.

        This will be called as a function, so no self!
        '''
        scope = request.client_info['scope']

        # can read anything
        if 'cvut:utvs:enrollments:all' in scope:
            return

        if 'cvut:utvs:enrollments:by-role' in scope:
            if 'B-00000-ZAMESTNANEC' in request.client_info['roles']:
                return

        if 'cvut:utvs:enrollments:personal' in scope:
            pnum = request.client_info['personal_number']
            if not pnum:
                raise exceptions.ForbiddenException(
                    'Permission denied. You have no personal_number and you '
                    'don\'t have cvut:utvs:enrollments:all or :by-role scope')

            if resource:
                # this is one resource
                # you are the student of this resource
                if pnum == resource.properties['personal_number']:
                    return
            else:
                # this is a list of resources
                # we'll filter all the enrollments by personal_number
                # (black magic prevents query_args from being updated,
                # so replace them instead)
                query_args = request.query_args.copy()
                try:
                    filter = query_args['personal_number'][0]
                    if int(filter) != pnum:
                        raise ValueError
                except (IndexError, KeyError):
                    pass
                except ValueError:
                    raise exceptions.ForbiddenException(
                        'Permission denied. '
                        'You cannot query on personal_number other than '
                        'your own.'
                    )
                query_args.update({'personal_number': [pnum]})
                request.query_args = query_args
                return

        # out of options
        if resource:
            message = 'You cannot see this enrollment.'
        else:
            message = 'You cannot see enrollments.'
        raise exceptions.ForbiddenException('Permission denied. ' + message)

    @onemany
    def _post_kos_code_null(cls, function_name, request, resource):
        '''This will be called as a function, so no self!'''
        if not resource.properties['kos_code_flag']:
            resource.properties['kos_course_code'] = None
        del resource.properties['kos_code_flag']

    __preprocessors__ = (picky_processor(_prepost_auth_logic,
                                         include=['retrieve_list']),)
    __postprocessors__ = (_post_kos_code_null,
                          picky_processor(_prepost_auth_logic,
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

    sport_id = db.Column('sport', db.Integer,
                         db.ForeignKey('v_sports.id_sport'))
    hall_id = db.Column('hall', db.Integer, db.ForeignKey('v_hall.id_hall'))
    teacher_id = db.Column('lector', db.Integer,
                           db.ForeignKey('v_lectors.id_lector'))

    @onemany
    def _post_day_int(cls, function_name, request, resource):
        '''This will be called as a function, so no self!'''
        resource.properties['day'] = int(resource.properties['day'])

    __postprocessors__ = (_post_day_int,)
