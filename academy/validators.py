from rest_framework import serializers
import re


class URLValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        pattern = re.compile(r'https?://(www\.)?youtube\.com')
        tmp_val = dict(value).get(self.field)

        if tmp_val and not bool(pattern.match(tmp_val)):
            raise serializers.ValidationError("URL should contain http://www.youtube.com")
