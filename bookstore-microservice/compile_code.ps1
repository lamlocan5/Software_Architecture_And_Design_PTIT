$root = 'c:\Users\Admin\Downloads\bookstore-microservice'
$out  = "$root\all_code.txt"
$sep  = '=' * 70

function Append-File([string]$path, [string]$label) {
    Add-Content -Path $out -Value ''
    Add-Content -Path $out -Value $sep
    Add-Content -Path $out -Value "FILE: $label"
    Add-Content -Path $out -Value $sep
    if (Test-Path $path) {
        Get-Content $path | Add-Content -Path $out
    } else {
        Add-Content -Path $out -Value '(file not found)'
    }
}

# Create/reset output file
Set-Content -Path $out -Value 'BOOKSTORE MICROSERVICE — FULL SOURCE CODE'
Add-Content -Path $out -Value "Generated: $(Get-Date)"
Add-Content -Path $out -Value $sep

# ── docker-compose
Append-File "$root\docker-compose.yml"                         'docker-compose.yml'

# ── API GATEWAY
Append-File "$root\api-gateway\Dockerfile"                     'api-gateway/Dockerfile'
Append-File "$root\api-gateway\requirements.txt"               'api-gateway/requirements.txt'
Append-File "$root\api-gateway\manage.py"                      'api-gateway/manage.py'
Append-File "$root\api-gateway\api_gateway\settings.py"        'api-gateway/api_gateway/settings.py'
Append-File "$root\api-gateway\api_gateway\urls.py"            'api-gateway/api_gateway/urls.py'
Append-File "$root\api-gateway\api_gateway\models.py"          'api-gateway/api_gateway/models.py'
Append-File "$root\api-gateway\api_gateway\views.py"           'api-gateway/api_gateway/views.py'
Append-File "$root\api-gateway\api_gateway\auth_views.py"      'api-gateway/api_gateway/auth_views.py'
Append-File "$root\api-gateway\api_gateway\context_processors.py" 'api-gateway/api_gateway/context_processors.py'
Append-File "$root\api-gateway\templates\base.html"            'api-gateway/templates/base.html'
Append-File "$root\api-gateway\templates\login.html"           'api-gateway/templates/login.html'
Append-File "$root\api-gateway\templates\register.html"        'api-gateway/templates/register.html'
Append-File "$root\api-gateway\templates\index.html"           'api-gateway/templates/index.html'
Append-File "$root\api-gateway\templates\user_home.html"       'api-gateway/templates/user_home.html'
Append-File "$root\api-gateway\templates\books.html"           'api-gateway/templates/books.html'
Append-File "$root\api-gateway\templates\customers.html"       'api-gateway/templates/customers.html'
Append-File "$root\api-gateway\templates\cart.html"            'api-gateway/templates/cart.html'
Append-File "$root\api-gateway\templates\orders.html"          'api-gateway/templates/orders.html'
Append-File "$root\api-gateway\templates\order_detail.html"    'api-gateway/templates/order_detail.html'
Append-File "$root\api-gateway\templates\reviews.html"         'api-gateway/templates/reviews.html'

# ── BOOK SERVICE
Append-File "$root\book-service\Dockerfile"                    'book-service/Dockerfile'
Append-File "$root\book-service\requirements.txt"              'book-service/requirements.txt'
Append-File "$root\book-service\book_service\settings.py"      'book-service/book_service/settings.py'
Append-File "$root\book-service\book_service\urls.py"          'book-service/book_service/urls.py'
Append-File "$root\book-service\app\models.py"                 'book-service/app/models.py'
Append-File "$root\book-service\app\serializers.py"            'book-service/app/serializers.py'
Append-File "$root\book-service\app\views.py"                  'book-service/app/views.py'

# ── CUSTOMER SERVICE
Append-File "$root\customer-service\Dockerfile"                'customer-service/Dockerfile'
Append-File "$root\customer-service\requirements.txt"          'customer-service/requirements.txt'
Append-File "$root\customer-service\customer_service\settings.py" 'customer-service/customer_service/settings.py'
Append-File "$root\customer-service\customer_service\urls.py"  'customer-service/customer_service/urls.py'
Append-File "$root\customer-service\app\models.py"             'customer-service/app/models.py'
Append-File "$root\customer-service\app\serializers.py"        'customer-service/app/serializers.py'
Append-File "$root\customer-service\app\views.py"              'customer-service/app/views.py'
Append-File "$root\customer-service\app\urls.py"               'customer-service/app/urls.py'

# ── CART SERVICE
Append-File "$root\cart-service\Dockerfile"                    'cart-service/Dockerfile'
Append-File "$root\cart-service\requirements.txt"              'cart-service/requirements.txt'
Append-File "$root\cart-service\cart_service\settings.py"      'cart-service/cart_service/settings.py'
Append-File "$root\cart-service\cart_service\urls.py"          'cart-service/cart_service/urls.py'
Append-File "$root\cart-service\app\models.py"                 'cart-service/app/models.py'
Append-File "$root\cart-service\app\serializers.py"            'cart-service/app/serializers.py'
Append-File "$root\cart-service\app\views.py"                  'cart-service/app/views.py'

# ── ORDER SERVICE
Append-File "$root\order-service\Dockerfile"                   'order-service/Dockerfile'
Append-File "$root\order-service\requirements.txt"             'order-service/requirements.txt'
Append-File "$root\order-service\order_service\settings.py"    'order-service/order_service/settings.py'
Append-File "$root\order-service\order_service\urls.py"        'order-service/order_service/urls.py'
Append-File "$root\order-service\app\models.py"                'order-service/app/models.py'
Append-File "$root\order-service\app\serializers.py"           'order-service/app/serializers.py'
Append-File "$root\order-service\app\views.py"                 'order-service/app/views.py'

# ── REVIEW SERVICE
Append-File "$root\review-service\Dockerfile"                  'review-service/Dockerfile'
Append-File "$root\review-service\requirements.txt"            'review-service/requirements.txt'
Append-File "$root\review-service\review_service\settings.py"  'review-service/review_service/settings.py'
Append-File "$root\review-service\review_service\urls.py"      'review-service/review_service/urls.py'
Append-File "$root\review-service\app\models.py"               'review-service/app/models.py'
Append-File "$root\review-service\app\serializers.py"          'review-service/app/serializers.py'
Append-File "$root\review-service\app\views.py"                'review-service/app/views.py'

$lines = (Get-Content $out).Count
Write-Host "Done! Total lines: $lines"
Write-Host "Output: $out"
