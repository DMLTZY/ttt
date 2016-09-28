from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.contrib.auth.hashers import check_password
from .models import OfficeSupplies, Category, MyUser, Histroy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import RegistrationForm, LoginForm, ChangeProfileForm


class Registraion(CreateView):
    template_name = 'demo/register.html'
    form_class = RegistrationForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/')
        else:
            return super(Registraion, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        f = form.save()
        # print(type(f))
        login(self.request, f)
        # print('register and login')
        return redirect('/')


def _load_user_history(request, userid):
    """
    Fetch special user's data from History table to session
    :param request: http request
    :param userid: log in user's id
    :return:
    """
    history = Histroy.objects.filter(Q(user_id=userid) & Q(status=True))
    cartnum = 0
    session_list = []
    if history.exists():
        for i in history:
            # print(i.supply_id)
            # print(type(i.supply_id))
            session_list.append(str(i.supply_id))
            older = int(request.session.get(str(i.supply_id), 0))
            if older != 0:
                _modify_history(request.user, i.supply_id, i.count, older)
            request.session[str(i.supply_id)] = older + i.count
            cartnum += i.count
    for k, v in request.session.items():
        if _is_int(k) and k not in session_list:
            _modify_history(request.user, int(k), 0, request.session.get(k))
    request.session['cartnum'] = request.session.get('cartnum', 0) + cartnum


def login_view(request):
    lastpath = '/'  # request.path
    if request.user.is_authenticated():
        return redirect(lastpath)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username_or_mobile = request.POST.get('username_or_mobile')
        password = request.POST.get('password')
        user = authenticate(username=username_or_mobile, password=password)
        if user is not None:
            login(request, user)
            _load_user_history(request, user.id)
            return redirect('/all/')
        try:
            user = MyUser.objects.get(mobile=username_or_mobile)
        except MyUser.DoesNotExist:
            error_message = True
        else:
            if check_password(password, user.password):
                login(request, user)
                _load_user_history(request, user.id)
                return redirect('/all/')
            else:
                error_message = True
        return render(request, 'demo/login.html', {'form': form, 'error_message': error_message})

    else:
        form = LoginForm()
        return render(request, 'demo/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/all/')


def test(request):
    return render(request, 'demo/test.html')


@ensure_csrf_cookie
def home(request):
    return render(request, 'demo/notice.html')
    # return redirect('demo:index', slug='all')  # slug: index,binder,glue,notebook,writing-tool


def _is_login(request):
    if request.user.username == "":
        is_login = ''  # anomymous user
    else:
        is_login = request.user.username
    return is_login


@ensure_csrf_cookie
def index(request, slug):
    category_list = ['binder', 'glue', 'notebook', 'writing-tool']
    query = request.GET.get('q')

    # print(type(request.user))
    if slug not in category_list and query:
        qs = OfficeSupplies.objects.filter(name__icontains=query)
    elif slug not in category_list and not query:
        qs = OfficeSupplies.objects.all()
    elif slug in category_list and query:
        qs = OfficeSupplies.objects.filter(
            Q(category__slug=slug) & Q(name__icontains=query)).order_by('category')
    else:
        qs = OfficeSupplies.objects.filter(category__slug=slug).order_by('category')

    count = qs.count()
    qs_cat = Category.objects.all()
    paginator = Paginator(qs, 6)
    current_page = request.GET.get('page')
    try:
        supplies_list = paginator.page(current_page)
    except PageNotAnInteger:
        supplies_list = paginator.page(1)
    except EmptyPage:
        supplies_list = paginator.page(paginator.num_pages)
    context = {
        'supplies': supplies_list,
        'categries': qs_cat,
        'slug': slug,
        'query': query,
        'supplies_count': count,
        'cart_num': request.session.get('cartnum'),
        'is_login': _is_login(request),
    }
    return render(request, 'demo/index.html', context)


class Detail(DetailView):
    template_name = 'demo/detail.html'
    context_object_name = 'supply'
    model = OfficeSupplies

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['categries'] = Category.objects.all()
        context['cart_num'] = self.request.session.get('cartnum')
        context['is_login'] = _is_login(self.request)
        return context


def _modify_history(user, sid, num, mod_num):
    """
    Modify History table in database, this function can handle: create,update,delete
    :param user: means login user
    :param sid: means special supply
    :param num: means the older count of supply
    :param mod_num: means add or delete count of supply
    :return:
    """
    if num == 0:
        Histroy.objects.create(user_id=user.id, supply_id=sid, count=mod_num)
    elif num == -1:
        Histroy.objects.filter(Q(supply_id=sid) & Q(user_id=user.id)).delete()
    else:
        Histroy.objects.filter(Q(user_id=user.id) & Q(supply_id=sid) & Q(status=True)).update(count=(num+mod_num))


def add_to_cart(request):
    # print('addtocart')
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        addnum = int(data.get('num'))                       # get modified count
        num = int(request.session.get(data.get('sid'), 0))  # get older count
        cartnum = request.session.get('cartnum', 0) + addnum
        if _is_login(request) == '':  # anonymous user
            request.session.set_expiry(3600)  # this need to change to 3600
            request.session.clear_expired()
        else:
            _modify_history(request.user, int(data.get('sid')), num, addnum)
        request.session[data['sid']] = num + addnum
        request.session['cartnum'] = cartnum
        return HttpResponse(cartnum)
    else:
        return redirect('/all/')


def _is_int(s):
    """
    Varify a str to int is correct
    :param s: str
    :return: True or False
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def _product_cart_context(request):
    cart_dict = {int(k): int(v) for k, v in request.session.items() if _is_int(k)}
    supplies_list = OfficeSupplies.objects.filter(id__in=list(cart_dict))
    context = {'cart_supplies': []}
    if supplies_list:
        for queryset in supplies_list:
            context['cart_supplies'].append({queryset: cart_dict.get(queryset.id)})
    context['cart_num'] = request.session.get('cartnum')
    return context


def cart(request):
    context = _product_cart_context(request)
    context['is_login'] = _is_login(request)
    # print(context)
    return render(request, 'demo/basket.html', context)


def del_item(request):
    if request.method == 'POST':
        # print('del')
        data = json.loads(request.body.decode('utf-8'))
        sid = data.get('sid')
        origin_count = int(request.session[sid])
        if _is_login(request) != '':
            _modify_history(request.user, int(sid), -1, 0)
        request.session['cartnum'] -= origin_count
        del request.session[sid]
        return HttpResponse(request.session['cartnum'])
    else:
        return redirect('/cart/')


def chg_item(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        a, sid = data.get('sid').split('_')
        origin_count = request.session[sid]
        present_count = int(data.get('num'))
        if _is_login(request) != '':
            _modify_history(request.user, int(sid), origin_count, present_count-origin_count)
        # print(sid,origin_count,present_count)
        request.session[sid] = present_count
        request.session['cartnum'] = request.session['cartnum'] - origin_count + present_count
        return HttpResponse(request.session['cartnum'])
    else:
        return redirect('/cart/')


@login_required(login_url='/login/')
def apply(request):
    if request.method == 'POST':
        Histroy.objects.filter(user_id=request.user.id).update(status=False)
        del_list = []
        for k, v in request.session.items():
            if _is_int(k):
                del_list.append(k)
        for i in del_list:
            del request.session[i]
        # print(sid,origin_count,present_count)
        request.session['cartnum'] = 0
        context = _product_cart_context(request)
        context['is_login'] = _is_login(request)
        context['is_success'] = True
        return render(request, 'demo/basket.html', context)
    else:
        return redirect('/cart/')


@login_required(login_url='/login/')
def profile(request):
    if request.method == 'POST':
        form = ChangeProfileForm(request.POST, request=request)
        if form.is_valid():
            user = form.save()
            login(request, user)
            _load_user_history(request, user.id)
            return render(request, 'demo/profile.html', {'is_success': True,
                                                         'is_login': _is_login(request),
                                                         'cart_num': request.session.get('cartnum')})
        else:
            return render(request, 'demo/profile.html', {'form': form,
                                                         'is_login': _is_login(request),
                                                         'cart_num': request.session.get('cartnum')})
    else:
        form = ChangeProfileForm(initial={
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email}, request=request)
        # print(type(form))
        return render(request, 'demo/profile.html', {'form': form,
                                                     'is_login': _is_login(request),
                                                     'cart_num': request.session.get('cartnum')})


def about(request):
    return render(request, 'demo/about.html', {'is_login': _is_login(request),
                                                'cart_num': request.session.get('cartnum')})
