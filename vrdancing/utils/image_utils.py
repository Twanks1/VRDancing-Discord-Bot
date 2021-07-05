#!/usr/bin/env python
# coding: utf-8

# Copyright 2011 Álvaro Justen [alvarojusten at gmail dot com]
# License: GPL <http://www.gnu.org/copyleft/gpl.html>

from PIL import Image, ImageDraw, ImageFont

class ImageText(object):
    def __init__(self, filename_or_size, mode='RGBA', background=(0, 0, 0, 0),
                 encoding='utf8'):
        if isinstance(filename_or_size, str):
            self.filename = filename_or_size
            self.image = Image.open(self.filename)
            self.size = self.image.size
        elif isinstance(filename_or_size, (list, tuple)):
            self.size = filename_or_size
            self.image = Image.new(mode, self.size, color=background)
            self.filename = None
        self.draw = ImageDraw.Draw(self.image)
        self.encoding = encoding

    def alpha_composite(self, img: Image):
        self.image.alpha_composite(img)

    def saveToFile(self, filename=None):
        self.image.save(filename or self.filename)

    def save(self, arr, format):
        self.image.save(arr, format)

    def show(self):
        self.image.show()

    def get_font_size(self, text, font, max_width=None, max_height=None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = self.get_text_size(font, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or \
           (max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" % \
                    text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or \
               (max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(self, x, y, text, font_filename, font_size=11,
                   color=(0, 0, 0), max_width=None, max_height=None, anchor="la", embedded_color=False):
        if font_size == 'fill' and \
           (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_filename, max_width,
                                           max_height)
        text_size = self.get_text_size(font_filename, font_size, text)
        font = ImageFont.truetype(font_filename, font_size)
        if x == 'center':
            x = (self.size[0] - text_size[0]) / 2
        if y == 'center':
            y = (self.size[1] - text_size[1]) / 2
        self.draw.text((x, y), text, font=font, fill=color, anchor=anchor, embedded_color=embedded_color)
        return text_size

    def get_text_size(self, font_filename, font_size, text):
        font = ImageFont.truetype(font_filename, font_size)
        return font.getsize(text)

    def write_text_box(self, x, y, text, box_width, font_filename,
                       font_size=11, color=(0, 0, 0), place='left',
                       justify_last_line=False, anchor="la", embedded_color=False):
        lines = []
        line = []
        words = text.split()
        for word in words:
            new_line = ' '.join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            text_height = size[1]
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        lines = [' '.join(line) for line in lines if line]

        height = y
        for index, line in enumerate(lines):
            if place == 'left':
                self.write_text(x, height, line, font_filename, font_size,
                                color, anchor=anchor, embedded_color=embedded_color)
            elif place == 'right':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = x + box_width - total_size[0]
                self.write_text(x_left, height, line, font_filename,
                                font_size, color, anchor=anchor, embedded_color=embedded_color)
            elif place == 'center':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = int(x + ((box_width - total_size[0]) / 2))
                self.write_text(x_left, height, line, font_filename,
                                font_size, color, anchor=anchor, embedded_color=embedded_color)
            elif place == 'justify':
                words = line.split()
                if (index == len(lines) - 1 and not justify_last_line) or \
                   len(words) == 1:
                    self.write_text(x, height, line, font_filename, font_size,
                                    color, anchor=anchor, embedded_color=embedded_color)
                    continue
                line_without_spaces = ''.join(words)
                total_size = self.get_text_size(font_filename, font_size,
                                                line_without_spaces)
                space_width = (box_width - total_size[0]) / (len(words) - 1.0)
                start_x = x
                for word in words[:-1]:
                    self.write_text(start_x, height, word, font_filename,
                                    font_size, color, anchor=anchor, embedded_color=embedded_color)
                    word_size = self.get_text_size(font_filename, font_size,
                                                    word)
                    start_x += word_size[0] + space_width
                last_word_size = self.get_text_size(font_filename, font_size,
                                                    words[-1])
                last_word_x = x + box_width - last_word_size[0]
                self.write_text(last_word_x, height, words[-1], font_filename,
                                font_size, color, anchor=anchor, embedded_color=embedded_color)
                                
            height += text_height
        return (box_width, height - y)

    def write_text_box_fit(self, x, y, text, box_width, box_height, font_filename,
                       max_font_size = 60,color=(0, 0, 0), place='left',
                       justify_last_line=False, anchor="la", embedded_color=False):
        words = text.split()

        # Figure out optimal font size (TODO: OPTIMIZE)
        total_height = 999999
        font_size = max_font_size
        while total_height >= box_height:
            lines = []
            line = []
            font_size = font_size - 1
            total_height = max_height_line = 0
            for word in words:
                new_line = ' '.join(line + [word])
                size = self.get_text_size(font_filename, font_size, new_line)
                max_height_line = max(max_height_line, size[1])
                if size[0] <= box_width:
                    line.append(word)
                else:
                    lines.append(line)
                    line = [word]
                    total_height += max_height_line + 1 # Add 1 for a small margin
                    max_height_line = 0
            if line:
                lines.append(line)

        lines = [' '.join(line) for line in lines if line]
        height = y
        for index, line in enumerate(lines):
            if place == 'left':
                self.write_text(x, height, line, font_filename, font_size,
                                color, anchor=anchor, embedded_color=embedded_color)
            elif place == 'right':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = x + box_width - total_size[0]
                self.write_text(x_left, height, line, font_filename,
                                font_size, color, anchor=anchor, embedded_color=embedded_color)
            elif place == 'center':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = int(x + ((box_width - total_size[0]) / 2))
                self.write_text(x_left, height, line, font_filename,
                                font_size, color, anchor=anchor, embedded_color=embedded_color)
            elif place == 'justify':
                words = line.split()
                if (index == len(lines) - 1 and not justify_last_line) or \
                   len(words) == 1:
                    self.write_text(x, height, line, font_filename, font_size,
                                    color, anchor=anchor, embedded_color=embedded_color)
                    continue
                line_without_spaces = ''.join(words)
                total_size = self.get_text_size(font_filename, font_size,
                                                line_without_spaces)
                space_width = (box_width - total_size[0]) / (len(words) - 1.0)
                start_x = x
                for word in words[:-1]:
                    self.write_text(start_x, height, word, font_filename,
                                    font_size, color, anchor=anchor, embedded_color=embedded_color)
                    word_size = self.get_text_size(font_filename, font_size,
                                                    word)
                    start_x += word_size[0] + space_width
                last_word_size = self.get_text_size(font_filename, font_size,
                                                    words[-1])
                last_word_x = x + box_width - last_word_size[0]
                self.write_text(last_word_x, height, words[-1], font_filename,
                                font_size, color, anchor=anchor, embedded_color=embedded_color)
                                
            height += self.get_text_size(font_filename, font_size, line)[1]
        return (box_width, height - y)