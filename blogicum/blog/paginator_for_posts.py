from django.core.paginator import Paginator

COUNT_FOR_PAGINATOR = 10


def paginator_for_posts(post_list, page_number):
    paginator = Paginator(post_list.order_by('-pub_date'), COUNT_FOR_PAGINATOR)
    return paginator.get_page(page_number)
