from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.base import USERS
from aw.model.job import Job
from aw.api_endpoints.base import API_PERMISSION, GenericResponse, get_api_user, api_docs_put, api_docs_delete, \
    api_docs_post, validate_no_xss, GenericErrorResponse, response_data_if_changed, API_PARAM_HASH, BaseResponse
from aw.utils.permission import has_manager_privileges
from aw.model.alert import BaseAlert, AlertPlugin, AlertGlobal, AlertGroup, AlertUser
from aw.utils.audit import log_audit


def update_jobs(alert: BaseAlert, job_ids: list):
    jobs = []
    for job_id in job_ids:
        try:
            jobs.append(Job.objects.get(id=job_id))

        except ObjectDoesNotExist:
            continue

    alert.jobs.set(jobs)


class AlertPluginReadWrite(serializers.ModelSerializer):
    class Meta:
        model = AlertPlugin
        fields = AlertPlugin.api_fields


def _get_alert_plugins() -> list[AlertPlugin]:
    return [AlertPluginReadWrite(instance=plugin).data for plugin in AlertPlugin.objects.all()]


class APIAlertPlugin(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertPluginReadWrite
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertPluginReadWrite},
        summary='Return list of Alert-Plugins',
        operation_id='alert_plugin_list',
    )
    def get(request):
        del request
        return Response(_get_alert_plugins())

    @extend_schema(
        request=AlertPluginReadWrite,
        responses=api_docs_post('Alert-Plugin'),
        summary='Create a new Alert-Plugin.',
        operation_id='alert_plugin_create',
    )
    def post(self, request):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alert-Plugin'},
                status=403,
            )

        serializer = AlertPluginReadWrite(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert-Plugin data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            o = serializer.save()
            log_audit(
                user=user,
                title='Alert-Plugin create',
                msg=f"Alert-Plugin created: ID '{o.id}', Name '{o.name}'",
            )
            return Response({
                'msg': f"Alert-Plugin '{serializer.validated_data['name']}' created successfully",
                'id': o.id,
            }, status=200)

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided Alert-Plugin data is not valid: '{err}'"},
                status=400,
            )


class APIAlertPluginItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertPluginReadWrite,
            404: OpenApiResponse(response=GenericErrorResponse, description='Alert-Plugin does not exist'),
        },
        summary='Return information of an Alert-Plugin.',
        operation_id='alert_plugin_get'
    )
    def get(request, plugin_id: int):
        del request
        try:
            plugin = AlertPlugin.objects.get(id=plugin_id)
            if plugin is not None:
                return Response(AlertPluginReadWrite(instance=plugin).data)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Alert-Plugin with ID {plugin_id} does not exist"}, status=404)

    @extend_schema(
        request=AlertPluginReadWrite,
        responses=api_docs_put('Alert-Plugin'),
        summary='Modify an Alert-Plugin.',
        operation_id='alert_plugin_edit',
    )
    def put(self, request, plugin_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alert-Plugins'},
                status=403,
            )

        serializer = AlertPluginReadWrite(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert-Plugin data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            plugin = AlertPlugin.objects.get(id=plugin_id)

        except ObjectDoesNotExist:
            plugin = None

        if plugin is None:
            return Response(
                data={'error': f"Alert-Plugin with ID {plugin_id} does not exist"},
                status=404,
            )

        try:
            AlertPlugin.objects.filter(id=plugin.id).update(**serializer.validated_data)
            log_audit(
                user=user,
                title='Alert-Plugin edit',
                msg=f"Alert-Plugin edited: ID '{plugin.id}', Name '{plugin.name}'",
            )
            return Response(data={'msg': f"Alert-Plugin '{plugin.name}' updated", 'id': plugin_id}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided Alert-Plugin data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert-Plugin'),
        summary='Delete an Alert-Plugin.',
        operation_id='alert_plugin_delete'
    )
    def delete(self, request, plugin_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alert-Plugins'},
                status=403,
            )

        try:
            plugin = AlertPlugin.objects.get(id=plugin_id)
            if plugin is not None:
                plugin.delete()
                log_audit(
                    user=user,
                    title='Alert-Plugin delete',
                    msg=f"Alert-Plugin deleted: ID '{plugin.id}', Name '{plugin.name}'",
                )
                return Response(data={'msg': f"Alert-Plugin '{plugin.name}' deleted", 'id': plugin_id}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Alert-Plugin with ID {plugin_id} does not exist"}, status=404)


class BaseAlertWriteRequest(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jobs'] = serializers.MultipleChoiceField(choices=[job.id for job in Job.objects.all()])

    name = serializers.CharField(validators=[])  # uc on update
    jobs = serializers.MultipleChoiceField(allow_blank=True, allow_null=True, choices=[])


class AlertUserReadResponse(serializers.ModelSerializer):
    class Meta:
        model = AlertUser
        fields = AlertUser.api_fields_read

    alert_type_name = serializers.CharField()
    condition_name = serializers.CharField()


class AlertUserWriteRequest(BaseAlertWriteRequest):
    class Meta:
        model = AlertUser
        fields = AlertUser.api_fields_write

    def validate(self, attrs: dict):
        for field in AlertUser.api_fields_write:
            if field in attrs:
                validate_no_xss(value=attrs[field], field=field)

        return attrs


def _get_user_alerts(user: USERS) -> list[AlertUser]:
    return [AlertUserReadResponse(instance=alert).data for alert in AlertUser.objects.filter(user=user)]


class APIAlertUser(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertUserReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertUserReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_user_list',
    )
    def get(request):
        return Response(_get_user_alerts(get_api_user(request)))

    @extend_schema(
        request=AlertUserWriteRequest,
        responses=api_docs_post('Alert'),
        summary='Create a new Alert.',
        operation_id='alert_user_create',
    )
    def post(self, request):
        user = get_api_user(request)
        serializer = AlertUserWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            serializer.validated_data['user_id'] = user.id
            o = serializer.save()
            log_audit(
                user=user,
                title='Alert-User create',
                msg=f"Alert-User created: ID '{o.id}', Name '{o.name}'",
            )
            return Response(
                {'msg': f"Alert '{serializer.validated_data['name']}' created successfully", 'id': o.id},
                status=200,
            )

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided Alert data is not valid: '{err}'"},
                status=400,
            )


class APIAlertUserItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertUserReadResponse,
            404: OpenApiResponse(response=GenericErrorResponse, description='Alert does not exist'),
        },
        summary='Return information of an Alert.',
        operation_id='alert_user_get'
    )
    def get(request, alert_id: int):
        user = get_api_user(request)

        try:
            alert = AlertUser.objects.get(id=alert_id, user=user)
            if alert is not None:
                return Response(AlertUserReadResponse(instance=alert).data)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'error': f"Alert with ID {alert_id} does not exist or is belongs to another user"},
            status=404,
        )

    @extend_schema(
        request=AlertUserWriteRequest,
        responses=api_docs_put('Alert'),
        summary='Modify an Alert.',
        operation_id='alert_user_edit',
    )
    def put(self, request, alert_id: int):
        user = get_api_user(request)
        serializer = AlertUserWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            alert = AlertUser.objects.get(id=alert_id, user=user)

        except ObjectDoesNotExist:
            alert = None

        if alert is None:
            return Response(
                data={'error': f"Alert with ID {alert_id} does not exist or is belongs to another user"},
                status=404,
            )

        try:
            update_jobs(alert=alert, job_ids=serializer.validated_data.pop('jobs'))
            AlertUser.objects.filter(id=alert.id).update(
                **{**serializer.validated_data, 'user': user.id}
            )
            log_audit(
                user=user,
                title='Alert-User edit',
                msg=f"Alert-User edited: ID '{alert.id}', Name '{alert.name}'",
            )
            return Response(data={'msg': f"Alert '{alert.name}' updated", 'id': alert_id}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided Alert data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert'),
        summary='Delete an Alert.',
        operation_id='alert_user_delete'
    )
    def delete(self, request, alert_id: int):
        user = get_api_user(request)

        try:
            alert = AlertUser.objects.get(id=alert_id, user=user)
            if alert is not None:
                alert.delete()
                log_audit(
                    user=user,
                    title='Alert-User delete',
                    msg=f"Alert-User deleted: ID '{alert.id}', Name '{alert.name}'",
                )
                return Response(data={'msg': f"Alert '{alert.name}' deleted", 'id': alert_id}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'error': f"Alert with ID {alert_id} does not exist or is belongs to another user"},
            status=404,
        )


class AlertGlobalReadResponse(serializers.ModelSerializer):
    class Meta:
        model = AlertGlobal
        fields = AlertGlobal.api_fields_read

    alert_type_name = serializers.CharField()
    condition_name = serializers.CharField()


class AlertGlobalWriteRequest(BaseAlertWriteRequest):
    class Meta:
        model = AlertGlobal
        fields = AlertGlobal.api_fields_write

    def validate(self, attrs: dict):
        for field in AlertGlobal.api_fields_write:
            if field in attrs:
                validate_no_xss(value=attrs[field], field=field)

        return attrs


def _get_global_alerts() -> list[AlertGlobal]:
    return [AlertGlobalReadResponse(instance=alert).data for alert in AlertGlobal.objects.all()]


class APIAlertGlobal(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertGlobalReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertGlobalReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_global_list',
    )
    def get(request):
        del request
        return Response(_get_global_alerts())

    @extend_schema(
        request=AlertGlobalWriteRequest,
        responses=api_docs_post('Alert'),
        summary='Create a new Alert.',
        operation_id='alert_global_create',
    )
    def post(self, request):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alert'},
                status=403,
            )

        serializer = AlertGlobalWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            o = serializer.save()
            log_audit(
                user=user,
                title='Alert-Global create',
                msg=f"Alert-Global created: ID '{o.id}', Name '{o.name}'",
            )
            return Response(
                {'msg': f"Alert '{serializer.validated_data['name']}' created successfully", 'id': o.id},
                status=200,
            )

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided Alert data is not valid: '{err}'"},
                status=400,
            )


class APIAlertGlobalItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertGlobalReadResponse,
            404: OpenApiResponse(response=GenericErrorResponse, description='Alert does not exist'),
        },
        summary='Return information of an Alert.',
        operation_id='alert_global_get'
    )
    def get(request, alert_id: int):
        del request
        try:
            alert = AlertGlobal.objects.get(id=alert_id)
            if alert is not None:
                return Response(AlertGlobalReadResponse(instance=alert).data)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Alert with ID {alert_id} does not exist"}, status=404)

    @extend_schema(
        request=AlertGlobalWriteRequest,
        responses=api_docs_put('Alert'),
        summary='Modify an Alert.',
        operation_id='alert_global_edit',
    )
    def put(self, request, alert_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alerts'},
                status=403,
            )

        serializer = AlertGlobalWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            alert = AlertGlobal.objects.get(id=alert_id)

        except ObjectDoesNotExist:
            alert = None

        if alert is None:
            return Response(
                data={'error': f"Alert with ID {alert_id} does not exist"},
                status=404,
            )

        try:
            update_jobs(alert=alert, job_ids=serializer.validated_data.pop('jobs'))
            AlertGlobal.objects.filter(id=alert.id).update(**serializer.validated_data)
            log_audit(
                user=user,
                title='Alert-Global edit',
                msg=f"Alert-Global edited: ID '{alert.id}', Name '{alert.name}'",
            )
            return Response(data={'msg': f"Alert '{alert.name}' updated", 'id': alert_id}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided Alert data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert'),
        summary='Delete an Alert.',
        operation_id='alert_global_delete'
    )
    def delete(self, request, alert_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alerts'},
                status=403,
            )

        try:
            alert = AlertGlobal.objects.get(id=alert_id)
            if alert is not None:
                alert.delete()
                log_audit(
                    user=user,
                    title='Alert-Global delete',
                    msg=f"Alert-Global deleted: ID '{alert.id}', Name '{alert.name}'",
                )
                return Response(data={'error': f"Alert '{alert.name}' deleted", 'id': alert_id}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Alert with ID {alert_id} does not exist"}, status=404)


class AlertGroupReadResponse(serializers.ModelSerializer):
    class Meta:
        model = AlertGroup
        fields = AlertGroup.api_fields_read

    alert_type_name = serializers.CharField()
    condition_name = serializers.CharField()
    group_name = serializers.CharField()


class AlertGroupWriteRequest(BaseAlertWriteRequest):
    class Meta:
        model = AlertGroup
        fields = AlertGroup.api_fields_write

    def validate(self, attrs: dict):
        for field in AlertGroup.api_fields_write:
            if field in attrs:
                validate_no_xss(value=attrs[field], field=field)

        return attrs


def _get_group_alerts() -> list[AlertGroup]:
    return [AlertGroupReadResponse(instance=alert).data for alert in AlertGroup.objects.filter()]


class APIAlertGroup(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertGroupReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertGroupReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_group_list',
    )
    def get(request):
        del request
        return Response(_get_group_alerts())

    @extend_schema(
        request=AlertGroupWriteRequest,
        responses=api_docs_post('Alert'),
        summary='Create a new Alert.',
        operation_id='alert_group_create',
    )
    def post(self, request):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alerts'},
                status=403,
            )

        serializer = AlertGroupWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            o = serializer.save()
            log_audit(
                user=user,
                title='Alert-Group create',
                msg=f"Alert-Group created: ID '{o.id}', Name '{o.name}'",
            )
            return Response(
                {'msg': f"Alert '{serializer.validated_data['name']}' created successfully", 'id': o.id},
                status=200,
            )

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided Alert data is not valid: '{err}'"},
                status=400,
            )


class APIAlertGroupItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertGroupReadResponse,
            404: OpenApiResponse(response=GenericErrorResponse, description='Alert does not exist'),
        },
        summary='Return information of an Alert.',
        operation_id='alert_group_get'
    )
    def get(request, alert_id: int):
        del request

        try:
            alert = AlertGroup.objects.get(id=alert_id)
            if alert is not None:
                return Response(AlertGroupReadResponse(instance=alert).data)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'error': f"Alert with ID {alert_id} does not exist"},
            status=404,
        )

    @extend_schema(
        request=AlertGroupWriteRequest,
        responses=api_docs_put('Alert'),
        summary='Modify an Alert.',
        operation_id='alert_group_edit',
    )
    def put(self, request, alert_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alerts'},
                status=403,
            )

        serializer = AlertGroupWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            alert = AlertGroup.objects.get(id=alert_id)

        except ObjectDoesNotExist:
            alert = None

        if alert is None:
            return Response(
                data={'error': f"Alert with ID {alert_id} does not exist"},
                status=404,
            )

        try:
            update_jobs(alert=alert, job_ids=serializer.validated_data.pop('jobs'))
            AlertGroup.objects.filter(id=alert.id).update(**serializer.validated_data)
            log_audit(
                user=user,
                title='Alert-Group edit',
                msg=f"Alert-Group edited: ID '{alert.id}', Name '{alert.name}'",
            )
            return Response(data={'msg': f"Alert '{alert.name}' updated", 'id': alert_id}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided Alert data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert'),
        summary='Delete an Alert.',
        operation_id='alert_group_delete'
    )
    def delete(self, request, alert_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='alert')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage Alerts'},
                status=403,
            )

        try:
            alert = AlertGroup.objects.get(id=alert_id)
            if alert is not None:
                alert.delete()
                log_audit(
                    user=user,
                    title='Alert-Group delete',
                    msg=f"Alert-Group deleted: ID '{alert.id}', Name '{alert.name}'",
                )
                return Response(data={'msg': f"Alert '{alert.name}' deleted", 'id': alert_id}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'error': f"Alert with ID {alert_id} does not exist"},
            status=404,
        )


class AlertAllReadResponse(BaseResponse):
    glob = serializers.ListSerializer(child=serializers.DictField())  # todo: rename to 'global'
    group = serializers.ListSerializer(child=serializers.DictField())
    user = serializers.ListSerializer(child=serializers.DictField())
    plugins = serializers.ListSerializer(child=serializers.DictField())


class APIAlertAll(APIView):
    http_method_names = ['get']
    serializer_class = AlertAllReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertAllReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_list',
        parameters=[API_PARAM_HASH],
    )
    def get(request):
        return response_data_if_changed(
            request,
            data={
                'global': _get_global_alerts(),
                'group': _get_group_alerts(),
                'user': _get_user_alerts(get_api_user(request)),
                'plugins': _get_alert_plugins(),
            },
        )
