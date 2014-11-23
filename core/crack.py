#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
$Id$

This file is part of the cintruder project,  http://cintruder.sourceforge.net.

Copyright (c) 2012/2015 psy <root@lordepsylon.net> - <epsylon@riseup.net>

cintruder is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

cintruder is distributed in the hope that it will be useful,  but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with cintruder; if not,  write to the Free Software Foundation,  Inc.,  51
Franklin St,  Fifth Floor,  Boston,  MA  02110-1301  USA
"""
from PIL import Image
import hashlib, os, math, time


class VectorCompare:
    def magnitude(self, concordance):
        total = 0
        for word, count in concordance.iteritems():
            # print concordance 
            total += count ** 2
        return math.sqrt(total)

    def relation(self, concordance1, concordance2):
        topvalue = 0
        for word, count in concordance1.iteritems():
            if concordance2.has_key(word):
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))


class CIntruderCrack(object):
    """
    Class to bruteforce captchas
    """

    def __init__(self, captcha=""):
        """
        Initialize main CIntruder
        """
        self.captcha = self.set_captcha(captcha)
        start = time.time()

    def buildvector(self, im):
        d1 = {}
        count = 0
        for i in im.getdata():
            d1[count] = i
            count += 1
        return d1

    def set_captcha(self, captcha):
        """
        Set the captcha.
        """
        self.captcha = captcha
        return captcha

    def crack(self, options):
        v = VectorCompare()
        iconset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                   'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        imageset = []
        last_letter = None
        print "Loading dictionary... "
        for letter in iconset:
            for img in os.listdir('iconset/%s/' % (letter)):
                temp = []
                if img != "Thumbs.db":  # win32 check
                    if options.verbose:
                        if last_letter != letter:
                            print "-----------------"
                            print "Word:", letter
                            print "-----------------"
                        print img
                        last_letter = letter
                    temp.append(self.buildvector(Image.open("iconset/%s/%s" % (letter, img))))
                imageset.append({letter: temp})

        try:
            im = Image.open(self.captcha)
            im2 = Image.new("P", im.size, 255)
            im = im.convert("P")
        except:
            print "\nError during Cracking process!. is that captcha supported?\n"
            return

        temp = {}
        for x in range(im.size[1]):
            for y in range(im.size[0]):
                pix = im.getpixel((y, x))
                temp[pix] = pix
                if pix == 3:  # pixel colour id
                    im2.putpixel((y, x), 0)

        inletter = False
        foundletter = False
        start = 0
        end = 0
        letters = []
        for y in range(im2.size[0]):  # slice across
            pixelCount = 0
            for x in range(im2.size[1]):  # slice down
                pix = im2.getpixel((y, x))
                if pix != 255:
                    print "------------------------>"
                    pixelCount += 1

            if pixelCount > 1:

                inletter = True

            if foundletter == False and inletter == True:
                foundletter = True
                start = y

            if foundletter == True and inletter == False:
                foundletter = False
                end = y
                letters.append((start, end))
            inletter = False

        count = 0
        countid = 1
        word_sug = None
        end = time.time()
        elapsed = end - start

        for letter in letters:
            m = hashlib.md5()
            print "----------------------------\n"
            im3 = im2.crop((letter[0], 0, letter[1], im2.size[1]))
            guess = []
            for image in imageset:
                for x, y in image.iteritems():
                    if len(y) != 0:
                        guess.append(( v.relation(y[0], self.buildvector(im3)), x))
            guess.sort(reverse=True)
            word_per = guess[0][0] * 100
            if str(word_per) == "100.0":
                print "Image position   :", countid
                print "Broken Percent   :", int(round(float(word_per))), "%", "[+]"
            else:
                print "Image position   :", countid
                print "Broken Percent   :", "%.4f" % word_per, "%"
            print "------------------"
            print "Word suggested   :", guess[0][1]

            if word_sug == None:
                word_sug = str(guess[0][1])
            else:
                word_sug = word_sug + str(guess[0][1])
            count += 1
            countid = countid + 1

        print "\n=================="
        if word_sug is None:
            print "Possible Solution: ", "[ No idea!. Maybe, you need to train more...]"
        else:
            print "Possible Solution: ", "[", word_sug, "]"
            if options.verbose:
                print "Elapsed OCR time :", elapsed
        print "==================\n"
        return word_sug

# if __name__ == "__main__":
#    print "===================================="
#    print "Captcha Cracked:",":-)\n"
