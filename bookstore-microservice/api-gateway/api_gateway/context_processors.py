def user_profile(request):
    """Inject user_customer_id into every template context."""
    customer_id = None
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            customer_id = request.user.profile.customer_id
        except Exception:
            pass
    is_admin = bool(getattr(request.user, "is_superuser", False))
    is_staff_role = False
    is_manager_role = False
    if request.user.is_authenticated:
        try:
            is_staff_role = request.user.groups.filter(name="staff").exists()
            is_manager_role = request.user.groups.filter(name="manager").exists()
        except Exception:
            pass

    return {
        'user_customer_id': customer_id,
        'is_admin': is_admin,
        'is_staff_role': is_staff_role,
        'is_manager_role': is_manager_role,
    }
