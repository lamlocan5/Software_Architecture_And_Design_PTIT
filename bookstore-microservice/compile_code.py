import os

root = r'c:\Users\Admin\Downloads\bookstore-microservice'
out  = os.path.join(root, 'all_code.txt')
sep  = '=' * 70

files = [
    ('docker-compose.yml',                                         'docker-compose.yml'),
    # API Gateway
    (r'api-gateway\Dockerfile',                                    'api-gateway/Dockerfile'),
    (r'api-gateway\requirements.txt',                              'api-gateway/requirements.txt'),
    (r'api-gateway\manage.py',                                     'api-gateway/manage.py'),
    (r'api-gateway\api_gateway\settings.py',                       'api-gateway/api_gateway/settings.py'),
    (r'api-gateway\api_gateway\urls.py',                           'api-gateway/api_gateway/urls.py'),
    (r'api-gateway\api_gateway\models.py',                         'api-gateway/api_gateway/models.py'),
    (r'api-gateway\api_gateway\views.py',                          'api-gateway/api_gateway/views.py'),
    (r'api-gateway\api_gateway\auth_views.py',                     'api-gateway/api_gateway/auth_views.py'),
    (r'api-gateway\api_gateway\context_processors.py',             'api-gateway/api_gateway/context_processors.py'),
    (r'api-gateway\templates\base.html',                           'api-gateway/templates/base.html'),
    (r'api-gateway\templates\login.html',                          'api-gateway/templates/login.html'),
    (r'api-gateway\templates\register.html',                       'api-gateway/templates/register.html'),
    (r'api-gateway\templates\index.html',                          'api-gateway/templates/index.html'),
    (r'api-gateway\templates\user_home.html',                      'api-gateway/templates/user_home.html'),
    (r'api-gateway\templates\books.html',                          'api-gateway/templates/books.html'),
    (r'api-gateway\templates\customers.html',                      'api-gateway/templates/customers.html'),
    (r'api-gateway\templates\cart.html',                           'api-gateway/templates/cart.html'),
    (r'api-gateway\templates\orders.html',                         'api-gateway/templates/orders.html'),
    (r'api-gateway\templates\order_detail.html',                   'api-gateway/templates/order_detail.html'),
    (r'api-gateway\templates\reviews.html',                        'api-gateway/templates/reviews.html'),
    # Book Service
    (r'book-service\Dockerfile',                                   'book-service/Dockerfile'),
    (r'book-service\requirements.txt',                             'book-service/requirements.txt'),
    (r'book-service\book_service\settings.py',                     'book-service/book_service/settings.py'),
    (r'book-service\book_service\urls.py',                         'book-service/book_service/urls.py'),
    (r'book-service\app\models.py',                                'book-service/app/models.py'),
    (r'book-service\app\serializers.py',                           'book-service/app/serializers.py'),
    (r'book-service\app\views.py',                                 'book-service/app/views.py'),
    # Customer Service
    (r'customer-service\Dockerfile',                               'customer-service/Dockerfile'),
    (r'customer-service\requirements.txt',                         'customer-service/requirements.txt'),
    (r'customer-service\customer_service\settings.py',             'customer-service/customer_service/settings.py'),
    (r'customer-service\customer_service\urls.py',                 'customer-service/customer_service/urls.py'),
    (r'customer-service\app\models.py',                            'customer-service/app/models.py'),
    (r'customer-service\app\serializers.py',                       'customer-service/app/serializers.py'),
    (r'customer-service\app\views.py',                             'customer-service/app/views.py'),
    (r'customer-service\app\urls.py',                              'customer-service/app/urls.py'),
    # Cart Service
    (r'cart-service\Dockerfile',                                   'cart-service/Dockerfile'),
    (r'cart-service\requirements.txt',                             'cart-service/requirements.txt'),
    (r'cart-service\cart_service\settings.py',                     'cart-service/cart_service/settings.py'),
    (r'cart-service\cart_service\urls.py',                         'cart-service/cart_service/urls.py'),
    (r'cart-service\app\models.py',                                'cart-service/app/models.py'),
    (r'cart-service\app\serializers.py',                           'cart-service/app/serializers.py'),
    (r'cart-service\app\views.py',                                 'cart-service/app/views.py'),
    # Order Service
    (r'order-service\Dockerfile',                                  'order-service/Dockerfile'),
    (r'order-service\requirements.txt',                            'order-service/requirements.txt'),
    (r'order-service\order_service\settings.py',                   'order-service/order_service/settings.py'),
    (r'order-service\order_service\urls.py',                       'order-service/order_service/urls.py'),
    (r'order-service\app\models.py',                               'order-service/app/models.py'),
    (r'order-service\app\serializers.py',                          'order-service/app/serializers.py'),
    (r'order-service\app\views.py',                                'order-service/app/views.py'),
    # Review Service
    (r'review-service\Dockerfile',                                 'review-service/Dockerfile'),
    (r'review-service\requirements.txt',                           'review-service/requirements.txt'),
    (r'review-service\review_service\settings.py',                 'review-service/review_service/settings.py'),
    (r'review-service\review_service\urls.py',                     'review-service/review_service/urls.py'),
    (r'review-service\app\models.py',                              'review-service/app/models.py'),
    (r'review-service\app\serializers.py',                         'review-service/app/serializers.py'),
    (r'review-service\app\views.py',                               'review-service/app/views.py'),
]

with open(out, 'w', encoding='utf-8') as f:
    f.write('BOOKSTORE MICROSERVICE — FULL SOURCE CODE\n')
    f.write(f'Total files: {len(files)}\n')
    f.write(sep + '\n')

    for rel, label in files:
        path = os.path.join(root, rel)
        f.write(f'\n{sep}\n')
        f.write(f'FILE: {label}\n')
        f.write(f'{sep}\n')
        if os.path.exists(path):
            try:
                content = open(path, encoding='utf-8', errors='replace').read()
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
            except Exception as e:
                f.write(f'(error reading file: {e})\n')
        else:
            f.write('(file not found)\n')

total_lines = sum(1 for _ in open(out, encoding='utf-8'))
print(f'Done! {len(files)} files compiled.')
print(f'Total lines: {total_lines}')
print(f'Output: {out}')
