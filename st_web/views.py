import re
import os
from urllib.parse import unquote_plus

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
import magic

from st_web.forms import ShareLinkForm
from st_web.models import ShareLink


d = {"a": "a"}
img_re = re.compile(r"^image/.*$")


def file_view(request, id, path):
    resource_path = get_path(id, path)
    _, filename = os.path.split(resource_path)
    _, ext = os.path.splitext(filename)
    mime = magic.from_file(resource_path, mime=True)
    contents = None
    if img_re.match(mime):
        img = reverse("raw", args=[id, path])
        return render(
            request,
            "image.html",
            get_context(
                request.path,
                contents=contents,
                ext=ext,
                filename=filename,
                img=img,
                mime=mime,
            ),
        )
    if mime == "text/plain":
        with open(resource_path, "r") as f:
            contents = f.read()
    return render(
        request,
        "file.html",
        get_context(
            request.path, contents=contents, ext=ext, filename=filename, mime=mime
        ),
    )


def get_context(path="", **kwargs):
    nav = []
    current_path = ""
    root = ""
    for index, item in enumerate(path.split("/")[1:]):
        if len(item) == 0:
            continue
        if index <= 1:
            root += f"/{item}"
            current_path = root
        else:
            current_path += f"/{item}"
            nav.append({"label": item, "path": current_path})
    print(nav)
    return {**kwargs, "folders": settings.ST_CONFIG, "nav": nav, "root_folder": root}


def get_dir_contents(full, relative):
    contents = os.listdir(full)
    contents = list(filter(lambda x: x[0] != ".", contents))
    dirs = []
    files = []

    for child in contents:
        child_path = os.path.join(full, child)
        data = {
            "is_dir": False,
            "name": child,
            "path": os.path.join(relative, child),
        }
        if os.path.isdir(child_path):
            data["is_dir"] = True
            dirs.append(data)
        else:
            files.append(data)

    dirs.sort(key=lambda x: x["name"].lower())
    files.sort(key=lambda x: x["name"].lower())

    return [*dirs, *files]


def get_file_info(folder_id, child):
    resource_path = get_path(folder_id, child)
    _, filename = os.path.split(resource_path)

    type_ = None

    if os.path.isdir(resource_path):
        type_ = "dir"
    else:
        type_ = "file"

    return {"filename": filename, "full_path": resource_path, "type": type_}


def get_path(folder_id, child):
    current_folder = None
    for f in settings.ST_CONFIG:
        if f["id"] == folder_id:
            current_folder = f
            break

    if current_folder is None:
        raise Exception("Folder does not exist")

    return os.path.join(current_folder["path"], child)


def folder(request, id, path):
    current_folder = None
    for f in settings.ST_CONFIG:
        if f["id"] == id:
            current_folder = f
            break

    if current_folder is None:
        return HttpResponse("Invalid folder id", status=404)

    current_path = os.path.join(current_folder["path"], path)
    contents = []
    if os.path.isdir(current_path):
        contents = get_dir_contents(current_path, os.path.join(id, path))
    else:
        return file_view(request, id, path)

    return render(request, "base.html", get_context(request.path, children=contents))


def home(request):
    return render(request, "base.html", {"children": [], "folders": settings.ST_CONFIG})


def raw(request, id, path):
    try:
        resource_path = get_path(id, path)
    except:
        return HttpResponse("Invalid path", status=400)

    _, filename = os.path.split(path)
    _, ext = os.path.splitext(filename)
    mime = magic.from_file(resource_path, mime=True)

    f = open(resource_path, "rb")
    file_contents = f.read()
    f.close()

    return HttpResponse(file_contents, content_type=mime)


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, "login.html")

    def post(self, request):
        next = request.POST.get("next") or "/"
        password = request.POST.get("password")
        username = request.POST.get("username")
        user = authenticate(request, password=password, username=username)

        if user is not None:
            login(request, user)
            return redirect(next)

        return render(request, "login.html")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")


class ShareView(View):
    def get(self, request, id, path):
        info = get_file_info(id, path)
        links = ShareLink.objects.filter(resource_path=info["full_path"])
        links = [{"short_code": "arst"}, {"short_code": "arstne"}]
        return render(request, "share.html", {"links": links, **info})

    def post(self, request, id, path):
        form = ShareLinkForm(request.POST)
        if form.is_valid():
            expiration_date = form.cleaned_data["expiration_date"]
            visit_limit = form.cleaned_data["visit_limit"]
            print("form is valid", expiration_date, visit_limit)
        info = get_file_info(id, path)
        links = ShareLink.objects.filter(resource_path=info["full_path"])
        links = [{"short_code": "arst"}, {"short_code": "arstne"}]
        return render(request, "share.html", {"links": links, **info})
