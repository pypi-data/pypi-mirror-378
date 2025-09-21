from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from aw.model.job import Job
from aw.model.job_credential import JobSharedCredentials
from aw.model.permission import JobPermission, JobPermissionMapping, JobPermissionMemberUser, \
    JobPermissionMemberGroup, JobCredentialsPermissionMapping, JobRepositoryPermissionMapping
from aw.api_endpoints.base import API_PERMISSION, GenericResponse, get_api_user, api_docs_put, api_docs_delete, \
    api_docs_post, validate_no_xss, API_PARAM_HASH, response_data_if_changed
from aw.utils.permission import has_manager_privileges
from aw.utils.util import is_set
from aw.base import USERS, GROUPS
from aw.model.repository import Repository
from aw.utils.audit import log_audit


class PermissionReadResponse(serializers.ModelSerializer):
    class Meta:
        model = JobPermission
        fields = JobPermission.api_fields_read

    permission_name = serializers.CharField(required=False)
    jobs = serializers.ListSerializer(child=serializers.IntegerField(), required=False)
    credentials = serializers.ListSerializer(child=serializers.IntegerField(), required=False)
    users_name = serializers.ListSerializer(child=serializers.CharField(), required=False)
    groups_name = serializers.ListSerializer(child=serializers.CharField(), required=False)
    jobs_name = serializers.ListSerializer(child=serializers.CharField(), required=False)
    credentials_name = serializers.ListSerializer(child=serializers.CharField(), required=False)
    repositories_name = serializers.ListSerializer(child=serializers.CharField(), required=False)


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job


class PermissionWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = JobPermission
        fields = JobPermission.api_fields_write

    jobs = serializers.MultipleChoiceField(allow_blank=True, allow_null=True, choices=[])
    credentials = serializers.MultipleChoiceField(allow_blank=True, allow_null=True, choices=[])
    repositories = serializers.MultipleChoiceField(allow_blank=True, allow_null=True, choices=[])
    users = serializers.MultipleChoiceField(allow_blank=True, allow_null=True, choices=[])
    groups = serializers.MultipleChoiceField(allow_blank=True, allow_null=True, choices=[])
    name = serializers.CharField(validators=[])  # uc on update

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jobs'] = serializers.MultipleChoiceField(choices=[job.id for job in Job.objects.all()])
        self.fields['credentials'] = serializers.MultipleChoiceField(
            choices=[creds.id for creds in JobSharedCredentials.objects.all()]
        )
        self.fields['repositories'] = serializers.MultipleChoiceField(
            choices=[repo.id for repo in Repository.objects.all()]
        )
        self.fields['users'] = serializers.MultipleChoiceField(choices=[user.id for user in USERS.objects.all()])
        self.fields['groups'] = serializers.MultipleChoiceField(choices=[group.id for group in GROUPS.objects.all()])

    def validate(self, attrs: dict):
        for field in JobPermission.api_fields_write:
            if field in attrs:
                validate_no_xss(value=attrs[field], field=field)

        return attrs

    @staticmethod
    def create_or_update(validated_data: dict, perm: JobPermission = None) -> JobPermission:
        # pylint: disable=R0912,R0915
        if 'permission' in validated_data:
            permission = validated_data['permission']
        else:
            permission = JobPermission.permission_default

        if perm is None:
            perm = JobPermission(
                name=validated_data['name'],
                permission=permission,
            )

        else:
            perm.name = validated_data['name']
            perm.permission = permission

        if 'jobs_all' in validated_data:
            perm.jobs_all = validated_data['jobs_all']

        if 'credentials_all' in validated_data:
            perm.credentials_all = validated_data['credentials_all']

        if 'repositories_all' in validated_data:
            perm.repositories_all = validated_data['repositories_all']

        perm.save()

        if 'jobs' in validated_data and is_set(validated_data['jobs']):
            jobs = []
            for job_id in validated_data['jobs']:
                try:
                    jobs.append(Job.objects.get(id=job_id))

                except ObjectDoesNotExist:
                    continue

            perm.jobs.set(jobs)

        if 'credentials' in validated_data and is_set(validated_data['credentials']):
            credentials = []
            for creds_id in validated_data['credentials']:
                try:
                    credentials.append(JobSharedCredentials.objects.get(id=creds_id))

                except ObjectDoesNotExist:
                    continue

            perm.credentials.set(credentials)

        if 'repositories' in validated_data and is_set(validated_data['repositories']):
            repositories = []
            for repo_id in validated_data['repositories']:
                try:
                    repositories.append(Repository.objects.get(id=repo_id))

                except ObjectDoesNotExist:
                    continue

            perm.repositories.set(repositories)

        if 'users' in validated_data and is_set(validated_data['users']):
            users = []
            for user_id in validated_data['users']:
                try:
                    users.append(USERS.objects.get(id=user_id))

                except ObjectDoesNotExist:
                    continue

            perm.users.set(users)

        if 'groups' in validated_data and is_set(validated_data['groups']):
            groups = []
            for group_id in validated_data['groups']:
                try:
                    groups.append(GROUPS.objects.get(id=group_id))

                except ObjectDoesNotExist:
                    continue

            perm.groups.set(groups)

        perm.save()
        return perm


def build_permissions(perm_id_filter: int = None) -> (list, dict):
    permissions_raw = JobPermission.objects.all()
    permission_jobs_id = {permission.id: [] for permission in permissions_raw}
    permission_jobs_name = {permission.id: [] for permission in permissions_raw}
    permission_credentials_id = {permission.id: [] for permission in permissions_raw}
    permission_credentials_name = {permission.id: [] for permission in permissions_raw}
    permission_repositories_id = {permission.id: [] for permission in permissions_raw}
    permission_repositories_name = {permission.id: [] for permission in permissions_raw}
    permission_users_id = {permission.id: [] for permission in permissions_raw}
    permission_users_name = {permission.id: [] for permission in permissions_raw}
    permission_groups_id = {permission.id: [] for permission in permissions_raw}
    permission_groups_name = {permission.id: [] for permission in permissions_raw}

    for mapping in JobPermissionMapping.objects.all():
        permission_jobs_id[mapping.permission.id].append(mapping.job.id)
        permission_jobs_name[mapping.permission.id].append(mapping.job.name)

    for mapping in JobCredentialsPermissionMapping.objects.all():
        permission_credentials_id[mapping.permission.id].append(mapping.credentials.id)
        permission_credentials_name[mapping.permission.id].append(mapping.credentials.name)

    for mapping in JobRepositoryPermissionMapping.objects.all():
        permission_repositories_id[mapping.permission.id].append(mapping.repository.id)
        permission_repositories_name[mapping.permission.id].append(mapping.repository.name)

    for mapping in JobPermissionMemberUser.objects.all():
        permission_users_id[mapping.permission.id].append(mapping.user.id)
        permission_users_name[mapping.permission.id].append(mapping.user.username)

    for mapping in JobPermissionMemberGroup.objects.all():
        permission_groups_id[mapping.permission.id].append(mapping.group.id)
        permission_groups_name[mapping.permission.id].append(mapping.group.name)

    permissions = []

    for permission in permissions_raw:
        if perm_id_filter is not None:
            if perm_id_filter != permission.id:
                continue

        permissions.append({
            'id': permission.id,
            'name': permission.name,
            'permission': permission.permission,
            'permission_name': permission.permission_name,
            'jobs': permission_jobs_id[permission.id],
            'jobs_name': permission_jobs_name[permission.id],
            'jobs_all': permission.jobs_all,
            'credentials': permission_credentials_id[permission.id],
            'credentials_name': permission_credentials_name[permission.id],
            'credentials_all': permission.credentials_all,
            'repositories': permission_repositories_id[permission.id],
            'repositories_name': permission_repositories_name[permission.id],
            'repositories_all': permission.repositories_all,
            'users': permission_users_id[permission.id],
            'users_name': permission_users_name[permission.id],
            'groups': permission_groups_id[permission.id],
            'groups_name': permission_groups_name[permission.id],
        })

    try:
        if perm_id_filter is not None:
            return permissions[0]

    except IndexError:
        return {}

    return permissions


def permission_in_use(permission: JobPermission) -> bool:
    in_use_jobs = JobPermissionMapping.objects.filter(permission=permission).exists()
    in_use_creds = JobCredentialsPermissionMapping.objects.filter(permission=permission).exists()
    return in_use_jobs or in_use_creds


class APIPermission(APIView):
    http_method_names = ['get', 'post']
    serializer_class = PermissionReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: PermissionReadResponse},
        summary='Return list of permissions',
        operation_id='permission_list',
        parameters=[API_PARAM_HASH],
    )
    def get(request):
        return response_data_if_changed(request, data=build_permissions())

    @extend_schema(
        request=PermissionWriteRequest,
        responses=api_docs_post('Permission'),
        summary='Create a new Permission.',
        operation_id='permission_create',
    )
    def post(self, request):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='permission')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage permissions'},
                status=403,
            )

        serializer = PermissionWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided permission data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            o = serializer.create_or_update(validated_data=serializer.validated_data, perm=None)
            log_audit(
                user=user,
                title='Permission create',
                msg=f"Permission created: ID '{o.id}', Name '{o.name}'",
            )
            return Response({
                'msg': f"Permission '{serializer.validated_data['name']}' created successfully",
                'id': o.id,
            }, status=200)

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided permission data is not valid: '{err}'"},
                status=400,
            )


class APIPermissionItem(APIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: PermissionReadResponse},
        summary='Return information of a permission.',
        operation_id='permission_get'
    )
    def get(request, perm_id: int):
        del request
        return Response(build_permissions(perm_id_filter=perm_id))

    @extend_schema(
        request=PermissionWriteRequest,
        responses=api_docs_put('Permission'),
        summary='Modify a permission.',
        operation_id='permission_edit',
    )
    def put(self, request, perm_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='permission')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage permissions'},
                status=403,
            )

        serializer = PermissionWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided permission data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            permission = JobPermission.objects.get(id=perm_id)

        except ObjectDoesNotExist:
            permission = None

        if permission is None:
            return Response(
                data={'error': f"Permission with ID {perm_id} does not exist"},
                status=404,
            )

        try:
            serializer.create_or_update(validated_data=serializer.validated_data, perm=permission)
            log_audit(
                user=user,
                title='Permission edit',
                msg=f"Permission edited: ID '{permission.id}', Name '{permission.name}'",
            )
            return Response(data={'msg': f"Permission '{permission.name}' updated", 'id': perm_id}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided permission data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Permission'),
        summary='Delete a permission.',
        operation_id='permission_delete'
    )
    def delete(self, request, perm_id: int):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='permission')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage permissions'},
                status=403,
            )

        try:
            permission = JobPermission.objects.get(id=perm_id)
            if permission is not None:
                if permission_in_use(permission):
                    return Response(
                        data={'error': f"Permission '{permission.name}' cannot be deleted as it is still in use"},
                        status=400,
                    )

                permission.delete()
                log_audit(
                    user=user,
                    title='Permission delete',
                    msg=f"Permission deleted: ID '{permission.id}', Name '{permission.name}'",
                )
                return Response(data={'msg': f"Permission '{permission.name}' deleted", 'id': perm_id}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Permission with ID {perm_id} does not exist"}, status=404)
