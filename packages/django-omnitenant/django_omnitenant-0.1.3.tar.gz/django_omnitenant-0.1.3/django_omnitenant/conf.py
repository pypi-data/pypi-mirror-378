from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from .constants import constants


class _WrappedSettings:
    def __getattr__(self, item):
        return getattr(django_settings, item)

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise ValueError("Item assignment is not supported")

        setattr(django_settings, key, value)

    @cached_property
    def OMNITENANT_CONFIG(self) -> dict:
        return getattr(django_settings, constants.OMNITENANT_CONFIG, {})

    @cached_property
    def SCHEMA_CONFIG(self) -> dict:
        return self.OMNITENANT_CONFIG.get(constants.SCHEMA_CONFIG, {})

    @cached_property
    def TENANT_RESOLVER(self) -> str:
        return self.OMNITENANT_CONFIG.get(
            constants.TENANT_RESOLVER,
            "django_omnitenant.resolvers.CustomDomainTenantResolver",
        )

    @cached_property
    def TIME_ZONE(self) -> str:
        return getattr(django_settings, "TIME_ZONE", "UTC")

    @cached_property
    def DEFAULT_TENANT_NAME(self) -> str:
        return self.SCHEMA_CONFIG.get(constants.DEFAULT_TENANT_NAME, "default")

    @cached_property
    def TENANT_MODEL(self) -> str:
        tenant = self.OMNITENANT_CONFIG.get(constants.TENANT_MODEL, "")
        if not tenant:
            raise ImproperlyConfigured(
                "OMNITENANT_CONFIG.TENANT_MODEL is not set. "
                "You must define TENANT_MODEL in your Omnitenant configuration."
            )
        return tenant

    @cached_property
    def DOMAIN_MODEL(self) -> str:
        domain_model: str = self.OMNITENANT_CONFIG.get(constants.DOMAIN_MODEL, "")
        if not domain_model:
            raise ImproperlyConfigured(
                "OMNITENANT_CONFIG.DOMAIN_MODEL is not set. "
                "You must define DOMAIN_MODEL in your Omnitenant configuration."
            )
        return domain_model

    @cached_property
    def DEFAULT_HOST(self) -> str:
        """
        Returns the default host for the tenant.
        This is used when no specific tenant is resolved.
        """
        return self.OMNITENANT_CONFIG.get(constants.DEFAULT_HOST, "localhost")


settings = _WrappedSettings()
