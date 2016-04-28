from ripozo import picky_processor, RequestContainer

from utvsapi import exceptions
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
    personal_number = db.Column('pers_number', db.Integer)
    url = db.Column(db.String)

    def _post_pnum_int(cls, function_name, request, resource):
        '''This will be called as a function, so no self!'''
        resource.properties['personal_number'] = int(
            resource.properties['personal_number'])

    __postprocessors__ = (picky_processor(_post_pnum_int,
                                          include=['retrieve']),)

    @classmethod
    def _is_teacher(cls, pnum):
        '''Checks if the personal number is a teacher'''
        request = RequestContainer(url_params={'personal_number': pnum})
        # We don't want to cycle trough auth again
        request.bypass_auth = True
        try:
            resources[cls.__name__].retrieve(request)
            return True
        except exceptions.NotFoundException:
            return False


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
        scopes = request.client_info['scopes']

        # can read anything
        if 'cvut:utvs:enrollments:all' in scopes:
            return

        # it's a person
        if 'cvut:utvs:enrollments:by-role' in scopes:
            pnum = request.client_info['personal_number']
            if not pnum:
                raise exceptions.ForbiddenException(
                    'Permission denied. You have no personal_number and you '
                    'don\'t have cvut:utvs:enrollments:all scope')

            if resource:
                # this is one resource
                # you are the student of this resource
                # this is a faster check than the teacher check,
                # so it comes first
                if pnum == resource.properties['personal_number']:
                    return

            if Teacher._is_teacher(pnum):
                # you are a teacher
                return

            if not resource:
                # this is a list of resources
                # you are a person, but not a teacher
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
                        'You cannot query on personal_number other then '
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

    def _post_kos_code_null(cls, function_name, request, resource):
        '''This will be called as a function, so no self!'''
        if not resource.properties['kos_code_flag']:
            resource.properties['kos_course_code'] = None
        del resource.properties['kos_code_flag']

    __preprocessors__ = (picky_processor(_prepost_auth_logic,
                                         include=['retrieve_list']),)
    __postprocessors__ = (picky_processor(_post_kos_code_null,
                                          include=['retrieve']),
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

    fk_sport = db.Column('sport', db.Integer,
                         db.ForeignKey('v_sports.id_sport'))
    fk_hall = db.Column('hall', db.Integer, db.ForeignKey('v_hall.id_hall'))
    fk_teacher = db.Column('lector', db.Integer,
                           db.ForeignKey('v_lectors.id_lector'))

    def _post_day_int(cls, function_name, request, resource):
        '''This will be called as a function, so no self!'''
        resource.properties['day'] = int(resource.properties['day'])

    __postprocessors__ = (picky_processor(_post_day_int,
                                          include=['retrieve']),)
