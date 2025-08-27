from __future__ import annotations

import asyncio
import atexit
import functools
import inspect
import logging
import os
import threading
import unittest
import weakref
from typing import Optional
from unittest.mock import patch

from botocore.response import StreamingBody
from moto import mock_aws

from .clients import ClientFactory

_default_logger = logging.getLogger("aws_testkit")
_default_logger.addHandler(logging.NullHandler())


class MotoTestKit:
    def __init__(
        self,
        region: Optional[str] = None,
        verbose: bool = False,
        logger: Optional[logging.Logger] = None,
        auto_start: bool = False,
        auto_stop_on_exit: bool = True,
        patch_aiobotocore: bool = True,
    ):
        os.environ.setdefault("AWS_DEFAULT_REGION", region or "us-east-1")
        os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
        os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

        self.region = os.environ["AWS_DEFAULT_REGION"]
        self._logger = logger or _default_logger
        if verbose and not logger:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("[aws_testkit] %(levelname)s - %(message)s")
            )
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)

        self._lock = threading.RLock()
        self._started = False
        self._moto_ctx = None
        self._patch_aiobotocore = patch_aiobotocore
        self._patchers = []

        self.clients = ClientFactory(self.region)

        if self._patch_aiobotocore:
            self._apply_aiobotocore_patches()

        if auto_stop_on_exit:
            weakref.finalize(self, self._finalize_on_gc)

        if auto_start:
            self.start()

    # ---------- ciclo de vida ----------
    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._moto_ctx = mock_aws()
            self._moto_ctx.start()
            self._started = True
            if self._patch_aiobotocore:
                self._apply_aiobotocore_patches()
            if self._patch_aiobotocore:
                atexit.register(self._atexit_stop)

    def stop(self) -> None:
        with self._lock:
            if not self._started:
                return
            if self._moto_ctx:
                self._moto_ctx.stop()
            self._moto_ctx = None
            try:
                asyncio.run(self.clients.close_async_clients())
            except RuntimeError:
                pass
            self._started = False
            self.clients._sync_clients.clear()

    def _finalize_on_gc(self) -> None:
        try:
            self.stop()
        except Exception:
            pass

    def _atexit_stop(self) -> None:
        try:
            asyncio.run(self.clients.close_async_clients())
        except Exception:
            pass
        self.stop()

    # ---------- acesso a clients ----------
    def get_client(self, service_name: str):
        self.ensure_started()
        return self.clients.get_client(service_name)

    async def get_async_client(self, service_name: str):
        self.ensure_started()
        return await self.clients.get_async_client(service_name)

    def ensure_started(self) -> None:
        if not self._started:
            self.start()

    async def close_async_clients(self) -> None:
        await self.clients.close_async_clients()

    def close_clients(self):
        self.clients.close_clients()

    # ---------- helpers tipados ----------
    def s3_helper(self):
        from .helpers import S3HelperTyped

        return S3HelperTyped(self.clients)

    def dynamo_helper(self):
        from .helpers import DynamoHelperTyped

        return DynamoHelperTyped(self.clients)

    def sqs_helper(self):
        from .helpers import SQSHelperTyped

        return SQSHelperTyped(self.clients)

    # ---------- patches ----------
    def _apply_aiobotocore_patches(self) -> None:
        self._patchers.append(self._patch_response_dict())
        self._patchers.append(self._patch_crc32_checker())

    @staticmethod
    def _patch_response_dict():
        async def _convert_to_response_dict_compat(http_response, operation_model):
            async def _await_or_value(obj):
                return await obj if inspect.isawaitable(obj) else obj

            headers = getattr(http_response, "headers", {}) or {}
            status = getattr(http_response, "status_code", 200)
            raw = getattr(http_response, "raw", b"")
            content = getattr(http_response, "content", b"")
            response_dict = {
                "headers": headers,
                "status_code": status,
                "context": {"operation_name": getattr(operation_model, "name", None)},
            }
            if status >= 300:
                response_dict["body"] = await _await_or_value(content)
            elif getattr(operation_model, "has_event_stream_output", False):
                response_dict["body"] = raw
            elif getattr(operation_model, "has_streaming_output", False):
                try:
                    length = int(headers.get("content-length", 0))
                except (TypeError, ValueError):
                    length = 0
                response_dict["body"] = StreamingBody(raw, length)
            else:
                response_dict["body"] = await _await_or_value(content)
            return response_dict

        patcher = patch(
            "aiobotocore.endpoint.convert_to_response_dict",
            _convert_to_response_dict_compat,
        )
        patcher.start()
        return patcher

    @staticmethod
    def _patch_crc32_checker():
        import binascii

        from aiobotocore.retryhandler import AioCRC32Checker

        original = AioCRC32Checker._check_response

        async def _check_response_compat(self, attempt_number, response):
            http_response = response[0]
            expected_crc = http_response.headers.get(self._header_name)
            if expected_crc is None:
                return await original(self, attempt_number, response)
            try:
                return await original(self, attempt_number, response)
            except TypeError:
                content = http_response.content
                data = await content if inspect.isawaitable(content) else content
                actual_crc32 = binascii.crc32(data) & 0xFFFFFFFF
                return actual_crc32 != int(expected_crc)

        patcher = patch(
            "aiobotocore.retryhandler.AioCRC32Checker._check_response",
            _check_response_compat,
        )
        patcher.start()
        return patcher


class AutoMotoTestKit(MotoTestKit):
    # --- Contexto síncrono ---
    def __enter__(self):
        self.ensure_started()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close_clients()
        except AttributeError:
            pass
        self.stop()

    # --- Contexto assíncrono ---
    async def __aenter__(self):
        self.ensure_started()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            # Se existir fechamento assíncrono, usa
            if hasattr(self, "close_async_clients"):
                await self.close_async_clients()
            else:
                # fallback para synchronous
                self.close_clients()
        except AttributeError:
            pass
        self.stop()


def use_moto_testkit(obj=None, *, auto_start=True, **kwargs):
    def _inject_into_self(args, mt):
        """Injeta no self quando rodando unittest.TestCase."""
        if args and isinstance(args[0], unittest.TestCase):
            setattr(args[0], "moto_testkit", mt)

    def _decorate_func(func):
        if getattr(func, "_is_moto_wrapped", False):
            return func  # evita decorar duas vezes

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **inner_kwargs):
                async with AutoMotoTestKit(auto_start=auto_start, **kwargs) as mt:
                    _inject_into_self(args, mt)
                    inner_kwargs.setdefault("moto_testkit", mt)
                    return await func(*args, **inner_kwargs)

        else:

            @functools.wraps(func)
            def wrapper(*args, **inner_kwargs):
                with AutoMotoTestKit(auto_start=auto_start, **kwargs) as mt:
                    _inject_into_self(args, mt)
                    inner_kwargs.setdefault("moto_testkit", mt)
                    return func(*args, **inner_kwargs)

        # Protege contra assinatura com *args/**kwargs
        sig = inspect.signature(func)
        if all(
            p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
            for p in sig.parameters.values()
        ):
            params = [p for p in sig.parameters.values() if p.name != "moto_testkit"]
            wrapper.__signature__ = inspect.Signature(
                parameters=params, return_annotation=sig.return_annotation
            )

        wrapper._is_moto_wrapped = True
        return wrapper

    def _decorate_class(cls):
        for name, attr in list(cls.__dict__.items()):
            if callable(attr) and (
                name.startswith("test_")
                or name in ("setUp", "tearDown", "setUpClass", "tearDownClass")
            ):
                setattr(cls, name, _decorate_func(attr))
        return cls

    if obj is None:
        return lambda real_obj: (
            _decorate_class(real_obj)
            if inspect.isclass(real_obj)
            else _decorate_func(real_obj)
        )
    return _decorate_class(obj) if inspect.isclass(obj) else _decorate_func(obj)
