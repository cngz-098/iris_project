from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
import io

# API için gerekli kütüphaneler 
from rest_framework import viewsets
from .serializers import IrisObservationSerializer

# Makine Öğrenmesi için gerekli kütüphaneler 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from .models import IrisObservation, Garden


def public_view(request):
    return render(request, 'iris_app/public.html')

def home_or_public(request):
    if request.user.is_authenticated:
        return render(request, 'iris_app/home.html')
    return render(request, 'iris_app/public.html')

# --- 1. KULLANICI İŞLEMLERİ --- 
def signin_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'iris_app/signin.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'iris_app/login.html', {'form': form})

@login_required
def home_view(request):
    # Roller arası farkı göstermek için 
    is_writer = request.user.groups.filter(name='Writer').exists()
    total_data = IrisObservation.objects.count()
    return render(request, 'iris_app/home.html', {
        'is_writer': is_writer,
        'total_data': total_data
    })

# --- 2. VERİ LİSTELEME VE ARAMA  ---
@login_required
def iris_list(request):
    items = IrisObservation.objects.all()
    
    # 3 farklı alana göre arama kriteri 
    species_query = request.GET.get('species')
    garden_query = request.GET.get('garden')
    min_sepal = request.GET.get('min_sepal')
    
    if species_query:
        items = items.filter(species__icontains=species_query)
    if garden_query:
        items = items.filter(garden__name__icontains=garden_query)
    if min_sepal:
        items = items.filter(sepal_length__gte=min_sepal)
        
    return render(request, 'iris_app/iris_list.html', {'items': items})

# --- 3. CRUD İŞLEMLERİ ---
@login_required
def iris_create(request):
    if request.method == "POST":
        IrisObservation.objects.create(
            garden_id=request.POST.get('garden'),
            sepal_length=request.POST.get('sepal_length'),
            sepal_width=request.POST.get('sepal_width'),
            petal_length=request.POST.get('petal_length'),
            petal_width=request.POST.get('petal_width'),
            species=request.POST.get('species')
        )
        return redirect('iris_list')
    
    gardens = Garden.objects.all()
    return render(request, 'iris_app/iris_form.html', {'gardens': gardens})

@login_required
def iris_update(request, pk):
    obj = get_object_or_404(IrisObservation, pk=pk)
    if request.method == "POST":
        obj.sepal_length = request.POST.get('sepal_length')
        obj.sepal_width = request.POST.get('sepal_width')
        obj.petal_length = request.POST.get('petal_length')
        obj.petal_width = request.POST.get('petal_width')
        obj.species = request.POST.get('species')
        obj.garden_id = request.POST.get('garden')
        obj.save()
        return redirect('iris_list')
    
    gardens = Garden.objects.all()
    return render(request, 'iris_app/iris_form.html', {'obj': obj, 'gardens': gardens})

@login_required
def iris_delete(request, pk):
    obj = get_object_or_404(IrisObservation, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect('iris_list')
    return render(request, 'iris_app/iris_confirm_delete.html', {'obj': obj})

# --- 4. CSV IMPORT/EXPORT --- 
@login_required
def export_iris_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="iris_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Species', 'SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Garden'])
    
    for obs in IrisObservation.objects.all():
        writer.writerow([obs.species, obs.sepal_length, obs.sepal_width, obs.petal_length, obs.petal_width, obs.garden.name])
    return response

@login_required
def import_iris_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Başlığı atla
        for row in csv.reader(io_string, delimiter=','):
            IrisObservation.objects.create(
                species=row[0], sepal_length=row[1], sepal_width=row[2],
                petal_length=row[3], petal_width=row[4], garden_id=1
            )
        return redirect('iris_list')
    return render(request, 'iris_app/import.html')

# --- 5. MAKİNE ÖĞRENMESİ --- 
@login_required
def predict_species(request):
    result = None
    accuracy = None
    selected_algo = request.POST.get('algorithm')
    
    if request.method == 'POST':
        try:
            sl = float(request.POST.get('sepal_length'))
            sw = float(request.POST.get('sepal_width'))
            pl = float(request.POST.get('petal_length'))
            pw = float(request.POST.get('petal_width'))
            
            # Eğitim verisi (UCI Iris Dataset örneği)
            X = [[5.1, 3.5, 1.4, 0.2], [4.9, 3.0, 1.4, 0.2], [7.0, 3.2, 4.7, 1.4], [6.4, 3.2, 4.5, 1.5], [6.3, 3.3, 6.0, 2.5], [5.8, 2.7, 5.1, 1.9]]
            y = ['Iris-setosa', 'Iris-setosa', 'Iris-versicolor', 'Iris-versicolor', 'Iris-virginica', 'Iris-virginica']
            
            # En az 3 farklı algoritma seçeneği
            if selected_algo == 'KNN':
                model = KNeighborsClassifier(n_neighbors=3)
            elif selected_algo == 'DecisionTree':
                model = DecisionTreeClassifier()
            else:
                model = LogisticRegression()
            
            model.fit(X, y)
            result = model.predict([[sl, sw, pl, pw]])[0]
            y_pred = model.predict(X)
            accuracy = accuracy_score(y, y_pred) * 100
        except:
            result = "Hata oluştu."

    return render(request, 'iris_app/predict.html', {'result': result, 'accuracy': accuracy, 'selected_algo': selected_algo})

# --- 6. REST API  --- 
class IrisObservationViewSet(viewsets.ModelViewSet):
    queryset = IrisObservation.objects.all()
    serializer_class = IrisObservationSerializer