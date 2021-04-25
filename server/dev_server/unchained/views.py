from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers

from .models import *

import django.http as http

import os
import subprocess
import signal
import secrets
import time
import json
import datetime
import re


def manage_user_login(request):
    req_body = json.loads(request.body)
    try:
        user_name = req_body['user_name']
    except KeyError:
        return http.HttpResponseBadRequest('\'user name\' needs a resolvable definition '
                                           + 'provided as request data component')

    try:
        password = req_body['password']
    except KeyError:
        return http.HttpResponseBadRequest('\'password\' needs a resolvable definition '
                                           + 'provided as request data component')

    '''
    if name is not None:
        username = name
        print('p2')
    else:
        print('p7')
        return http.HttpResponseBadRequest('User name is undefined')

    if 'password' in request.POST:
        password = request.POST['password']
    else:
        return http.HttpResponseBadRequest('Password is undefined')
    '''

    try:
        log_employee = Employee.objects.get(user_name=user_name)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('Missing user account')

    if not log_employee.password == password:
        return http.HttpResponseForbidden('Wrong password')
    else:
        user_token = secrets.token_urlsafe(32)
        log_employee.token = user_token
        log_employee.save()
        user_id = log_employee.id
        response = {'user_id': user_id, 'user_token': user_token}

        return http.JsonResponse(response, status=200)


def manage_user_logout(request):
    req_headers = request.headers
    try:
        user_token = req_headers['Authorization']
    except KeyError:
        return http.HttpResponseBadRequest('\'security token\' needs a resolvable definition '
                                           + 'provided as request header component')

    req_body = json.loads(request.body)
    try:
        user_id = req_body['user_id']
    except KeyError:
        return http.HttpResponseBadRequest('\'user id\' needs a resolvable definition '
                                           + 'provided as request data component')

    try:
        current_user = Employee.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('User ID is not valid.\nLogout error')

    if current_user.token != user_token:
        return http.HttpResponseForbidden('Attempted request from non-authorized user account\n'
                                          + 'Logout error')

    '''
    if name is not None:
        username = name
        print('p2')
    else:
        print('p7')
        return http.HttpResponseBadRequest('User name is undefined')

    if 'password' in request.POST:
        password = request.POST['password']
    else:
        return http.HttpResponseBadRequest('Password is undefined')
    '''
    current_user.token = ''
    current_user.save()

    return http.HttpResponse(status=200)


def init_session(request):
    req_headers = request.headers
    print('headers:', req_headers)

    try:
        user_token = req_headers['Authorization']
    except KeyError:
        return http.HttpResponseBadRequest('\'security token\' needs a resolvable definition '
                                           + 'provided as request header component')

    req_body = json.loads(request.body)
    try:
        user_id = req_body['user_id']
    except KeyError:
        return http.HttpResponseBadRequest('\'user ID\' needs a resolvable definition '
                                           + 'provided as request data component')

    try:
        host_ip = req_body['host_ip']
    except KeyError:
        return http.HttpResponseBadRequest('\'host ip address\' needs a resolvable definition '
                                           + 'provided as request data component')

    try:
        current_user = Employee.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('User ID is not valid.\nSession opening refused')

    if current_user.token != user_token:
        return http.HttpResponseForbidden('Attempted request from non-authorized user account\n'
                                          + 'Session opening refused')

    # try:
    new_session = RealTimeRecognitionControl.objects.get(host_ip_address=host_ip)
    # except ObjectDoesNotExist:
    # return http.HttpResponseNotFound('User ID is not valid.\nSession opening refused')

    monitor_file_name = new_session.monitor_file_name
    stasis_instance_name = new_session.stasis_instance_name
    websocket_connection_address = new_session.websocket_connection_address
    ws_connect_config = {'ws_address': websocket_connection_address}

    # try:
    # session_process = psutil.Process(session.stasis_pid)
    # process_status = session_process.status()

    launch_session(new_session,
                   current_user,
                   stasis_instance_name,
                   monitor_file_name,
                   websocket_connection_address)

    return http.JsonResponse(ws_connect_config, status=200)
    # else:
    # response = http.HttpResponseBadRequest('Speech recognition service is already on\n'
    #                                 + "No need enforcing restart unless the current session is over")
    '''
    except psutil.NoSuchProcess:
        print("id was assigned to process that does no longer exist\n."
              + "New process gets started to resolve an agent session control in actual job operation context")
        launch_session(session, current_user_id, stasis_instance_name, monitor_file_name)
        response = JsonResponse(ws_connection_address, status=200)
    '''


def launch_session(session, current_user, stasis_instance_name, monitor_file_name, websocket_connection_address):

    ws_connection_process = subprocess.Popen(['ws_connect.py',
                                              websocket_connection_address],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT)

    stasis_process = subprocess.Popen(['call-transcript-ari-server',
                                       stasis_instance_name,
                                       monitor_file_name,
                                       websocket_connection_address],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)

    session.websocket_pid = ws_connection_process.pid
    session.stasis_pid = stasis_process.pid
    session.current_user = current_user
    session.save()


def cancel_session(request):
    req_headers = request.headers
    try:
        user_token = req_headers['Authorization']
    except KeyError:
        return http.HttpResponseBadRequest('\'security token\' needs a resolvable definition '
                                           + 'provided as request header component')

    req_body = json.loads(request.body)

    '''
    try:
        user_id = req_body['user_id']
    except KeyError:
        return http.HttpResponseBadRequest('\'user ID\' needs a resolvable definition '
                                           + 'provided as request data component')
    '''

    try:
        host_ip = req_body['host_ip']
    except KeyError:
        return http.HttpResponseBadRequest('\'host ip address\' needs a resolvable definition '
                                           + 'provided as request data component')

    '''    
    try:
        current_user = Employee.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('User ID is not valid.\nSession opening refused')
    '''

    try:
        current_session = RealTimeRecognitionControl.objects.get(host_ip_address=host_ip)
        current_user = current_session.current_user
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('Host ip address is not valid.\nSession closing refused')

    if current_user.token != user_token:
        return http.HttpResponseForbidden('Attempted request from non-authorized user account\n'
                                          + 'Session closing refused')

    '''
    try:
        session = RealTimeRecognitionControl.objects.get(host_ip_address=host_ip)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('Host ip address is not valid.\nSession closing refused')

    print('p22')

    #host_ip = request.GET['host_ip']
    #session = None

    try:
        session = RealTimeRecognitionControl.objects.get(host_ip_address=host_ip)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('User host address is not valid.\nCancel attempt failed')
    '''

    stasis_pid = current_session.stasis_pid
    ws_pid = current_session.websocket_pid
    time.sleep(0.5)
    os.kill(ws_pid, signal.SIGTERM)
    time.sleep(0.5)
    os.kill(stasis_pid, signal.SIGTERM)
    time.sleep(0.5)
    os.kill(ws_pid, signal.SIGKILL)
    time.sleep(0.5)
    os.kill(stasis_pid, signal.SIGKILL)

    current_session.stasis_pid = 1
    current_session.websocket_pid = 1
    current_session.current_user = None
    current_session.save()

    return http.HttpResponse(status=200)


def prepare_readable_response(item):
    base_cat_code = item['base_category_code_id']
    base_cat_name = BaseCategory.objects.get(code=base_cat_code).name
    item['base_category'] = base_cat_name

    try:
        subcat_code = item['subcategory_code_id']
        subcat_name = Subcategory.objects.get(code=subcat_code).name
        item['subcategory'] = subcat_name
    except KeyError:
        pass

    str_datetime = re.split('[.+]', str(item['registered_on']))[0]
    dt_raw = datetime.datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')
    dt_standard = dt_raw.strftime('%d-%b-%Y %H:%M:%S')
    item['registered_on'] = dt_standard

    try:
        customer_type = item['caller_customer_type']
        if customer_type == 'IND':
            customer_type_result = '[B2C] Физическое лицо'
        elif customer_type == 'CORP <B2B>':
            customer_type_result = '[B2B] Корпоративный'
        else:
            customer_type_result = '[B2G] Корпоративный'
        item['caller_customer_type'] = customer_type_result
    except KeyError:
        pass

    try:
        business_unit = item['business_unit']
        if business_unit == 'Own retail store':
            business_unit_result = 'Ритейл-сеть оператора'
        elif business_unit == 'Partner retail store':
            business_unit_result = 'Ритейл-сеть партнёров'
        else:
            business_unit_result = 'Контактный центр оператора'

        item['business_unit'] = business_unit_result
    except KeyError:
        pass

    try:
        service_code = item['service_code_id']
        if service_code is not None:
            service_code_result = ServiceRange.objects.get(code=service_code)
            item['service_category'] = service_code_result.category
            item['service_name'] = service_code_result.name
    except KeyError:
        pass

    try:
        enabled_service_code = item['enabled_service_code_id']
        if enabled_service_code is not None:
            enabled_service_code_result = ServiceRange.objects.get(code=enabled_service_code)
            item['enabled_service_category'] = enabled_service_code_result.category.name
            item['enabled_service_name'] = enabled_service_code_result.name

        disabled_service_code = item['disabled_service_code_id']
        if disabled_service_code is not None:
            disabled_service_code_result = ServiceRange.objects.get(code=disabled_service_code)
            item['disabled_service_category'] = disabled_service_code_result.category.name
            item['disabled_service_name'] = disabled_service_code_result.name
    except KeyError:
        pass

    try:
        case_service_code = item['case_service_code_id']
        if case_service_code is not None:
            case_service_code_result = ServiceRange.objects.get(code=case_service_code)
            item['case_service_category'] = case_service_code_result.category.name
            item['case_service_name'] = case_service_code_result.name
    except KeyError:
        pass

    try:
        str_datetime = re.split('[.+]', str(item['start_timestamp']))[0]
        print('datetime: ', str_datetime)
        dt_raw = datetime.datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')
        dt_standard = dt_raw.strftime('%d-%b-%Y %H:%M:%S')
        item['start_timestamp'] = dt_standard
    except KeyError:
        pass

    try:
        str_datetime = re.split('[.+]', str(item['contact_time_period']))[0]
        print('datetime: ', str_datetime)
        dt_raw = datetime.datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')
        dt_standard = dt_raw.strftime('%d-%b-%Y %H:%M:%S')
        item['contact_time_period'] = dt_standard
    except KeyError:
        pass

    try:
        cancel_ground = item['cancel_ground']
        if cancel_ground == 'WRONG_UNKNOWN_BASIC_REQUISITES':
            cancel_ground_result = 'Не пройдена первичная идентификация (ФИО/паспортные данные)'
        else:
            cancel_ground_result = 'Не пройдена аутентификация по кодовому слову'
        item['cancel_ground'] = cancel_ground_result
    except KeyError:
        pass


def verify_request_origin(request, user_id):
    req_headers = request.headers

    try:
        user_token = req_headers['Authorization']
    except KeyError:
        return http.HttpResponseBadRequest('\'security token\' needs a resolvable definition '
                                           + 'provided as request header component')

    try:
        current_user = Employee.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound('User ID is not valid.\nRequest handling tried with error result')

    if current_user.token != user_token:
        return http.HttpResponseForbidden('Attempted request from non-authorized user account\n'
                                          + 'Request handling tried with error result')


def get_user_reports(request, user_id):
    common_auth_response = verify_request_origin(request, user_id)

    if common_auth_response is not None:
        return common_auth_response

    current_user = Employee.objects.get(id=user_id)
    subclass_reports = set(CallHandlingReport.__subclasses__())
    reports = list()

    for item in subclass_reports:
        model_reports = list(item.objects
                             .filter(employee=current_user)
                             .values('report_id', 'caller_phone', 'base_category_code_id',
                                     'subcategory_code_id', 'caller_contract_region', 'registered_on'))
        if len(model_reports) > 0:
            reports.append(model_reports)

    report_list = list()

    for cat_reports in reports:
        for elem in cat_reports:
            prepare_readable_response(elem)

            report_list.append(elem)

    response = sorted(report_list, key=lambda x: x['report_id'])

    return http.JsonResponse(response[:10], safe=False)


def get_report_details(request, report_id):
    user_id = request.GET['user_id']
    common_auth_response = verify_request_origin(request, user_id)

    if common_auth_response is not None:
        return common_auth_response

    subclass_reports = set(CallHandlingReport.__subclasses__())

    '''
    for item in subclass_reports:
        try:
            report = item.objects.get(report_id=report_id)
        except ObjectDoesNotExist:
            pass
    '''
    reports = list()

    for item in subclass_reports:
        try:
            reports = list(item.objects.filter(report_id=report_id).values())
            if len(reports) == 1:
                break
        except ObjectDoesNotExist:
            pass

    if len(reports) == 0:
        return http.HttpResponseNotFound('No report with matching ID was found.\n'
                                         + 'Request handling tried with error result')

    report_selected = reports[0]
    prepare_readable_response(report_selected)
    #print('select 1: ', report_selected)

    try:
        report_selected['service_category'] = report_selected['service_category'].name
    except KeyError:
        pass

    #print('select 2: ', report_selected)

    return http.JsonResponse(report_selected, safe=False)


def get_base_category_options(request):
    user_id = request.GET['user_id']
    common_auth_response = verify_request_origin(request, user_id)

    if common_auth_response is not None:
        return common_auth_response

    base_category_list = sorted(list(BaseCategory.objects.values()), key=lambda x: x['code'])

    return http.JsonResponse(base_category_list, safe=False)


def get_subcategory_options(request):
    user_id = request.GET['user_id']
    common_auth_response = verify_request_origin(request, user_id)

    if common_auth_response is not None:
        return common_auth_response

    subcategory_list = sorted(list(Subcategory.objects.values()), key=lambda x: x['code'])

    return http.JsonResponse(subcategory_list, safe=False)


def get_service_categories(request):
    user_id = request.GET['user_id']
    common_auth_response = verify_request_origin(request, user_id)

    if common_auth_response is not None:
        return common_auth_response

    service_categories = list(ServiceCategory.objects.values())

    return http.JsonResponse(service_categories, safe=False)

result = {}
loc = list()
cls = list()
trbl = list()
date = list()
time = list()

result['category'] = 'Техническая поддержка' # GUI адаптируется к категории услуг КЦ    
result['location'] = loc # B-LOC -> место фиксации неполадок
result['class'] = cls # B-CLS -> вид услуг связи
result['trbl'] = trbl # B-TRBL -> основной признак неполадок
result['date'] = date # B-DATE -> дата возникновения неполадок
result['time'] = time # B-TIME -> время возникновения неполадок
# result[...] = ...