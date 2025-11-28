import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_POST

from src.media.models import Media
from src.media.services.my_content.my_content_service import MyContentService
from src.media.services.update_my_content.update_my_content_service import UpdateMyContentService
from src.media.services.upload_media.upload_media_service import UploadMediaService
from src.media.services.views.views_service import ViewsService
from src.user.models import User


@require_GET
@login_required
def upload(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if user.is_regular_user():
        raise PermissionDenied

    is_creator = user.is_creator()
    if is_creator or is_creator == False:
        if not _can_access_upload(request):
            return redirect(reverse_lazy('age_verification.become_creator'))

    return render(
        request,
        'upload.html',
        {
            'upload_api': reverse_lazy('media.api.upload'),
            'my_content_url': reverse_lazy('media.my_content'),
            'user_suggestion_api': "reverse_lazy(user.api.user_search)"
        })


@require_POST
@login_required
def api_upload(request: HttpRequest) -> JsonResponse:
    user: User = request.user
    if user.is_regular_user():
        raise PermissionDenied

    is_creator = user.is_creator()
    if is_creator or is_creator == False:
        if not _can_access_upload(request):
            return JsonResponse({'error': 'Permission Denied'}, status=403)

    file = request.FILES.get('file')
    post = request.POST
    service = UploadMediaService()
    service.upload_media(
        user=request.user,
        uploaded_file=file,
        description=post.get('description'),
        post_type=post.get('postType')
    )

    return JsonResponse({})


@require_GET
@login_required
def my_content(request: HttpRequest) -> HttpResponse:
    get = request.GET
    page = int(get.get('page')) if get.get('page') else 1

    service = MyContentService()
    media = service.list_my_content(user=request.user, current_page=page)

    return render(
        request,
        'my_content.html', {
            'media_list': media,
            'user_suggestion_api': 'dummy link'  # "reverse_lazy('user.api.user_search')",
        })


@require_POST
@login_required
def update_my_media(request: HttpRequest) -> HttpResponse:
    post = request.POST
    delete = post.getlist('delete')
    ids = post.getlist('media_ids')
    descriptions = post.getlist('descriptions')

    service = UpdateMyContentService()
    service.update_my_content(
        user=request.user,
        delete_list=delete,
        ids=ids,
        descriptions=descriptions,
    )

    messages.success(request, 'Your content has been updated.')
    return redirect('media.my_content')


@require_POST
@login_required
def api_unlock(request: HttpRequest) -> JsonResponse:
    post = json.loads(request.body)
    try:
        service = UnlockService()
        result = service.unlock(user=request.user, media_id=int(post.get('media_id')))
    except BalanceTooLowException as e:
        return JsonResponse(
            {
                'error': f'Your balance is too low. <a href="{reverse_lazy('payment.list_packages')}" class="underline">Click here to buy more coins.</a>'
            },
            status=402
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=402)

    return JsonResponse(result)


@require_GET
def view_single_media(request: HttpRequest, id: int) -> HttpResponse:
    media = Media.objects.get(pk=id)
    return render(request, 'single_media.html', {'media': media})


# no need for login_required
@require_POST
def record_views(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body)
    service = ViewsService()
    service.record_view(user=request.user, media_id=int(body.get('media_id')))
    return JsonResponse({})


def _can_access_upload(request: HttpRequest) -> bool:
    return True
    service = CreatorService()
    age_verification = service.is_age_verification_completed(request.user)
    agreement = service.is_creator_agreement_completed(request.user)

    if not age_verification or not agreement:
        messages.warning(request, 'You have to sign creator agreement and verify your age')
        return False
    else:
        return True
