from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import TruncDay
from django.shortcuts import render
from django.utils import timezone
from orders.models import Order, OrderItem
from paintings.models import Painting


@staff_member_required
def dashboard_home(request):
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)

    orders = Order.objects.all()
    completed_orders = orders.filter(payment_status='completed')

    total_revenue = completed_orders.aggregate(total=Sum('total'))['total'] or 0
    total_orders = orders.count()
    total_customers = get_user_model().objects.count()
    inventory_count = Painting.objects.filter(status='published').count()
    revenue_30_days = completed_orders.filter(created__gte=last_30_days).aggregate(total=Sum('total'))['total'] or 0
    orders_30_days = orders.filter(created__gte=last_30_days).count()
    recent_orders = orders.order_by('-created')[:10]

    low_stock_paintings = Painting.objects.filter(status='published', stock__lte=5).order_by('stock')[:10]

    top_selling = (
        OrderItem.objects.values('painting__title', 'painting__slug')
        .annotate(quantity_sold=Sum('quantity'), revenue=Sum(F('price') * F('quantity'), output_field=DecimalField()))
        .order_by('-quantity_sold')[:5]
    )

    status_counts = {choice[0]: 0 for choice in Order.ORDER_STATUS_CHOICES}
    for row in orders.values('status').annotate(count=Count('id')):
        status_counts[row['status']] = row['count']

    sales_by_day_qs = (
        completed_orders.filter(created__gte=last_7_days)
        .annotate(day=TruncDay('created'))
        .values('day')
        .annotate(total=Sum('total'))
        .order_by('day')
    )

    sales_by_day = {item['day'].date(): float(item['total'] or 0) for item in sales_by_day_qs}
    sales_labels = []
    sales_data = []
    for i in range(7, 0, -1):
        day = (now - timedelta(days=i)).date()
        sales_labels.append(day.strftime('%b %d'))
        sales_data.append(sales_by_day.get(day, 0))

    order_status_labels = [label for label, _ in Order.ORDER_STATUS_CHOICES]
    order_status_data = [status_counts[label] for label, _ in Order.ORDER_STATUS_CHOICES]

    return render(request, 'dashboard/home.html', {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'inventory_count': inventory_count,
        'revenue_30_days': revenue_30_days,
        'orders_30_days': orders_30_days,
        'recent_orders': recent_orders,
        'low_stock_paintings': low_stock_paintings,
        'top_selling': top_selling,
        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'order_status_labels': order_status_labels,
        'order_status_data': order_status_data,
    })
