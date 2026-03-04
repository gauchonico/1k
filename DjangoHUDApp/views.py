from multiprocessing import context
from DjangoHUDApp.forms import TransactionForm
from DjangoHUDApp.models import Profile, SavingGroup, Transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Sum, Q, Avg, Max, Count
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

def is_banker(user):
    return user.groups.filter(name='Banker').exists()

def index(request):
	return render(request, "pages/index.html")

def pageLogin(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "auth/login.html", context)

class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    
    def get_success_url(self):
        # Redirect to your all-transactions page upon successful login
        return reverse_lazy('DjangoHUDApp:transactions')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        # First, get the existing context (which includes the login form)
        context = super().get_context_data(**kwargs)
        
        # Add your custom UI context for the "Clean" login page
        context.update({
            "appSidebarHide": 1,
            "appHeaderHide": 1,
            "appContentClass": 'p-0',
            "pageTitle": "Login | The 1k Project" # Optional: add a page title
        })
        
        return context

class UserLogoutView(LogoutView):
    # After logout, send them back to the login page
    next_page = reverse_lazy('DjangoHUDApp:login')

    def dispatch(self, request, *args, **kwargs):
        # Optional: Add a success message that appears on the login page
        messages.info(request, "You have been logged out successfully. See you tomorrow for your next 1k!")
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            main_group = SavingGroup.objects.first()
			
            transaction.user = request.user  # Automatically link to logged-in founder
            transaction.group = main_group
            transaction.status = 'pending'   # Default status
            transaction.save()
            
            messages.success(request, "Transaction submitted! Wait for Banker verification. 🔥")
            return redirect('DjangoHUDApp:all-transactions')
    else:
        form = TransactionForm(initial={'amount': 1000}) # Default to 1k
        
    return render(request, 'transactions/add_transaction.html', {'form': form})
    
@login_required(login_url='DjangoHUDApp:login')
def transactions(request):
    is_banker = request.user.groups.filter(name='Banker').exists()
    
    if is_banker:
        transactions = Transaction.objects.all().select_related('user__profile').order_by('-created_at')
    else:
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        
    # 2. Search Logic (by Username or Transaction ID)
    query = request.GET.get('q')
    if query:
        transactions = transactions.filter(
            Q(user__username__icontains=query) | 
            Q(transaction_id__icontains=query)
        )
    # filter logic    
    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
        
        
    # 3. Calculation Logic
    if is_banker:
        # BANKER STATS: Global Pool and Group Consistency
        total_display_amount = Transaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        stats = Profile.objects.aggregate(
            avg_streak=Avg('current_streak'),
            max_streak=Max('current_streak'),
            active_savers=Count('id', filter=Q(current_streak__gt=0))
        )
        streak_display = {
            'main': f"{stats['active_savers']} Active",
            'sub': f"Avg: {stats['avg_streak']} | Best: {stats['max_streak']}"
        }
    else:
        # MEMBER STATS: Personal Savings and Personal Flame
        total_display_amount = transactions.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        current_streak = request.user.profile.current_streak
        streak_display = {
            'main': f"{current_streak} Days",
            'sub': "Don't break the chain! 🔥" if current_streak > 0 else "Save today to start!"
        }
        
    context = {
		'transactions':transactions,
		'is_banker':is_banker,
		'search_query': query,
		'total_amount':total_display_amount,
		'streak_display': streak_display
	}
    return render(request, "transactions/transactions.html", context)

def leaderboard(request):
    # We query the User model, but attach the sum of their 'completed' transactions
    # We use 'transaction__amount' because Transaction has a ForeignKey to User
    top_savers = User.objects.annotate(
        total_saved=Sum('transaction__amount', filter=Q(transaction__status='completed'))
    ).order_by('-total_saved')

    context = {
        'top_savers': top_savers,
        'page_title': 'Leaderboard | The 1k Project'
    }
    return render(request, 'transactions/leaderboard.html', context)
def analytics(request):
	return render(request, "pages/analytics.html")

def emailInbox(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-3"
	}
	return render(request, "pages/email-inbox.html", context)

def emailDetail(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-3"
	}
	return render(request, "pages/email-detail.html", context)

def emailCompose(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-3"
	}
	return render(request, "pages/email-compose.html", context)

def widgets(request):
	return render(request, "pages/widgets.html")

def posCustomerOrder(request):
	 
	return render(request, "pages/pos-customer-order.html", context)

def posKitchenOrder(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-kitchen-order.html", context)

def posCounterCheckout(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-counter-checkout.html", context)

def posTableBooking(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-table-booking.html", context)

def posMenuStock(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-menu-stock.html", context)

def uiBootstrap(request):
	return render(request, "pages/ui-bootstrap.html")

def uiButtons(request):
	return render(request, "pages/ui-buttons.html")

def uiCard(request):
	return render(request, "pages/ui-card.html")

def uiIcons(request):
	return render(request, "pages/ui-icons.html")

def uiModalNotifications(request):
	return render(request, "pages/ui-modal-notifications.html")

def uiTypography(request):
	return render(request, "pages/ui-typography.html")

def uiTabsAccordions(request):
	return render(request, "pages/ui-tabs-accordions.html")

def formElements(request):
	return render(request, "pages/form-elements.html")

def formPlugins(request):
	return render(request, "pages/form-plugins.html")

def formWizards(request):
	return render(request, "pages/form-wizards.html")

def tableElements(request):
	return render(request, "pages/table-elements.html")

def tablePlugins(request):
	return render(request, "pages/table-plugins.html")

def chartJs(request):
	return render(request, "pages/chart-js.html")

def chartApex(request):
	return render(request, "pages/chart-apex.html")

def map(request):
	return render(request, "pages/map.html")

def layoutStarter(request):
	return render(request, "pages/layout-starter.html")

def layoutFixedFooter(request):
	context = {
		"appFooter": 1
	}
	return render(request, "pages/layout-fixed-footer.html", context)

def layoutFullHeight(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-0"
	}
	return render(request, "pages/layout-full-height.html", context)

def layoutFullWidth(request):
	context = {
		"appContentFullWidth": 1,
		"appSidebarHide": 1
	}
	return render(request, "pages/layout-full-width.html", context)

def layoutBoxedLayout(request):
	context = {
		"appBoxedLayout": 1,
		"bodyClass": "pace-top"
	}
	return render(request, "pages/layout-boxed-layout.html", context)

def layoutCollapsedSidebar(request):
	context = {
		"appSidebarCollapsed": 1
	}
	return render(request, "pages/layout-collapsed-sidebar.html", context)

def layoutTopNav(request):
	context = {
		"appTopNav": 1,
		"appSidebarHide": 1
	}
	return render(request, "pages/layout-top-nav.html", context)

def layoutMixedNav(request):
	context = {
		"appTopNav": 1,
	}
	return render(request, "pages/layout-mixed-nav.html", context)

def layoutMixedNavBoxedLayout(request):
	context = {
		"appTopNav": 1,
		"appBoxedLayout": 1
	}
	return render(request, "pages/layout-mixed-nav-boxed-layout.html", context)

def pageScrumBoard(request):
	return render(request, "pages/page-scrum-board.html")

def pageProduct(request):
	return render(request, "pages/page-product.html")

def pageProductDetails(request):
	return render(request, "pages/page-product-details.html")

def pageOrder(request):
	return render(request, "pages/page-order.html")

def pageOrderDetails(request):
	return render(request, "pages/page-order-details.html")

def pageGallery(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'p-0',
		"appSidebarCollapsed": 1
	}
	return render(request, "pages/page-gallery.html", context)

def pageSearchResults(request):
	return render(request, "pages/page-search-results.html")

def pageComingSoon(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-coming-soon.html", context)

def pageError(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-error.html", context)



def pageRegister(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-register.html", context)

def pageMessenger(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'p-3'
	}
	return render(request, "pages/page-messenger.html", context)

def pageDataManagement(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'py-3'
	}
	return render(request, "pages/page-data-management.html", context)

def pageFileManager(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'd-flex flex-column'
	}
	return render(request, "pages/page-file-manager.html", context)

def pagePricing(request):
	return render(request, "pages/page-pricing.html")

def profile(request):
	return render(request, "pages/profile.html")

def calendar(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-0"
	}
	return render(request, "pages/calendar.html", context)

def settings(request):
	return render(request, "pages/settings.html")

def helper(request):
	return render(request, "pages/helper.html")
	
def error404(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-error.html", context)

def handler404(request, exception = None):
	return redirect('/404/')