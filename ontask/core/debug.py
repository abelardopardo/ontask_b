"""
  Code to create a debug message with the file and line.

  Based on
  https://medium.com/@neeraj.online/python-show-file-name-and-line-number-when-calling-print-like-javascript-console-log-eb240d757f9a
  By Neeraj Gupta

"""
import inspect
from operator import truediv


class OnTaskDebug:
    last_trace_message = ''
    indent_str_default = '    '
    flag_force_location = False

    @classmethod
    def _location_msg(cls, active=True, offset=0, levels=1, end="\n") -> str:
        result = ''
        if not active:
            return result

        for level in range(levels):
            caller_frame_record = inspect.stack()[level + offset + 1]
            frame = caller_frame_record[0]
            info = inspect.getframeinfo(frame)
            file = info.filename
            result += '[{}:{} {}()]'.format(
                file,
                info.lineno,
                info.function) + end

        return result

    @classmethod
    def set_trace(cls, *args, **kwargs) -> str:
        cls.last_trace_message = result = ''
        if "active" in kwargs:
            active = kwargs.pop("active")
            if not active:
                return result

        if "location" in kwargs:
            location = kwargs.pop("location")
        else:
            location = True

        if "indent_str" in kwargs:
            indent_str = kwargs.pop("indent_str")
        else:
            indent_str = cls.indent_str_default

        prefix = ""
        if "indent" in kwargs:
            indent = kwargs.pop("indent")
            prefix = indent_str * indent

        line_start = ""
        if "new_line" in kwargs:
            flag_new_line = kwargs.pop("new_line")
            if flag_new_line:
                line_start = "\n"

        offset = 0
        if "offset" in kwargs:
            offset = kwargs.pop("offset")

        end = " "
        if "end" in kwargs:
            end = kwargs.pop("end")

        if location or cls.flag_force_location:
            result = cls._location_msg(offset=1 + offset, end=end)

        result = line_start + prefix + result
        if args:
            result += ' '.join(args)
        cls.last_trace_message = result

        return result
