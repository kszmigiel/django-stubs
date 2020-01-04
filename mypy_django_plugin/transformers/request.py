from mypy.plugin import AttributeContext
from mypy.types import Instance
from mypy.types import Type as MypyType
from mypy.types import UnionType

from mypy_django_plugin.django.context import DjangoContext
from mypy_django_plugin.lib import chk_helpers, helpers


def set_auth_user_model_as_type_for_request_user(ctx: AttributeContext, django_context: DjangoContext) -> MypyType:
    # Imported here because django isn't properly loaded yet when module is loaded
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser

    abstract_base_user_info = helpers.lookup_class_typeinfo(helpers.get_typechecker_api(ctx), AbstractBaseUser)
    anonymous_user_info = helpers.lookup_class_typeinfo(helpers.get_typechecker_api(ctx), AnonymousUser)

    # This shouldn't be able to happen, as we managed to import the models above.
    assert abstract_base_user_info is not None
    assert anonymous_user_info is not None

    if ctx.default_attr_type != UnionType([Instance(abstract_base_user_info, []), Instance(anonymous_user_info, [])]):
        # Type has been changed from the default in django-stubs.
        # I.e. HttpRequest has been subclassed and user-type overridden, so let's leave it as is.
        return ctx.default_attr_type

    auth_user_model = django_context.settings.AUTH_USER_MODEL
    model_cls = django_context.apps_registry.get_model(auth_user_model)
    model_info = helpers.lookup_class_typeinfo(chk_helpers.get_typechecker_api(ctx), model_cls)
    if model_info is None:
        return ctx.default_attr_type

    return UnionType([Instance(user_info, []), Instance(anonymous_user_info, [])])
