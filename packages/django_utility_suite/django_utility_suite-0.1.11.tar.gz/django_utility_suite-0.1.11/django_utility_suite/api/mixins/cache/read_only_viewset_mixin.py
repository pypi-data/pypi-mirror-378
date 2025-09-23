import base64
import xxhash
import re
import heapq

from django.conf import settings
from django.core.cache import cache
from django.db import close_old_connections, connections
from django.utils import translation
from django.utils.translation import get_language
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from typing import final

from django_utility_suite.api.mixins.utils import seconds_until


class PrivateCacheMethodsMixin:
    CACHE_SOURCE_HEADER = "X-Cache-Source"

    def _attach_cache_headers(self, response, source: str):
        if isinstance(response, Response):
            response[self.CACHE_SOURCE_HEADER] = source
        return response

    @final
    def _get_cache_key(self):
        # DON'T OVERRIDE. Customize key using get_cache_key method
        return f"{self.cache_prefix}:{self.get_cache_key()}:{self.cache_timeout}secs:{self.DEFAULT}"

    @final
    def _get_fallback_key(self):
        # DON'T OVERRIDE. Customize key using get_cache_fallback_key method
        return f"{self.cache_prefix}:{self.get_cache_fallback_key()}:{self.fallback_cache_timeout}secs:{self.FALLBACK}"

    @final
    def _get_deploy_cache_key(self):
        # DON'T OVERRIDE. Customize key using get_cache_key method
        return f"{self.cache_prefix}:{self.get_cache_key()}:{self.DEPLOY}"

    def _get_instance_response_and_set_cache(self, request, *args, **kwargs):
        lang = self.get_request_lang(request)
        with translation.override(lang):
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            response = Response(serializer.data)
            response = self._finalize_response(args, kwargs, request, response)
            self._set_cache(response, self.cache_timeout)
            return response

    def _get_list_response_and_set_cache(self, request, *args, **kwargs):
        lang = self.get_request_lang(request)
        with translation.override(lang):
            qs = self.get_queryset()
            queryset = self.filter_queryset(qs)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                response = Response(serializer.data)

            response = self._finalize_response(args, kwargs, request, response)
            self._set_cache(response, self.cache_timeout)
            return response

    def _finalize_response(self, args, kwargs, request, response):
        response = self.finalize_response(request, response, *args, **kwargs)
        if hasattr(response, "render") and callable(response.render):
            response.render()
        return response

    def _get_cache(self):
        use_deploy_cache = self.request.headers.get(
            settings.USE_DEPLOY_CACHE_HEADER, False
        )
        if bool(use_deploy_cache):
            key = self._get_deploy_cache_key()
            data = cache.get(key)
            data_source = self.DEPLOY
            if data is None:
                self.force_deploy_cache_update = True
            return data, data_source

        key = self._get_cache_key()

        data = cache.get(key)
        data_source = self.DEFAULT
        if data is None:
            data_source = self.FALLBACK
            fallback_key = self._get_fallback_key()
            data = cache.get(fallback_key)
        if data is None:
            data_source = self.DEPLOY
            deploy_key = self._get_deploy_cache_key()
            data = cache.get(deploy_key)
            if data is None:
                self.force_deploy_cache_update = True
        return data, data_source

    def _set_cache(self, data, timeout):
        fallback_timeout = self.fallback_cache_timeout
        deploy_timeout = self.deploy_cache_timeout
        if hasattr(data, "data"):
            if data.data is None or (
                    isinstance(data.data, (list, dict)) and not data.data
            ):
                # Short timeout for empty results due to performance database problems
                timeout = self.ONE_MINUTE
                fallback_timeout = self.ONE_MINUTE
                deploy_timeout = self.ONE_MINUTE

        if self.force_deploy_cache_update:
            deploy_key = self._get_deploy_cache_key()
            cache.set(deploy_key, data, deploy_timeout)
            if self.request.headers.get(settings.USE_DEPLOY_CACHE_HEADER, False):
                return

        key = self._get_cache_key()
        fallback_key = self._get_fallback_key()
        cache.set(key, data, timeout)
        cache.set(fallback_key, data, fallback_timeout)


class CacheReadOnlyViewSetMixin(PrivateCacheMethodsMixin, GenericAPIView):
    CACHE_KEY_PREFIX = settings.CACHE_MIXIN_PREFIX
    ONE_MINUTE = 60  # one minute in seconds
    DEFAULT_15_MINUTES = ONE_MINUTE * 15
    FALLBACK_30_MINUTES = ONE_MINUTE * 30

    DEFAULT = "default"
    FALLBACK = "fallback"
    DEPLOY = "deploy"

    force_deploy_cache_update = False

    DEFAULT_KEYS_LIST_BYTES_LENGTH = 32

    @property
    def cache_prefix(self):
        raise NotImplementedError("cache_prefix not defined")

    def get_cache_key(self):
        raise NotImplementedError("get_cache_key() is not implemented.")

    @property
    def cache_timeout(self):
        return self.DEFAULT_15_MINUTES

    @property
    def fallback_cache_timeout(self):
        return self.FALLBACK_30_MINUTES

    @property
    def deploy_cache_timeout(self):
        """
        By default, it will be invalidated at 20:00:00 PM.
        Deploy cache keys will be progressively updated as customers browse the frontend
        """
        return seconds_until(target_hour=20, target_minute=0, target_second=0)

    def get_cache_fallback_key(self):
        return self.get_cache_key()

    def get_request_lang(self, request, *args, **kwargs):
        lang = get_language()
        header_lang = self.request.headers.get("Accept-Language")
        if header_lang is None:
            lang = "es"
        return lang

    def retrieve(self, request, *args, **kwargs):
        cached_response, data_source = self._get_cache()
        if cached_response:
            self._attach_cache_headers(cached_response, data_source)
            if data_source in (self.FALLBACK, self.DEPLOY):
                self._get_instance_response_and_set_cache(request, *args, **kwargs)
            return cached_response

        response = self._get_instance_response_and_set_cache(request, *args, **kwargs)
        self._attach_cache_headers(response, "miss")
        return response

    def list(self, request, *args, **kwargs):
        cached_response, data_source = self._get_cache()
        if cached_response:
            self._attach_cache_headers(cached_response, data_source)
            if data_source in (self.FALLBACK, self.DEPLOY):
                self._get_list_response_and_set_cache(request, *args, **kwargs)
            return cached_response
        response = self._get_list_response_and_set_cache(request, *args, **kwargs)
        self._attach_cache_headers(response, "miss")
        return response

    def filter_cached_response_data(
            self,
            response,
            search_fields,
            search_query_param_name="search",
            limit_query_param_name="limit",
    ):
        """
        Filters a cached list response based on a search term and an optional limit.

        Args:
            response (Response): The original response from the list() method.
            search_fields (list[str]): Fields to apply the search on.
            search_query_param_name (str): Name of the search query parameter (default: "search").
            limit_query_param_name (str): Name of the limit query parameter (default: "limit").

        Returns:
            Response: Filtered and/or limited response.
        """

        filtered_data = response.data
        kword = (self.request.GET.get(search_query_param_name, "") or "").strip().lower()
        try:
            limit = int(self.request.GET.get(limit_query_param_name, 0))
        except (TypeError, ValueError):
            limit = 0

        if kword and search_fields:
            word_re = re.compile(rf"\b{re.escape(kword)}\b")

            def score_tuple(obj, idx):
                texts = [str(obj.get(f) or "").lower() for f in search_fields]
                total_hits = sum(t.count(kword) for t in texts)
                if total_hits == 0:
                    return None
                word_hits = sum(len(word_re.findall(t)) for t in texts)
                exact_eq = any(t == kword for t in texts)
                first_pos = min((t.find(kword) for t in texts if kword in t), default=10 ** 9)
                # less is better (in order to use nsmallest)
                return (-int(exact_eq), -word_hits, -total_hits, first_pos, idx)

            scored = ((score_tuple(obj, i), obj) for i, obj in enumerate(response.data))
            scored = ((st, obj) for st, obj in scored if st is not None)

            if limit and limit > 0:
                top = heapq.nsmallest(limit, scored, key=lambda x: x[0])
                filtered_data = [obj for _, obj in top]
            else:
                filtered_data = [obj for _, obj in sorted(scored, key=lambda x: x[0])]
        else:
            # Without search: apply only limit
            if limit and limit > 0:
                filtered_data = filtered_data[:limit]

        return Response(filtered_data)

    def create_key_from_list(self, param_list, length_bytes=DEFAULT_KEYS_LIST_BYTES_LENGTH, base64url=True,
                             prefix="hashed-key:"):
        """
        Use this method in order to optimize the cache key generation using query params or any data.
        :param param_list:
        :param length_bytes:
        :param base64url:
        :param prefix:
        :return:
        """

        h64s = []
        for s in param_list:
            if not s:
                continue
            h64s.append(xxhash.xxh3_64_intdigest(s.strip().lower()))
        h64s = sorted(set(h64s))
        final = xxhash.xxh3_128()
        for v in h64s:
            final.update(v.to_bytes(8, "little", signed=False))
        raw = bytes.fromhex(final.hexdigest())[:length_bytes]
        out = base64.urlsafe_b64encode(raw).rstrip(b"=").decode() if base64url else raw.hex()
        return f"{prefix}{out}"
