from django.shortcuts import render, redirect

from .forms import DocumentForm

def modelform_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('modelform_upload')
    else:
        form = DocumentForm()
    return render(request, 'translator/upload.html', {
        'form': form
    })
