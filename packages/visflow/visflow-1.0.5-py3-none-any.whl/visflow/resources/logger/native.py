from __future__ import annotations

import json
import logging
import logging.handlers
import os
import pathlib as p
import sys
import typing as t

from visflow.resources.logger import BaseLogger, LoggerBackend
from visflow.resources.logger.types import LoggingTarget, LogLevel
from visflow.utils import ansi

_LEVEL_MAP: t.Dict[LogLevel, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class ContextFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: (
            ansi.ANSIFormatter.FG.GRAY,
            ansi.ANSIFormatter.STYLE.DIM,
        ),
        logging.INFO: (ansi.ANSIFormatter.FG.BRIGHT_CYAN,),
        logging.WARNING: (
            ansi.ANSIFormatter.FG.BRIGHT_YELLOW,
            ansi.ANSIFormatter.STYLE.BOLD,
        ),
        logging.ERROR: (
            ansi.ANSIFormatter.FG.BRIGHT_RED,
            ansi.ANSIFormatter.STYLE.BOLD,
        ),
        logging.CRITICAL: (
            ansi.ANSIFormatter.FG.BRIGHT_RED,
            ansi.ANSIFormatter.BG.WHITE,
            ansi.ANSIFormatter.STYLE.BOLD,
        ),
    }

    COMPONENT_STYLES = {
        "timestamp": (ansi.ANSIFormatter.FG.GRAY,),
        "logger": (ansi.ANSIFormatter.FG.MAGENTA,),
        "tag": (ansi.ANSIFormatter.FG.CYAN, ansi.ANSIFormatter.STYLE.BOLD),
        "arrow": (ansi.ANSIFormatter.FG.GRAY,),
        "context": (ansi.ANSIFormatter.FG.GRAY,),
        # Same as arrow for consistency
    }

    def __init__(
        self,
        is_console: bool = False,
        use_colors: bool = True,
        verbose: bool | None = None,
    ):
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.is_console = is_console
        self.use_colors = use_colors

        if self.use_colors:
            ansi.ANSIFormatter.enable(True)
        if verbose is None:
            verbose = os.getenv("VF_VERBOSE", "0") not in ("0", "", "false", "off")
        self.verbose = verbose

    @staticmethod
    def _extract_context(record: logging.LogRecord, /) -> t.Dict[str, t.Any]:
        """Extract context from log record, excluding standard fields."""
        excluded = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "getMessage",
            "exc_info",
            "exc_text",
            "stack_info",
            "message",
        }

        context = {}
        for key, value in record.__dict__.items():
            if not key.startswith("_") and key not in excluded:
                try:
                    json.dumps(value)  # Test serializability
                    context[key] = value
                except (TypeError, ValueError):
                    context[key] = str(value)
        return context

    def _format_with_tag(self, name: str, context: t.Dict[str, t.Any]) -> str:
        """Format logger name with optional TAG."""
        tag = context.get("TAG")

        if tag:
            # Calculate available space: 20 total - 1 for dot = 39
            available_space = 19
            name_len = len(name)
            tag_len = len(tag)
            total_needed = name_len + tag_len

            if total_needed <= available_space:
                # Both fit, no truncation needed
                truncated_name = name
                truncated_tag = tag
            else:
                # Need to truncate
                if name_len <= 8:  # Keep short names intact
                    truncated_name = name
                    remaining = available_space - name_len
                    if tag_len > remaining:
                        truncated_tag = f"...{tag[-(remaining - 3):]}"
                    else:
                        truncated_tag = tag
                else:
                    # Truncate name, keep reasonable tag space
                    max_tag_space = min(tag_len, 8)  # At most 8 chars for tag
                    max_name_space = available_space - max_tag_space

                    if name_len > max_name_space:
                        truncated_name = f"...{name[-(max_name_space - 3):]}"
                    else:
                        truncated_name = name
                        max_tag_space = available_space - len(truncated_name)

                    if tag_len > max_tag_space:
                        truncated_tag = f"...{tag[-(max_tag_space - 3):]}"
                    else:
                        truncated_tag = tag

            full_display = f"{truncated_name}.{truncated_tag}"

            if self.use_colors:
                colored_name = ansi.ANSIFormatter.format(
                    truncated_name, *self.COMPONENT_STYLES["logger"]
                )
                colored_tag = ansi.ANSIFormatter.format(
                    truncated_tag, *self.COMPONENT_STYLES["tag"]
                )
                colored_dot = ansi.ANSIFormatter.format(".", ansi.ANSIFormatter.FG.GRAY)
                display = f"{colored_name}{colored_dot}{colored_tag}"
            else:
                display = full_display

            # Pad to 20 characters
            if len(full_display) < 20:
                display += " " * (20 - len(full_display))
            else:
                # Should not happen with our calculation, but just in case
                display = display[:20] if not self.use_colors else display
        else:
            # Without TAG: use full 20 characters
            if len(name) > 20:
                truncated_name = f"...{name[-17:]}"  # 20 - 3 = 17
            else:
                truncated_name = name

            display = f"{truncated_name:<20}"  # Left-align and pad to 20

            if self.use_colors:
                display = ansi.ANSIFormatter.format(
                    display, *self.COMPONENT_STYLES["logger"]
                )

        return display

    def _format_context(self, context: t.Dict[str, t.Any], prefix_len: int) -> str:
        """Format context for console output."""
        if not self.verbose:
            return ""

        # Remove TAG since it's in logger name
        ctx = {k: v for k, v in context.items() if k != "TAG"}
        if not ctx:
            return ""

        indent = " " * (prefix_len - 3)  # for "==> "
        arrow = "==>"
        if self.use_colors:
            arrow = ansi.ANSIFormatter.format(arrow, *self.COMPONENT_STYLES["context"])

        lines = []
        for k, v in ctx.items():
            line = f"{k}={v}"
            if self.use_colors:
                line = ansi.ANSIFormatter.format(
                    line, *self.COMPONENT_STYLES["context"]
                )
            lines.append(f"\n{indent}{arrow} {line}")

        return "".join(lines)

    @staticmethod
    def _get_prefix_length(timestamp: str, logger: str, loglevel: str) -> int:
        """Calculate prefix length for alignment."""
        return len(f"[{timestamp}] [{logger}] [{loglevel}] => ")

    def format(self, record: logging.LogRecord) -> str:
        context = self._extract_context(record)

        if self.is_console:
            return self._format_console(record, context)
        else:
            return self._format_json(record, context)

    def _format_console(
        self, record: logging.LogRecord, context: t.Dict[str, t.Any]
    ) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        logger_name = self._format_with_tag(record.name, context)
        level_name = f"{record.levelname:<8}"
        message = record.getMessage()

        # Apply colors
        if self.use_colors:
            timestamp = ansi.ANSIFormatter.format(
                timestamp, *self.COMPONENT_STYLES["timestamp"]
            )
            level_name = ansi.ANSIFormatter.format(
                level_name, *self.LEVEL_COLORS.get(record.levelno, ())
            )
            arrow = ansi.ANSIFormatter.format("=>", *self.COMPONENT_STYLES["arrow"])
        else:
            arrow = "=>"

        # Calculate alignment using plain text lengths
        plain_timestamp = self.formatTime(record, self.datefmt)
        plain_level = f"{record.levelname:<8}"
        prefix_len = self._get_prefix_length(
            plain_timestamp, "visflow" + 13 * " ", plain_level  # Max 20-char logger
        )  # Use consistent 20-char logger
        indent = " " * (prefix_len - 3)

        # Handle multiline messages
        if "\n" in message:
            lines = message.split("\n")
            message_lines = [lines[0]]
            for line in lines[1:]:
                message_lines.append(f"{indent}{arrow} {line}")
            message = "\n".join(message_lines)

        # Build log line
        log_line = f"[{timestamp}] [{logger_name}] [{level_name}] {arrow} " f"{message}"

        # Add context
        context_str = self._format_context(context, prefix_len)
        if context_str:
            log_line += context_str

        # Handle exceptions
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if not log_line.endswith("\n"):
                log_line += "\n"

            exc_lines = [line for line in record.exc_text.split("\n") if line.strip()]
            for line in exc_lines:
                colored_line = line
                if self.use_colors:
                    colored_line = ansi.ANSIFormatter.format(
                        line, ansi.ANSIFormatter.FG.RED, ansi.ANSIFormatter.STYLE.DIM
                    )
                log_line += f"{indent}{arrow} {colored_line}\n"

        return log_line.rstrip("\n")

    def _format_json(
        self, record: logging.LogRecord, context: t.Dict[str, t.Any]
    ) -> str:
        """Format for file output as JSON."""
        data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if context:
            data.update(context)

        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)

        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _create_handler(target: LoggingTarget) -> logging.Handler:
    handler: logging.Handler
    if target.logname in ("stdout", "stderr"):
        # Console handler
        stream = sys.stdout if target.logname == "stdout" else sys.stderr
        handler = logging.StreamHandler(stream)
        formatter = ContextFormatter(is_console=True, use_colors=True)
    else:
        # File handler
        file_path = p.Path(target.logname)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(filename=str(file_path), encoding="utf-8")
        formatter = ContextFormatter(is_console=False, use_colors=False)

    handler.setFormatter(formatter)
    handler.setLevel(_LEVEL_MAP.get(target.loglevel, logging.INFO))
    return handler


class NativeLoggingBackend(LoggerBackend):
    def __init__(self) -> None:
        self._logger = logging.getLogger("visflow")
        self._logger.setLevel(logging.DEBUG)
        self._handlers: t.List[logging.Handler] = []
        ansi.ANSIFormatter.enable(ansi.ANSIFormatter.supports_color())

    def setup_handlers(self, targets: t.List[LoggingTarget]) -> None:
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        self._handlers.clear()

        # Create new handlers
        for target in targets:
            handler = _create_handler(target)
            self._logger.addHandler(handler)
            self._handlers.append(handler)

        self._logger.propagate = False

    def log(self, msg: str, /, level: LogLevel, **context: t.Any) -> None:
        log_level = _LEVEL_MAP.get(level, logging.INFO)
        record = self._logger.makeRecord(
            name=self._logger.name,
            level=log_level,
            fn="",
            lno=0,
            msg=msg,
            args=(),
            exc_info=None,
        )

        # Add context to record
        for key, value in context.items():
            setattr(record, key, value)

        self._logger.handle(record)

    def sync(self) -> None:
        """Flush all handlers."""
        for handler in self._handlers:
            if hasattr(handler, "flush"):
                handler.flush()

    def close(self) -> None:
        """Close all handlers."""
        for handler in self._handlers:
            try:
                handler.close()
                self._logger.removeHandler(handler)
            except Exception:
                pass
        self._handlers.clear()


class NativeLogger(BaseLogger):
    def __init__(
        self,
        targets: t.Sequence[LoggingTarget] | None = None,
        initial_ctx: t.Dict[str, t.Any] | None = None,
    ):
        backend = NativeLoggingBackend()
        super().__init__(backend, targets, initial_ctx)

    @classmethod
    def enable_colors(cls, enabled: bool = True, /) -> None:
        ansi.ANSIFormatter.enable(enabled)

    @classmethod
    def supports_colors(cls) -> bool:
        return ansi.ANSIFormatter.supports_color()
