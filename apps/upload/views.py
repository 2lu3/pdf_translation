from django.shortcuts import render, redirect

from .forms import PDFDocumentForm


def modelform_upload(request):
    if request.method == "POST":
        form = PDFDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("modelform_upload")
    else:
        form = PDFDocumentForm()
    return render(request, "translator/upload.html", {"form": form})
